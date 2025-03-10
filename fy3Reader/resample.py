import numpy as np
from pyproj import Proj, transform
from scipy.spatial import cKDTree
from scipy.interpolate import griddata
from scipy.ndimage import binary_dilation

try:
    from fy3Reader.bicubic_interp import bicubic
except ImportError:
    # pip install Cython
    # pkg-config --cflags numpy -> /path/to/numpy
    # export C_INCLUDE_PATH=/path/to/numpy:$C_INCLUDE_PATH
    import pyximport; pyximport.install()
    from fy3Reader.bicubic_interp import bicubic

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
    interpolated = valid_data[indices].astype(float)
    interpolated[distances > threshold] = np.nan
    if no_xy:
        return interpolated.reshape(to_shape)
    else:
        return lon_grid, lat_grid, interpolated.reshape(to_shape)

def spline_interp(x, y, arr, to_shape, no_xy=False):
    H, W = to_shape
    x, y = x.ravel(), y.ravel()
    xmin, xmax = x.min(), x.max()
    ymin, ymax = y.min(), y.max()
    newx, newy = np.meshgrid(np.linspace(xmin, xmax, W),
                             np.linspace(ymin, ymax, H))
    new_arr = griddata(np.dstack((x, y))[0], arr.ravel(), (newx, newy), method='linear')
    if no_xy:
        return new_arr
    else:
        return xn, yn, new_arr

def bicubic_interp(arr, to_shape):
    ny, nx = arr.shape
    dy, dx = to_shape
    new_arr = bicubic(arr.astype('double'), dy/ny, dx/nx, a=-0.5)
    return new_arr

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
