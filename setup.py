import os
import shutil
import numpy as np

from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("fy3Reader/bicubic_interp.pyx"),
    include_dirs=[np.get_include()]
)

# delete cache after compiled
shutil.rmtree("build")
os.remove("fy3Reader/bicubic_interp.c")
