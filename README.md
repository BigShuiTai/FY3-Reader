# FY3-Reader
A package includes FY-3 (FengYun-3) MWRI L1 (FY-3D/G) &amp; PMR L2 (FY-3G) reader.

## Installation
**NOTE: Following commands have only been tested on Linux System (Debian, Fedora, Ubuntu, CentOS, etc.)**

For the first time using the package, please run following commands:
```Bash
pip install Cython numpy==1.24.2 scipy==1.11.1 h5py==3.8.0 matplotlib==3.5.3 pyproj==3.5.0
python setup.py build_ext --inplace
```

## Package Usage
```Python
# Read a FY-3D MWRI L1 file
from fy3Reader.mwri_l1 import FY3D_MWRI_L1

mwri_l1 = FY3D_MWRI_L1("FY3D_MWRIA_GBAL_L1_20240530_0405_010KM_MS.HDF")
mwri_l1.load('89_color')
mwri_l1.crop((25, 35, 135, 145))
mwri_l1.resample(resampler='bicubic', to_shape=(2000, 2000))
lons, lats = mwri_l1.get_lonlats()
data_projected = mwri_l1.values
```

## Run Full Test
```Bash
cd FY3-Reader
python test.py
```

## Test Results
![89_color_nearest](89_color_nearest.png)
![89_color_bicubic](89_color_bicubic.png)
