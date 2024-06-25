"""FY-3 MWRI L1 Reader includes FY-3D & FY-3F & FY-3G"""

from fy3Reader.mwri_base import MWRI_BASE
from fy3Reader.composite import *

class FY3D_MWRI_L1(MWRI_BASE):

    def __init__(self, fname):
        super(FY3D_MWRI_L1, self).__init__(fname)
        if not self.attrs["Satellite Name"] == "FY-3D":
            raise ValueError("Satellite not matched")
        self.MWRI_DATASETS = {"S1": ["btemp_10.0v","btemp_10.0h","btemp_18.0v","btemp_18.0h","btemp_23.0v","btemp_23.0h","btemp_37.0v","btemp_37.0h","btemp_89.0v","btemp_89.0h"]}
        self.MWRI_DATASETS_EXACT = {"btemp_10.0v":"btemp_10.65v", "btemp_10.0h":"btemp_10.65h", "btemp_18.0v":"btemp_18.7v", "btemp_18.0h":"btemp_18.7h", "btemp_23.0v":"btemp_23.8v", "btemp_23.0h":"btemp_23.8h", "btemp_37.0v":"btemp_36.5v", "btemp_37.0h":"btemp_36.5h", "btemp_89.0v":"btemp_89.0v", "btemp_89.0v":"btemp_89.0h"}

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
        self.latitude = self._datasets["Geolocation"]["Latitude"][:]
        self.longitude = self._datasets["Geolocation"]["Longitude"][:]
        if self.composite_func is None:
            EOB = self._datasets["Calibration"][flag]
            self.data = self._cal_bt(
                EOB[dataset_index, ...],
                EOB.attrs["Intercept"],
                EOB.attrs["Slope"]
            )
        else:
            self.data = band_datas

class FY3F_MWRI_L1(MWRI_BASE):

    def __init__(self, fname):
        super(FY3F_MWRI_L1, self).__init__(fname)
        if not self.attrs["Satellite Name"] == "FY-3F":
            raise ValueError("Satellite not matched")
        self.MWRI_DATASETS = {"S1": ["btemp_10.0v","btemp_10.0h","btemp_18.0v","btemp_18.0h","btemp_23.0v","btemp_23.0h","btemp_37.0v","btemp_37.0h","btemp_89.0v","btemp_89.0h"], "S2": ["btemp_50.0v","btemp_50.0h","btemp_52.0v","btemp_52.0h","btemp_53.24v","btemp_53.24h","btemp_53.75v","btemp_53.75h","btemp_118.0_3v","btemp_118.0_2v","btemp_118.0_1.4v","btemp_118.0_1.2v","btemp_165.5v","btemp_183.0_2v","btemp_183.0_3v","btemp_183.0_7v"]}
        self.MWRI_DATASETS_EXACT = {"btemp_10.0v":"btemp_10.65v", "btemp_10.0h":"btemp_10.65h", "btemp_18.0v":"btemp_18.7v", "btemp_18.0h":"btemp_18.7h", "btemp_23.0v":"btemp_23.8v", "btemp_23.0h":"btemp_23.8h", "btemp_37.0v":"btemp_36.5v", "btemp_37.0h":"btemp_36.5h", "btemp_89.0v":"btemp_89.0v", "btemp_89.0v":"btemp_89.0h", "btemp_50.0v":"btemp_50.3v", "btemp_50.0h":"btemp_50.3h", "btemp_52.0v":"btemp_52.61v", "btemp_52.0h":"btemp_52.61h", "btemp_53.24v":"btemp_53.24v", "btemp_53.24h":"btemp_53.24h", "btemp_53.75v":"btemp_53.75v", "btemp_53.75h":"btemp_53.75h", "btemp_118.0_3v":"btemp_118.7503_3.2v", "btemp_118.0_2v":"btemp_118.7503_2.1v", "btemp_118.0_1.4v":"btemp_118.7503_1.4v", "btemp_118.0_1.2v":"btemp_118.7503_1.2v", "btemp_165.5v":"btemp_165.5_0.75v", "btemp_183.0_2v":"btemp_183.31_2v", "btemp_183.0_3v":"btemp_183.31_3.4v", "btemp_183.0_7v":"btemp_183.31_7v"}
        self.COMPOSITE_BANDS = {
            "89_pct": {"dataset": "Window Channel", "bands":["btemp_89.0v","btemp_89.0h"], "func": PolarizationCorrectedTemperature, "fractions":((1.7, 0.7)), "rgb": False},
            "89_color": {"dataset": "Window Channel", "bands":["btemp_89.0v","btemp_89.0h"], "func": Color_89, "fractions":((1.7, 0.7)), "rgb": True},
            "37_pct": {"dataset": "Window Channel", "bands":["btemp_37.0v","btemp_37.0h"], "func": PolarizationCorrectedTemperature, "fractions":((2.15, 1.15)), "rgb": False},
            "37_color": {"dataset": "Window Channel", "bands":["btemp_37.0v","btemp_37.0h"], "func": Color_37, "fractions":((2.15, 1.15)), "rgb": True},
        }

    def all_available_datasets(self):
        return self.MWRI_DATASETS["S1"] + self.MWRI_DATASETS["S2"]

    def load(self, name):
        if name in self.MWRI_DATASETS["S1"]:
            dataset_index = self.MWRI_DATASETS["S1"].index(name)
            dataset = self._datasets["Window Channel"]
            flag = "EARTH_OBSERVE_BT"
            self.composite_func = None
        elif name in self.MWRI_DATASETS["S2"]:
            dataset_index = self.MWRI_DATASETS["S2"].index(name)
            dataset = self._datasets["Sounding Channel"]
            flag = "EARTH_OBSERVE_BT"
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
            EOB = dataset["Calibration"][flag]
            self.data = self._cal_bt(
                EOB[..., dataset_index],
                EOB.attrs["Intercept"],
                EOB.attrs["Slope"]
            )
        else:
            self.data = band_datas

class FY3G_MWRI_L1(MWRI_BASE):

    def __init__(self, fname):
        super(FY3G_MWRI_L1, self).__init__(fname)
        if not self.attrs["Satellite Name"] == "FY-3G":
            raise ValueError("Satellite not matched")
        self.MWRI_DATASETS = {"S1": ["btemp_10.0v","btemp_10.0h","btemp_18.0v","btemp_18.0h","btemp_23.0v","btemp_23.0h","btemp_37.0v","btemp_37.0h","btemp_89.0v","btemp_89.0h"], "S2": ["btemp_50.0v","btemp_50.0h","btemp_52.0v","btemp_52.0h","btemp_53.24v","btemp_53.24h","btemp_53.75v","btemp_53.75h","btemp_118.0_3v","btemp_118.0_2v","btemp_118.0_1.4v","btemp_118.0_1.2v","btemp_165.5v","btemp_183.0_2v","btemp_183.0_3v","btemp_183.0_7v"]}
        self.MWRI_DATASETS_EXACT = {"btemp_10.0v":"btemp_10.65v", "btemp_10.0h":"btemp_10.65h", "btemp_18.0v":"btemp_18.7v", "btemp_18.0h":"btemp_18.7h", "btemp_23.0v":"btemp_23.8v", "btemp_23.0h":"btemp_23.8h", "btemp_37.0v":"btemp_36.5v", "btemp_37.0h":"btemp_36.5h", "btemp_89.0v":"btemp_89.0v", "btemp_89.0v":"btemp_89.0h", "btemp_50.0v":"btemp_50.3v", "btemp_50.0h":"btemp_50.3h", "btemp_52.0v":"btemp_52.61v", "btemp_52.0h":"btemp_52.61h", "btemp_53.24v":"btemp_53.24v", "btemp_53.24h":"btemp_53.24h", "btemp_53.75v":"btemp_53.75v", "btemp_53.75h":"btemp_53.75h", "btemp_118.0_3v":"btemp_118.7503_3.2v", "btemp_118.0_2v":"btemp_118.7503_2.1v", "btemp_118.0_1.4v":"btemp_118.7503_1.4v", "btemp_118.0_1.2v":"btemp_118.7503_1.2v", "btemp_165.5v":"btemp_165.5_0.75v", "btemp_183.0_2v":"btemp_183.31_2v", "btemp_183.0_3v":"btemp_183.31_3.4v", "btemp_183.0_7v":"btemp_183.31_7v"}

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
