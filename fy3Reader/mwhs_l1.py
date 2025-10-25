"""FY-3 MWHS-II L1 Reader for FY-3D/E/F/H Satellite"""

from fy3Reader.mwhs_base import MWHS_BASE

class FY3D_MWHS_L1(MWHS_BASE):

    def __init__(self, fname):
        super(FY3D_MWHS_L1, self).__init__(fname)
        if not self.attrs["Satellite Name"] == "FY-3D":
            raise ValueError("Satellite not matched")
        self.MWHS_DATASETS = ["btemp_89h", "btemp_118.008v", "btemp_118.02v", "btemp_118.03v", "btemp_118.08v", "btemp_118.11v", "btemp_118.25v", "btemp_118.3v", "btemp_118.5v", "btemp_150h", "btemp_183.1v", "btemp_183.18v", "btemp_183.3v", "btemp_183.45v", "btemp_183.7v"]

    def all_available_datasets(self):
        return self.MWHS_DATASETS

    def load(self, name):
        if name in self.MWHS_DATASETS:
            dataset_index = self.MWHS_DATASETS.index(name)
            flag = "Earth_Obs_BT"
        else:
            raise ValueError(f"Dataset not found: {name}")
        self.dataset_name = name
        # load lonlat & data
        self.latitude = self._datasets["Geolocation"]["Latitude"][:]
        self.longitude = self._datasets["Geolocation"]["Longitude"][:]
        EOB = self._datasets["Data"][flag]
        self.data = self._cal_bt(
            EOB[dataset_index, ...],
            EOB.attrs["Intercept"],
            EOB.attrs["Slope"]
        )

class FY3E_MWHS_L1(MWHS_BASE):

    def __init__(self, fname):
        super(FY3E_MWHS_L1, self).__init__(fname)
        if not self.attrs["Satellite Name"] == "FY-3E":
            raise ValueError("Satellite not matched")
        self.MWHS_DATASETS = ["btemp_89h", "btemp_118.008v", "btemp_118.02v", "btemp_118.03v", "btemp_118.08v", "btemp_118.11v", "btemp_118.25v", "btemp_118.3v", "btemp_118.5v", "btemp_166h", "btemp_183.1v", "btemp_183.18v", "btemp_183.3v", "btemp_183.45v", "btemp_183.7v"]

    def all_available_datasets(self):
        return self.MWHS_DATASETS

    def load(self, name):
        if name in self.MWHS_DATASETS:
            dataset_index = self.MWHS_DATASETS.index(name)
            flag = "Earth_Obs_BT"
        else:
            raise ValueError(f"Dataset not found: {name}")
        self.dataset_name = name
        # load lonlat & data
        self.latitude = self._datasets["Geolocation"]["Latitude"][:]
        self.longitude = self._datasets["Geolocation"]["Longitude"][:]
        EOB = self._datasets["Data"][flag]
        self.data = self._cal_bt(
            EOB[dataset_index, ...],
            EOB.attrs["Intercept"],
            EOB.attrs["Slope"]
        )

class FY3F_MWHS_L1(MWHS_BASE):

    def __init__(self, fname):
        super(FY3F_MWHS_L1, self).__init__(fname)
        if not self.attrs["Satellite Name"] == "FY-3F":
            raise ValueError("Satellite not matched")
        self.MWHS_DATASETS = ["btemp_89h", "btemp_118.008v", "btemp_118.02v", "btemp_118.03v", "btemp_118.08v", "btemp_118.11v", "btemp_118.25v", "btemp_118.3v", "btemp_118.5v", "btemp_166h", "btemp_183.1v", "btemp_183.18v", "btemp_183.3v", "btemp_183.45v", "btemp_183.7v"]

    def all_available_datasets(self):
        return self.MWHS_DATASETS

    def load(self, name):
        if name in self.MWHS_DATASETS:
            dataset_index = self.MWHS_DATASETS.index(name)
            flag = "Earth_Obs_BT"
        else:
            raise ValueError(f"Dataset not found: {name}")
        self.dataset_name = name
        # load lonlat & data
        self.latitude = self._datasets["Geolocation"]["Latitude"][:]
        self.longitude = self._datasets["Geolocation"]["Longitude"][:]
        EOB = self._datasets["Data"][flag]
        self.data = self._cal_bt(
            EOB[dataset_index, ...],
            EOB.attrs["Intercept"],
            EOB.attrs["Slope"]
        )

class FY3H_MWHS_L1(MWHS_BASE):

    def __init__(self, fname):
        super(FY3H_MWHS_L1, self).__init__(fname)
        if not self.attrs["Satellite Name"] == "FY-3H":
            raise ValueError("Satellite not matched")
        self.MWHS_DATASETS = ["btemp_89h", "btemp_118.008v", "btemp_118.02v", "btemp_118.03v", "btemp_118.08v", "btemp_118.11v", "btemp_118.25v", "btemp_118.3v", "btemp_118.5v", "btemp_166h", "btemp_183.1v", "btemp_183.18v", "btemp_183.3v", "btemp_183.45v", "btemp_183.7v"]

    def all_available_datasets(self):
        return self.MWHS_DATASETS

    def load(self, name):
        if name in self.MWHS_DATASETS:
            dataset_index = self.MWHS_DATASETS.index(name)
            flag = "Earth_Obs_BT"
        else:
            raise ValueError(f"Dataset not found: {name}")
        self.dataset_name = name
        # load lonlat & data
        self.latitude = self._datasets["Geolocation"]["Latitude"][:]
        self.longitude = self._datasets["Geolocation"]["Longitude"][:]
        EOB = self._datasets["Data"][flag]
        self.data = self._cal_bt(
            EOB[dataset_index, ...],
            EOB.attrs["Intercept"],
            EOB.attrs["Slope"]
        )
