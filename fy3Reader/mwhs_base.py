"""FY-3 MWHS-II L1 Reader base"""

import h5py
import numpy as np
from datetime import datetime
from functools import lru_cache
from fy3Reader.resample import (
    lonlat_interp,
    kdtree_interp,
    spline_interp,
    bicubic_interp
)

class MWHS_BASE(object):

    def __init__(self, fname):
        self._datasets = h5py.File(fname, "r")
        self.dataset_name = None
        self.data = None
        self.latitude = None
        self.longitude = None
        self.MWHS_DATASETS = None
        self.MWHS_DATASETS_EXACT = None

    @staticmethod
    def _cal_bt(dataset, intercept, slope):
        # 0 slope is invalid. Note: slope can be a scalar or array.
        slope = np.where(slope == 0, 1, slope)
        dataset = dataset * slope + intercept
        return dataset

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
        return NotImplemented

    def get_exact_dataset_name(self, dataset_name):
        return self.MWHS_DATASETS_EXACT[dataset_name]

    def load(self, name):
        return NotImplemented

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
                "Longitude or Latitude or data is empty. "
                "You should run `load` first."
            )
        yi, yj, xi, xj = self._get_indices(ll_box)
        self.latitude = self.latitude[yi:yj, xi:xj]
        self.longitude = self.longitude[yi:yj, xi:xj]
        self.data = self.data[yi:yj, xi:xj]

    def resample(self, resampler='nearest', to_shape=None, **kwargs):
        if resampler not in ('nearest', 'spline', 'bicubic'):
            raise ValueError("Resampler only supports `nearest`, `spline` and `bicubic`.")
        if to_shape is None:
            raise ValueError("`to_shape` parameter should be provided.")
        if not len(to_shape) == 2:
            raise ValueError("`to_shape` should be a list or tuple that length is 2.")
        if resampler == 'nearest':
            self.longitude, self.latitude, self.data = kdtree_interp(
                self.longitude, self.latitude, self.data, to_shape, no_xy=False
            )
        elif resampler == 'spline':
            self.longitude, self.latitude, self.data = spline_interp(
                self.longitude, self.latitude, self.data, to_shape, no_xy=False
            )
        elif resampler == 'bicubic':
            self.longitude, self.latitude, self.data = bicubic_interp(
                self.longitude, self.latitude, self.data, to_shape, no_xy=False
            )

    def get_lonlats(self):
        return self.longitude, self.latitude
    
    @property
    def values(self):
        return self.data
