# cython: language_level=3, boundscheck=False, wraparound=False, nonecheck=False, cdivision=True, initializedcheck=False
# distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION
# Modified from https://github.com/rootpine/Bicubic-interpolation

import numpy as np
cimport numpy as np

cimport cython
from libc.math cimport floor, fabs, isnan


cdef inline Py_ssize_t clamp_ssize(Py_ssize_t v,
                                   Py_ssize_t lo,
                                   Py_ssize_t hi) nogil:
    if v < lo: return lo
    if v > hi: return hi
    return v


cdef inline double u(double t, double a) nogil:
    cdef double at = fabs(t)
    if at <= 1.0:
        return (a + 2.0)*at*at*at - (a + 3.0)*at*at + 1.0
    elif at < 2.0:
        return a*at*at*at - 5.0*a*at*at + 8.0*a*at - 4.0*a
    else:
        return 0.0


@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
def bicubic_map(double[:, ::1] img,
                double[:, ::1] I,
                double[:, ::1] J,
                double a=-0.5):
    cdef Py_ssize_t H  = img.shape[0]
    cdef Py_ssize_t W  = img.shape[1]
    cdef Py_ssize_t OH = I.shape[0]
    cdef Py_ssize_t OW = I.shape[1]

    cdef np.ndarray out_np = np.empty((OH, OW), dtype=np.float64)
    cdef double[:, ::1] out = out_np

    cdef Py_ssize_t r, c, ix, iy
    cdef Py_ssize_t xi0, xi1, xi2, xi3, yi0, yi1, yi2, yi3
    cdef double x, y, dx, dy
    cdef double wx0, wx1, wx2, wx3, wy0, wy1, wy2, wy3
    cdef double acc

    for r in range(OH):
        for c in range(OW):
            y = I[r, c]
            x = J[r, c]

            if isnan(y) or isnan(x):
                out[r, c] = np.nan
                continue

            if y < 0.0:       y = 0.0
            elif y > H - 1:   y = H - 1.0
            if x < 0.0:       x = 0.0
            elif x > W - 1:   x = W - 1.0

            iy = <Py_ssize_t>floor(y)
            ix = <Py_ssize_t>floor(x)
            dy = y - iy
            dx = x - ix

            xi0 = clamp_ssize(ix - 1, 0, W - 1)
            xi1 = ix
            xi2 = clamp_ssize(ix + 1, 0, W - 1)
            xi3 = clamp_ssize(ix + 2, 0, W - 1)

            yi0 = clamp_ssize(iy - 1, 0, H - 1)
            yi1 = iy
            yi2 = clamp_ssize(iy + 1, 0, H - 1)
            yi3 = clamp_ssize(iy + 2, 0, H - 1)

            wx0 = u(1.0 + dx, a);  wx1 = u(dx, a)
            wx2 = u(1.0 - dx, a);  wx3 = u(2.0 - dx, a)
            wy0 = u(1.0 + dy, a);  wy1 = u(dy, a)
            wy2 = u(1.0 - dy, a);  wy3 = u(2.0 - dy, a)

            acc  = (wx0*img[yi0, xi0] + wx1*img[yi0, xi1] + wx2*img[yi0, xi2] + wx3*img[yi0, xi3]) * wy0
            acc += (wx0*img[yi1, xi0] + wx1*img[yi1, xi1] + wx2*img[yi1, xi2] + wx3*img[yi1, xi3]) * wy1
            acc += (wx0*img[yi2, xi0] + wx1*img[yi2, xi1] + wx2*img[yi2, xi2] + wx3*img[yi2, xi3]) * wy2
            acc += (wx0*img[yi3, xi0] + wx1*img[yi3, xi1] + wx2*img[yi3, xi2] + wx3*img[yi3, xi3]) * wy3

            out[r, c] = acc

    return out_np
