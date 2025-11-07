"""FY-3 MWRI/MWHS Composite Bands"""

import numpy as np
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

class PolarizationDifference(object):

    def __init__(self, datas, fractions=(1.0, 1.0)):
        self.v, self.h = datas
        self.fractions = fractions

    def composite(self):
        """Generate the Polarization Difference composite."""
        return self.v * self.fractions[0] - self.h * self.fractions[1]

class PolarizationCorrectedTemperature(object):

    def __init__(self, datas, fractions=(1.7, 0.7)):
        self.v, self.h = datas
        self.fractions = fractions

    def composite(self):
        """Generate the Polarization Corrected Temperature composite."""
        return self.v * self.fractions[0] - self.h * self.fractions[1]

class Color_89(object):

    def __init__(self, datas, fractions=(1.7, 0.7)):
        self.v_89, self.h_89 = datas
        self.PCT_89 = PolarizationCorrectedTemperature((self.v_89, self.h_89), fractions=fractions)
        self.composite_name = '89_color'
        self.colormaps = {
            "r_89_pct": ScalarMappable(norm=Normalize(vmin=212, vmax=295, clip=True), cmap="gray_r"),
            "g_89_h": ScalarMappable(norm=Normalize(vmin=245, vmax=305, clip=True), cmap="gray"),
            "b_89_v": ScalarMappable(norm=Normalize(vmin=255, vmax=310, clip=True), cmap="gray"),
        }

    def composite(self):
        """Generate the 89_color composite."""
        self.pct_89 = self.PCT_89.composite()
        self.r = self.colormaps["r_89_pct"].to_rgba(self.pct_89, bytes=True)[..., 0]
        self.g = self.colormaps["g_89_h"].to_rgba(self.h_89, bytes=True)[..., 0]
        self.b = self.colormaps["b_89_v"].to_rgba(self.v_89, bytes=True)[..., 0]
        return np.stack([self.r, self.g, self.b], axis=-1)

class Color_37(object):

    def __init__(self, datas, fractions=(2.15, 1.15)):
        self.v_37, self.h_37 = datas
        self.PCT_37 = PolarizationCorrectedTemperature((self.v_37, self.h_37), fractions=fractions)
        self.composite_name = '37_color'
        self.colormaps = {
            "r_37_pct": ScalarMappable(norm=Normalize(vmin=260, vmax=280, clip=True), cmap="gray_r"),
            "g_37_h": ScalarMappable(norm=Normalize(vmin=195, vmax=280, clip=True), cmap="gray"),
            "b_37_v": ScalarMappable(norm=Normalize(vmin=170, vmax=280, clip=True), cmap="gray"),
        }

    def composite(self):
        """Generate the 37_color composite."""
        self.pct_37 = self.PCT_37.composite()
        self.r = self.colormaps["r_37_pct"].to_rgba(self.pct_37, bytes=True)[..., 0]
        self.g = self.colormaps["g_37_h"].to_rgba(self.v_37, bytes=True)[..., 0]
        self.b = self.colormaps["b_37_v"].to_rgba(self.h_37, bytes=True)[..., 0]
        return np.stack([self.r, self.g, self.b], axis=-1)

class HydrometeorType(object):

    def __init__(self, datas, fractions=((1.0, 1.0), (1.7, 0.7))):
        self.v_19, self.h_19, self.v_89, self.h_89 = datas
        self.PD_19 = PolarizationDifference((self.v_19, self.h_19), fractions=fractions[0])
        self.PCT_89 = PolarizationCorrectedTemperature((self.v_89, self.h_89), fractions=fractions[1])
        self.composite_name = 'hydrometeor_type'
        self.colormaps = {
            "r_89_pct": ScalarMappable(norm=Normalize(vmin=205, vmax=290, clip=True), cmap="gray_r"),
            "g_19_pd": ScalarMappable(norm=Normalize(vmin=0, vmax=65, clip=True), cmap="gray_r"),
            "b_89_h": ScalarMappable(norm=Normalize(vmin=240, vmax=305, clip=True), cmap="gray"),
        }

    def composite(self):
        """Generate the hydrometeor_type composite."""
        self.pct_89 = self.PCT_89.composite()
        self.pd_19 = self.PD_19.composite()
        self.r = self.colormaps["r_89_pct"].to_rgba(self.pct_89, bytes=True)[..., 0]
        self.g = self.colormaps["g_19_pd"].to_rgba(self.pd_19, bytes=True)[..., 0]
        self.b = self.colormaps["b_89_h"].to_rgba(self.h_89, bytes=True)[..., 0]
        return np.stack([self.r, self.g, self.b], axis=-1)

class Color_89_MWHS(object):

    def __init__(self, datas, fractions=None):
        self.h_89, self.h_166 = datas
        self.composite_name = '89_color_mwhs'
        self.colormaps = {
            "r_166_h": ScalarMappable(norm=Normalize(vmin=120, vmax=305, clip=True), cmap="gray_r"),
            "g_89_h": ScalarMappable(norm=Normalize(vmin=245, vmax=305, clip=True), cmap="gray"),
            "b_89_h": ScalarMappable(norm=Normalize(vmin=245, vmax=305, clip=True), cmap="gray"),
        }

    def composite(self):
        """Generate the 89_color_mwhs composite."""
        self.r = self.colormaps["r_166_h"].to_rgba(self.h_166, bytes=True)[..., 0]
        self.g = self.colormaps["g_89_h"].to_rgba(self.h_89, bytes=True)[..., 0]
        self.b = self.colormaps["b_89_h"].to_rgba(self.h_89, bytes=True)[..., 0]
        return np.stack([self.r, self.g, self.b], axis=-1)
