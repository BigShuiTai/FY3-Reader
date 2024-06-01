"""FY-3 MWRI L1 Reader includes FY-3D & FY-3G"""

import h5py
import numpy as np
from datetime import datetime
from functools import lru_cache
from fy3Reader.resample import kdtree_interp, spline_interp, bicubic_interp, rgb_project
from fy3Reader.composite import PolarizationCorrectedTemperature, Color_89, Color_37

class FY3D_MWRI_L1(object):

    def __init__(self, fname):
        self.datasets = h5py.File(fname, "r")
        if not self.attrs["Satellite Name"] == "FY-3D":
            raise ValueError("Satellite not matched")
        self.dataset_name = None
        self.composite_func = None
        self.data = self.latitude = self.longitude = None
        self.MWRI_DATASETS = {"S1": ["btemp_10.0v","btemp_10.0h","btemp_18.0v","btemp_18.0h","btemp_23.0v","btemp_23.0h","btemp_37.0v","btemp_37.0h","btemp_89.0v","btemp_89.0h"]}
        self.COMPOSITE_BANDS = {
            "89_pct": {"dataset": "S1", "bands":["btemp_89.0v","btemp_89.0h"], "func": PolarizationCorrectedTemperature, "fractions":((1.7, 0.7))},
            "89_color": {"dataset": "S1", "bands":["btemp_89.0v","btemp_89.0h"], "func": Color_89, "fractions":((1.7, 0.7))},
            "37_pct": {"dataset": "S1", "bands":["btemp_37.0v","btemp_37.0h"], "func": PolarizationCorrectedTemperature, "fractions":((2.15, 1.15))},
            "37_color": {"dataset": "S1", "bands":["btemp_37.0v","btemp_37.0h"], "func": Color_37, "fractions":((2.15, 1.15))},
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
        return self.MWRI_DATASETS["S1"]

    def load(self, name):
        if name in self.MWRI_DATASETS["S1"]:
            dataset_index = self.MWRI_DATASETS["S1"].index(name)
            flag = "EARTH_OBSERVE_BT_10_to_89GHz"
            self.composite_func = None
        elif name in self.COMPOSITE_BANDS:
            band_datas = []
            for band in self.COMPOSITE_BANDS[name]["bands"]:
                self.load(band)
                band_datas.append(self.data)
            self.composite_func = self.COMPOSITE_BANDS[name]["func"]
        else:
            raise ValueError(f"Dataset not found: {name}")
        self.dataset_name = name
        # load lonlat & data
        self.latitude = self.datasets["Geolocation"]["Latitude"][:]
        self.longitude = self.datasets["Geolocation"]["Longitude"][:]
        if self.composite_func is None:
            EOB = self.datasets["Calibration"][flag]
            self.data = self._cal_bt(
                EOB[dataset_index, ...],
                EOB.attrs["Intercept"],
                EOB.attrs["Slope"]
            )
        else:
            self.data = band_datas

    @property
    def attrs(self):
        return {k: self._autodecode(v) for k, v in self.datasets.attrs.items()}

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
                self.latitude = kdtree_interp(self.latitude, to_shape)
                self.longitude = kdtree_interp(self.longitude, to_shape)
                self.data = kdtree_interp(self.data, to_shape)
            elif resampler == 'spline':
                self.latitude = spline_interp(self.latitude, to_shape)
                self.longitude = spline_interp(self.longitude, to_shape)
                self.data = spline_interp(self.data, to_shape)
            elif resampler == 'bicubic':
                self.latitude = bicubic_interp(self.latitude, to_shape)
                self.longitude = bicubic_interp(self.longitude, to_shape)
                self.data = bicubic_interp(self.data, to_shape)
        else:
            # start interploation
            if resampler == 'nearest':
                # need higher precision lonlat to avoid strips
                interp_lonlat = spline_interp
                interp_data = kdtree_interp
            elif resampler == 'spline':
                interp_lonlat = interp_data = spline_interp
            elif resampler == 'bicubic':
                interp_lonlat = interp_data = bicubic_interp
            self.latitude = interp_lonlat(self.latitude, to_shape)
            self.longitude = interp_lonlat(self.longitude, to_shape)
            for idx, d in enumerate(self.data):
                self.data[idx] = interp_data(d, to_shape)
            # make data projected
            cm = self.composite_func(self.data, fractions=self.COMPOSITE_BANDS[self.dataset_name]["fractions"])
            self.data = rgb_project(self.longitude, self.latitude, cm.composite(), **kwargs)
            self.composite_func = None

    def get_lonlats(self):
        return self.longitude, self.latitude
    
    @property
    def values(self):
        return self.data

class FY3G_MWRI_L1(object):

    def __init__(self, fname):
        self._datasets = h5py.File(fname, "r")
        if not self.attrs["Satellite Name"] == "FY-3G":
            raise ValueError("Satellite not matched")
        self.dataset_name = None
        self.composite_func = None
        self.data = self.latitude = self.longitude = None
        self.MWRI_DATASETS = {"S1": ["btemp_10.0v","btemp_10.0h","btemp_18.0v","btemp_18.0h","btemp_23.0v","btemp_23.0h","btemp_37.0v","btemp_37.0h","btemp_89.0v","btemp_89.0h"], "S2": ["btemp_50v","btemp_50.0h","btemp_52.0v","btemp_52.0h","btemp_53.24v","btemp_53.24h","btemp_53.75v","btemp_53.75h","btemp_118.0v","btemp_165.0v","btemp_183.0v"]}
        self.COMPOSITE_BANDS = {
            "89_pct": {"dataset": "S1", "bands":["btemp_89.0v","btemp_89.0h"], "func": PolarizationCorrectedTemperature, "fractions":((1.7, 0.7))},
            "89_color": {"dataset": "S1", "bands":["btemp_89.0v","btemp_89.0h"], "func": Color_89, "fractions":((1.7, 0.7))},
            "37_pct": {"dataset": "S1", "bands":["btemp_37.0v","btemp_37.0h"], "func": PolarizationCorrectedTemperature, "fractions":((2.15, 1.15))},
            "37_color": {"dataset": "S1", "bands":["btemp_37.0v","btemp_37.0h"], "func": Color_37, "fractions":((2.15, 1.15))},
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
        return self.MWRI_DATASETS["S1"] + self.MWRI_DATASETS["S2"]

    def load(self, name):
        if name in self.MWRI_DATASETS["S1"]:
            dataset_index = self.MWRI_DATASETS["S1"].index(name)
            dataset = self._datasets["S1"]
            flag = "EARTH_OBSERVE_BT_10_to_89GHz"
            self.composite_func = None
        elif name in self.MWRI_DATASETS["S2"]:
            dataset_index = self.MWRI_DATASETS["S2"].index(name)
            dataset = self._datasets["S2"]
            flag = "EARTH_OBSERVE_BT_50_to_183GHz"
            self.composite_func = None
        elif name in self.COMPOSITE_BANDS:
            band_datas = []
            for band in self.COMPOSITE_BANDS[name]["bands"]:
                self.load(band)
                band_datas.append(self.data)
            dataset = self._datasets[self.COMPOSITE_BANDS[name]["dataset"]]
            self.composite_func = self.COMPOSITE_BANDS[name]["func"]
        else:
            raise ValueError(f"Dataset not found: {name}")
        self.dataset_name = name
        # load lonlat & data
        self.latitude = dataset["Geolocation"]["Latitude"][:]
        self.longitude = dataset["Geolocation"]["Longitude"][:]
        if self.composite_func is None:
            EOB = dataset["Data"][flag]
            self.data = self._cal_bt(
                EOB[..., dataset_index],
                EOB.attrs["Intercept"],
                EOB.attrs["Slope"]
            )
        else:
            self.data = band_datas

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
                self.latitude = kdtree_interp(self.latitude, to_shape)
                self.longitude = kdtree_interp(self.longitude, to_shape)
                self.data = kdtree_interp(self.data, to_shape)
            elif resampler == 'spline':
                self.latitude = spline_interp(self.latitude, to_shape)
                self.longitude = spline_interp(self.longitude, to_shape)
                self.data = spline_interp(self.data, to_shape)
            elif resampler == 'bicubic':
                self.latitude = bicubic_interp(self.latitude, to_shape)
                self.longitude = bicubic_interp(self.longitude, to_shape)
                self.data = bicubic_interp(self.data, to_shape)
        else:
            # start interploation
            if resampler == 'nearest':
                # need higher precision lonlat to avoid strips
                interp_lonlat = spline_interp
                interp_data = kdtree_interp
            elif resampler == 'spline':
                interp_lonlat = interp_data = spline_interp
            elif resampler == 'bicubic':
                interp_lonlat = interp_data = bicubic_interp
            self.latitude = interp_lonlat(self.latitude, to_shape)
            self.longitude = interp_lonlat(self.longitude, to_shape)
            for idx, d in enumerate(self.data):
                self.data[idx] = interp_data(d, to_shape)
            # make data projected
            cm = self.composite_func(self.data, fractions=self.COMPOSITE_BANDS[self.dataset_name]["fractions"])
            self.data = rgb_project(self.longitude, self.latitude, cm.composite(), **kwargs)
            self.composite_func = None

    def get_lonlats(self):
        return self.longitude, self.latitude
    
    @property
    def values(self):
        return self.data
