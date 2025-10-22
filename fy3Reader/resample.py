import numpy as np
from pyproj import Proj, transform
from scipy.spatial import cKDTree
from scipy.interpolate import griddata
from scipy.interpolate import CloughTocher2DInterpolator
from scipy.ndimage import map_coordinates
from scipy.ndimage import binary_dilation

try:
    from fy3Reader.bicubic_interp import bicubic_map
    _HAS_CY_BICUBIC_MAP = True
except ImportError:
    _HAS_CY_BICUBIC_MAP = False

def lonlat_interp(x, y, to_shape):
    H, W = to_shape
    xs, ys = x.ravel(), y.ravel()
    xmin, xmax = xs.min(), xs.max()
    ymin, ymax = ys.min(), ys.max()
    xn, yn = np.meshgrid(np.linspace(xmin, xmax, W),
                         np.linspace(ymin, ymax, H))
    return xn, yn

def kdtree_interp(x, y, arr, to_shape, threshold_mult=2, no_xy=False):
    mask = ~np.isnan(arr)
    valid_lon = x[mask].ravel()
    valid_lat = y[mask].ravel()
    valid_data = arr[mask].ravel()
    if len(valid_data) == 0:
        return np.full(to_shape, np.nan)
    tree = cKDTree(np.column_stack((valid_lon, valid_lat)))
    nn_distances, _ = tree.query(tree.data, k=2)
    max_nn_distance = np.max(nn_distances[:, 1])
    threshold = max_nn_distance * threshold_mult
    lon_grid, lat_grid = lonlat_interp(x, y, to_shape)
    target_points = np.column_stack((lon_grid.ravel(), lat_grid.ravel()))
    distances, indices = tree.query(target_points, k=1)
    new_arr = valid_data[indices].astype(float)
    new_arr[distances > threshold] = np.nan
    new_arr = new_arr.reshape(to_shape)
    return new_arr if no_xy else (lon_grid, lat_grid, new_arr)

def spline_interp(x, y, arr, to_shape, no_xy=False):
    H, W = to_shape
    x, y = x.ravel(), y.ravel()
    xmin, xmax = x.min(), x.max()
    ymin, ymax = y.min(), y.max()
    newx, newy = np.meshgrid(np.linspace(xmin, xmax, W),
                             np.linspace(ymin, ymax, H))
    new_arr = griddata(np.dstack((x, y))[0], arr.ravel(), (newx, newy), method='linear')
    return new_arr if no_xy else (xn, yn, new_arr)

def _build_index_interpolators(lon, lat):
    H, W = lon.shape
    I, J = np.indices((H, W))
    m = ~(np.isnan(lon) | np.isnan(lat))
    pts = np.column_stack([lon[m].ravel(), lat[m].ravel()])
    ival = I[m].ravel().astype(float)
    jval = J[m].ravel().astype(float)
    Itp = CloughTocher2DInterpolator(pts, ival, fill_value=np.nan)
    Jtp = CloughTocher2DInterpolator(pts, jval, fill_value=np.nan)
    return Itp, Jtp

def bicubic_interp(x, y, arr, to_shape, a=-0.5, threshold_mult=2.0, no_xy=False):
    lon_grid, lat_grid = lonlat_interp(x, y, to_shape)
    Itp, Jtp = _build_index_interpolators(x, y)
    Igrid = Itp(lon_grid, lat_grid)
    Jgrid = Jtp(lon_grid, lat_grid)
    if _HAS_CY_BICUBIC_MAP:
        out = bicubic_map(arr.astype('double'), Igrid.astype('double'), Jgrid.astype('double'), a=a)
    else:
        out = map_coordinates(arr, [Igrid, Jgrid], order=3, mode='nearest', cval=np.nan)
    return out if no_xy else (lon_grid, lat_grid, out)

def rgb_project(lons, lats, data, **kwargs):
    if not len(data.shape) == 3:
        raise ValueError("`data` must be a 3-dimensional array")
    proj_latlon = Proj(proj='latlong', datum='WGS84')
    proj_dst = Proj(proj='eqc', datum='WGS84', **kwargs)
    x, y = transform(proj_latlon, proj_dst, lons, lats)
    # Normalize coordinates to the image size
    min_x, min_y = x.min(), y.min()
    max_x, max_y = x.max(), y.max()
    normalized_x = ((x - min_x) / (max_x - min_x) * (data.shape[1] - 1)).astype(int)
    normalized_y = ((y - min_y) / (max_y - min_y) * (data.shape[0] - 1)).astype(int)
    # Create new image with transformed coordinates
    projected = np.zeros_like(data)
    projected[normalized_y, normalized_x] = data
    # Find the mask of the empty (zero) pixels
    mask = (projected == 0).all(axis=2)
    # Create mask for valid data points
    valid_points_mask = np.zeros_like(mask, dtype=bool)
    valid_points_mask[normalized_y, normalized_x] = True
    # Exclude edges from interpolation by dilating the edge mask
    edge_mask = binary_dilation(valid_points_mask, iterations=2) & ~valid_points_mask
    # Only interpolate internal pixels (excluding edges)
    internal_mask = mask & edge_mask
    # Perform interpolation only on internal mask
    coords = np.array(np.nonzero(valid_points_mask)).T  # Non-zero coordinates
    tree = cKDTree(coords)
    missing_coords = np.array(np.nonzero(internal_mask)).T
    distances, indices = tree.query(missing_coords, k=1)
    projected[internal_mask] = projected[tuple(coords[indices].T)]
    return projected
