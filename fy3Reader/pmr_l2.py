"""FY-3G PMR L2 Reader"""

import h5py
import numpy as np
from datetime import datetime
from functools import lru_cache
from fy3Reader.resample import kdtree_interp, spline_interp, bicubic_interp

class FY3G_PMR_L2(object):

    def __init__(self, fname):
        self._datasets = h5py.File(fname, "r")
        if not self.attrs["Satellite Name"] == "FY-3G":
            raise ValueError("Satellite not matched")
        self.dataset_name = None
        self.data = self.latitude = self.longitude = None

    @staticmethod
    def _autodecode(string, encoding="gbk"):
        return string.decode(encoding) if isinstance(string, bytes) else string

    @lru_cache(maxsize=2)
    def _get_indices(self, georange):
        latmin, latmax, lonmin, lonmax = georange
        lat = self.latitude
        lon = self.longitude
        barr = (
            (lat > latmin - 0.5)
            & (lat < latmax + 0.5)
            & (lon > lonmin - 0.5)
            & (lon < lonmax + 0.5)
        )
        barrind = np.where(barr)
        barrind_y, barrind_x = barrind
        yi, yj = np.amin(barrind_y), np.amax(barrind_y)
        xi, xj = np.amin(barrind_x), np.amax(barrind_x)
        return yi, yj, xi, xj

    def all_available_datasets(self):
        return list(self._datasets["SLV"].keys())

    def load(self, name, level=0):
        if name not in self.all_available_datasets():
            raise ValueError(f"Dataset not found: {name}")
        if level not in (0, 1):
            raise ValueError(
                "Level of the geolocation should be "
                "0 (surface of the Earth's ellipsoid) "
                "or 1 (approx. 18 km above the Earth's ellipsoid)"
            )
        self.dataset_name = name
        # load lonlat & data
        self.longitude = self._datasets["Geo_Fields"]["Longitude"][:,:,level]
        self.latitude = self._datasets["Geo_Fields"]["Latitude"][:,:,level]
        self.data = self._datasets["SLV"][self.dataset_name][:]
        # mask invalid values
        self.longitude[self.longitude==-9999.9] = np.inf
        self.longitude[self.longitude==-9999.9] = np.inf
        self.data[self.data==-9999.9] = np.nan

    @property
    def attrs(self):
        return {k: self._autodecode(v) for k, v in self._datasets.attrs.items()}

    @property
    def platform_name(self):
        return self.attrs["Satellite Name"]

    @property
    def start_time(self):
        time = self.attrs['Observing Beginning Date']
        time += " " + self.attrs['Observing Beginning Time']
        try:
            return datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            return datetime.strptime(time, "%Y-%m-%d %H:%M:%S")

    @property
    def end_time(self):
        time = self.attrs['Observing Ending Date']
        time += " " + self.attrs['Observing Ending Time']
        try:
            return datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            return datetime.strptime(time, "%Y-%m-%d %H:%M:%S")

    def crop(self, ll_box):
        if self.longitude is None or self.latitude is None or self.data is None:
            raise ValueError(
                "Longitude or Latitude or data is not empty. "
                "You should run `load` first."
            )
        yi, yj, xi, xj = self._get_indices(ll_box)
        self.latitude = self.latitude[yi:yj, xi:xj]
        self.longitude = self.longitude[yi:yj, xi:xj]
        self.data = self.data[yi:yj, xi:xj]

    def resample(self, resampler='nearest', to_shape=None):
        if resampler not in ('nearest', 'spline', 'bicubic'):
            raise ValueError("Resampler only supports `nearest`, `spline` and `bicubic`.")
        if to_shape is None:
            raise ValueError("`to_shape` parameter should be provided.")
        if not len(to_shape) == 2:
            raise ValueError("`to_shape` should be a list or tuple that length is 2.")
        if resampler == 'nearest':
            self.longitude, self.latitude, self.data = kdtree_interp(
                self.longitude, self.latitude, self.data, to_shape
            )
        elif resampler == 'spline':
            self.latitude = spline_interp(self.latitude, to_shape)
            self.longitude = spline_interp(self.longitude, to_shape)
            self.data = spline_interp(self.data, to_shape)
        elif resampler == 'bicubic':
            self.latitude = bicubic_interp(self.latitude, to_shape)
            self.longitude = bicubic_interp(self.longitude, to_shape)
            self.data = bicubic_interp(self.data, to_shape)

    def get_lonlats(self):
        return self.longitude, self.latitude
    
    @property
    def values(self):
        return self.data
