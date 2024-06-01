from fy3Reader.mwri_l1 import *
from fy3Reader.pmr_l2 import *

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

if __name__ == "__main__":
    # test code for FY-3D & FY-3G readers
    # TEST 01: FY-3D MWRI-L1 Reader
    mwri_l1_3d = FY3D_MWRI_L1("FY3D_MWRIA_GBAL_L1_20240530_0405_010KM_MS.HDF")
    mwri_l1_3d.load('btemp_89.0h')
    print(mwri_l1_3d.attrs, mwri_l1_3d.platform_name)
    print(mwri_l1_3d.all_available_datasets())
    print(mwri_l1_3d.start_time, mwri_l1_3d.end_time)
    print(mwri_l1_3d.get_lonlats(), mwri_l1_3d.values)
    # TEST 02: FY-3G MWRI-L1 Reader
    mwri_l1_3g = FY3G_MWRI_L1("FY3G_MWRI-_ORBD_L1_20240529_0328_7000M_V1.HDF")
    mwri_l1_3g.load('btemp_89.0h')
    print(mwri_l1_3g.attrs, mwri_l1_3g.platform_name)
    print(mwri_l1_3g.all_available_datasets())
    print(mwri_l1_3g.start_time, mwri_l1_3g.end_time)
    print(mwri_l1_3g.get_lonlats(), mwri_l1_3g.values)
    # TEST 03: FY-3G PMR-L2 Reader
    pmr_l2 = FY3G_PMR_L2("FY3G_PMR--_ORBA_L2_KuR_MLT_NUL_20240528_0026_5000M_V0.HDF")
    pmr_l2.load('zFactorCorrectedESurface', level=1)
    print(pmr_l2.attrs, pmr_l2.platform_name)
    print(pmr_l2.all_available_datasets())
    print(pmr_l2.start_time, pmr_l2.end_time)
    print(pmr_l2.get_lonlats(), pmr_l2.values)
    # TEST 04: MWRI Composite
    mwri_l1 = FY3D_MWRI_L1("FY3D_MWRIA_GBAL_L1_20240530_0405_010KM_MS.HDF")
    mwri_l1.load('89_color')
    mwri_l1.crop((25, 35, 135, 145))
    mwri_l1.resample(resampler='bicubic', to_shape=(2000, 2000))
    lons, lats = mwri_l1.get_lonlats()
    projected = mwri_l1.values
    img_extent = (135, 145, 25, 35)
    data_extent = (lons.min(), lons.max(), lats.min(), lats.max())
    print(data_extent)
    # plot projected data
    f = plt.figure(figsize=(10, 10), facecolor="#000000", dpi=200)
    central_longitude = 0
    proj = ccrs.Mercator(central_longitude=central_longitude)
    ax = f.add_axes([0, 0, 1, 1], projection=proj)
    ax.set_extent(img_extent, crs=ccrs.PlateCarree())
    plt.axis("off")
    ax.imshow(projected, extent=data_extent, transform=ccrs.PlateCarree(), origin="lower")
    ax.add_feature(
        cfeature.COASTLINE.with_scale("10m"),
        facecolor="None",
        edgecolor="orange",
        lw=0.5,
    )
    ax.annotate(
        f' 2024/05/30 04:05Z FY-3D MWRI @Shuitai ',
        xy=(0.5, 0),
        va="bottom",
        ha="center",
        xycoords="axes fraction",
        bbox=dict(facecolor="w", edgecolor="none", alpha=0.7),
    )
    plt.savefig(
        "89_color_bicubic",
        bbox_inches="tight",
        pad_inches=0,
    )
    plt.close("all")
