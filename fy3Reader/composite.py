"""FY-3 MWRI Composite Bands"""

import numpy as np
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

class PolarizationCorrectedTemperature(object):

    def __init__(self, datas, fractions=(1.7, 0.7)):
        self.v, self.h = datas
        self.fractions = fractions

    def composite(self):
        """Generate the PCT composite."""
        return self.v * self.fractions[0] - self.h * self.fractions[1]

class Color_89(object):

    def __init__(self, datas, fractions=(1.7, 0.7)):
        self.v, self.h = datas
        self.PCT = PolarizationCorrectedTemperature(datas, fractions=fractions)
        self.composite_name = '89_color'
        self.colormaps = {
            "89_pct": ScalarMappable(norm=Normalize(vmin=212, vmax=295, clip=True), cmap="gray_r"),
            "89_h": ScalarMappable(norm=Normalize(vmin=245, vmax=305, clip=True), cmap="gray"),
            "89_v": ScalarMappable(norm=Normalize(vmin=255, vmax=310, clip=True), cmap="gray"),
        }

    def composite(self):
        """Generate the 89_color composite."""
        self.pct = self.PCT.composite()
        self.pct = self.colormaps["89_pct"].to_rgba(self.pct, bytes=True)[..., 0]
        self.h = self.colormaps["89_h"].to_rgba(self.h, bytes=True)[..., 0]
        self.v = self.colormaps["89_v"].to_rgba(self.v, bytes=True)[..., 0]
        return np.stack([self.pct, self.h, self.v], axis=-1)

class Color_37(object):

    def __init__(self, datas, fractions=(2.15, 1.15)):
        self.v, self.h = datas
        self.PCT = PolarizationCorrectedTemperature(datas, fractions=fractions)
        self.composite_name = '37_color'
        self.colormaps = {
            "37_pct": ScalarMappable(norm=Normalize(vmin=260, vmax=280, clip=True), cmap="gray_r"),
            "37_h": ScalarMappable(norm=Normalize(vmin=195, vmax=280, clip=True), cmap="gray"),
            "37_v": ScalarMappable(norm=Normalize(vmin=170, vmax=280, clip=True), cmap="gray"),
        }

    def composite(self):
        """Generate the 37_color composite."""
        self.pct = self.PCT.composite()
        self.pct = self.colormaps["37_pct"].to_rgba(self.pct, bytes=True)[..., 0]
        self.v = self.colormaps["37_h"].to_rgba(self.v, bytes=True)[..., 0]
        self.h = self.colormaps["37_v"].to_rgba(self.h, bytes=True)[..., 0]
        return np.stack([self.pct, self.v, self.h], axis=-1)
