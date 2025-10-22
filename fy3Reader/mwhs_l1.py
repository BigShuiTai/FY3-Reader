"""FY-3 MWHS-II L1 Reader for FY-3D/E/F/H Satellite"""

from fy3Reader.mwhs_base import MWHS_BASE

class FY3D_MWHS_L1(MWHS_BASE):

    def __init__(self, fname):
        super(FY3D_MWHS_L1, self).__init__(fname)
        if not self.attrs["Satellite Name"] == "FY-3D":
            raise ValueError("Satellite not matched")
        self.MWHS_DATASETS = ["btemp_89h", "btemp_118_0.08v", "btemp_118_0.2v", "btemp_118_0.3v", "btemp_118_0.8v", "btemp_118_1.1v", "btemp_118_2.5v", "btemp_118_3.0v", "btemp_118_5.0v", "btemp_150h", "btemp_183_1.0v", "btemp_183_1.8v", "btemp_183_3.0v", "btemp_183_4.5v", "btemp_183_7.0v"]

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
        self.MWHS_DATASETS = ["btemp_89h", "btemp_118_0.08v", "btemp_118_0.2v", "btemp_118_0.3v", "btemp_118_0.8v", "btemp_118_1.1v", "btemp_118_2.5v", "btemp_118_3.0v", "btemp_118_5.0v", "btemp_166h", "btemp_183_1.0v", "btemp_183_1.8v", "btemp_183_3.0v", "btemp_183_4.5v", "btemp_183_7.0v"]

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
        self.MWHS_DATASETS = ["btemp_89h", "btemp_118_0.08v", "btemp_118_0.2v", "btemp_118_0.3v", "btemp_118_0.8v", "btemp_118_1.1v", "btemp_118_2.5v", "btemp_118_3.0v", "btemp_118_5.0v", "btemp_166h", "btemp_183_1.0v", "btemp_183_1.8v", "btemp_183_3.0v", "btemp_183_4.5v", "btemp_183_7.0v"]

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
        self.MWHS_DATASETS = ["btemp_89h", "btemp_118_0.08v", "btemp_118_0.2v", "btemp_118_0.3v", "btemp_118_0.8v", "btemp_118_1.1v", "btemp_118_2.5v", "btemp_118_3.0v", "btemp_118_5.0v", "btemp_166h", "btemp_183_1.0v", "btemp_183_1.8v", "btemp_183_3.0v", "btemp_183_4.5v", "btemp_183_7.0v"]

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
