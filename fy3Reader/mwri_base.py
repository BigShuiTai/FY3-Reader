"""FY-3 MWRI L1 Reader base"""

import h5py
import numpy as np
from datetime import datetime
from functools import lru_cache
from fy3Reader.resample import (
    lonlat_interp,
    kdtree_interp,
    spline_interp,
    bicubic_interp,
    rgb_project
)
from fy3Reader.composite import *

class MWRI_BASE(object):

    def __init__(self, fname):
        self._datasets = h5py.File(fname, "r")
        self.dataset_name = None
        self.composite_func = None
        self.data = None
        self.latitude = None
        self.longitude = None
        self.MWRI_DATASETS = None
        self.MWRI_DATASETS_EXACT = None
        self.COMPOSITE_BANDS = {
            "89_pct": {"dataset": "S1", "bands":["btemp_89.0v","btemp_89.0h"], "func": PolarizationCorrectedTemperature, "fractions":((1.7, 0.7)), "rgb": False},
            "89_color": {"dataset": "S1", "bands":["btemp_89.0v","btemp_89.0h"], "func": Color_89, "fractions":((1.7, 0.7)), "rgb": True},
            "37_pct": {"dataset": "S1", "bands":["btemp_37.0v","btemp_37.0h"], "func": PolarizationCorrectedTemperature, "fractions":((2.15, 1.15)), "rgb": False},
            "37_color": {"dataset": "S1", "bands":["btemp_37.0v","btemp_37.0h"], "func": Color_37, "fractions":((2.15, 1.15)), "rgb": True},
        }

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
        return self.MWRI_DATASETS_EXACT[dataset_name]

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
                "Longitude or Latitude or data is not empty. "
                "You should run `load` first."
            )
        yi, yj, xi, xj = self._get_indices(ll_box)
        self.latitude = self.latitude[yi:yj, xi:xj]
        self.longitude = self.longitude[yi:yj, xi:xj]
        if self.composite_func is None:
            self.data = self.data[yi:yj, xi:xj]
        else:
            for idx, d in enumerate(self.data):
                self.data[idx] = d[yi:yj, xi:xj]

    def resample(self, resampler='nearest', to_shape=None, **kwargs):
        if resampler not in ('nearest', 'spline', 'bicubic'):
            raise ValueError("Resampler only supports `nearest`, `spline` and `bicubic`.")
        if to_shape is None:
            raise ValueError("`to_shape` parameter should be provided.")
        if not len(to_shape) == 2:
            raise ValueError("`to_shape` should be a list or tuple that length is 2.")
        if self.composite_func is None:
            if self.dataset_name in self.COMPOSITE_BANDS:
                return
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
        else:
            # start interploation
            if resampler == 'nearest':
                # need higher precision lonlat to avoid strips
                interp_lonlat = lonlat_interp
                interp_data = kdtree_interp
            elif resampler == 'spline':
                interp_lonlat = lonlat_interp
                interp_data = spline_interp
            elif resampler == 'bicubic':
                interp_lonlat = lonlat_interp
                interp_data = bicubic_interp
            for idx, d in enumerate(self.data):
                self.data[idx] = interp_data(self.longitude, self.latitude, d, to_shape, no_xy=True)
            self.longitude, self.latitude = interp_lonlat(self.longitude, self.latitude, to_shape)
            # make data projected
            cm = self.composite_func(self.data, fractions=self.COMPOSITE_BANDS[self.dataset_name]["fractions"])
            if self.COMPOSITE_BANDS[self.dataset_name]["rgb"]:
                self.data = rgb_project(self.longitude, self.latitude, cm.composite(), **kwargs)
            else:
                self.data = cm.composite()
            self.composite_func = None

    def get_lonlats(self):
        return self.longitude, self.latitude
    
    @property
    def values(self):
        return self.data
