# cython: language_level=3
# Modified from https://github.com/rootpine/Bicubic-interpolation
import numpy as np
cimport numpy as np
cimport cython

from libc.math cimport floor as _floor, abs

cdef int floor(double val):
    return <int>_floor(val)

# Interpolation kernel
cdef double u(double s, double a):
    s_abs = abs(s)
    if (s_abs >= 0) & (s_abs <= 1):
        return (a + 2) * (s_abs ** 3) - (a + 3) * (s_abs ** 2) + 1
    elif (s_abs > 1) & (s_abs <= 2):
        return a * (s_abs ** 3) - (5 * a) * (s_abs ** 2) + (8 * a) * s_abs - 4 * a
    return 0

# Padding
@cython.boundscheck(False)
cdef double[:, :] padding(double [:, :] img, int H, int W):
    cdef double[:, :] zimg = np.zeros((H + 4, W + 4))
    zimg[2 : H + 2, 2 : W + 2] = img
    # Pad the first/last two col and row
    zimg[2 : H + 2, 0:2] = img[:, 0:1]
    zimg[H + 2 : H + 4, 2 : W + 2] = img[H - 1 : H, :]
    zimg[2 : H + 2, W + 2 : W + 4] = img[:, W - 1 : W]
    zimg[0:2, 2 : W + 2,] = img[0:1, :]
    # Pad the missing eight points
    zimg[0:2, 0:2] = img[0, 0]
    zimg[H + 2 : H + 4, 0:2] = img[H - 1, 0]
    zimg[H + 2 : H + 4, W + 2 : W + 4] = img[H - 1, W - 1]
    zimg[0:2, W + 2 : W + 4] = img[0, W - 1]
    return zimg

# Bicubic operation
@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
def bicubic(double[:, :] img, double h_ratio, double w_ratio, double a):
    cdef int H, W, inc, dH, dW
    cdef double[:, :] dst
    cdef int c_H, c_W
    cdef double[:] mat_l = np.zeros(4)
    cdef double[:] mat_r = np.zeros(4)
    cdef double[:, :] mat_m = np.zeros((4, 4))
    cdef double[:] mat_lm = np.zeros(4)
    # Get image size
    H, W = img.shape[0], img.shape[1]

    img = padding(img, H, W)
    # Create new image
    dH = floor(H * h_ratio)
    dW = floor(W * w_ratio)
    dst = np.zeros((dH, dW))

    c_H =  0
    while c_H < dH:
        c_W = 0
        while c_W < dW:
            x = c_W / w_ratio + 2
            y = c_H / h_ratio + 2

            x1 = 1 + x - floor(x)
            x2 = x - floor(x)
            x3 = floor(x) + 1 - x
            x4 = floor(x) + 2 - x

            y1 = 1 + y - floor(y)
            y2 = y - floor(y)
            y3 = floor(y) + 1 - y
            y4 = floor(y) + 2 - y

            mat_l[0] = u(x1, a)
            mat_l[1] = u(x2, a)
            mat_l[2] = u(x3, a)
            mat_l[3] = u(x4, a)
            mat_m[0, 0] = img[int(y - y1), int(x - x1)]
            mat_m[0, 1] = img[int(y - y2), int(x - x1)]
            mat_m[0, 2] = img[int(y + y3), int(x - x1)]
            mat_m[0, 3] = img[int(y + y4), int(x - x1)]
            mat_m[1, 0] = img[int(y - y1), int(x - x2)]
            mat_m[1, 1] = img[int(y - y2), int(x - x2)]
            mat_m[1, 2] = img[int(y + y3), int(x - x2)]
            mat_m[1, 3] = img[int(y + y4), int(x - x2)]
            mat_m[2, 0] = img[int(y - y1), int(x + x3)]
            mat_m[2, 1] = img[int(y - y2), int(x + x3)]
            mat_m[2, 2] = img[int(y + y3), int(x + x3)]
            mat_m[2, 3] = img[int(y + y4), int(x + x3)]
            mat_m[3, 0] = img[int(y - y1), int(x + x4)]
            mat_m[3, 1] = img[int(y - y2), int(x + x4)]
            mat_m[3, 2] = img[int(y + y3), int(x + x4)]
            mat_m[3, 3] = img[int(y + y4), int(x + x4)]
            mat_r[0] = u(y1, a)
            mat_r[1] = u(y2, a)
            mat_r[2] = u(y3, a)
            mat_r[3] = u(y4, a)
            # dot(mat_l, mat_m)
            mat_lm[0] = mat_l[0] * mat_m[0, 0] + mat_l[1] * mat_m[1, 0] + mat_l[2] * mat_m[2, 0] + mat_l[3] * mat_m[3, 0]
            mat_lm[1] = mat_l[0] * mat_m[0, 1] + mat_l[1] * mat_m[1, 1] + mat_l[2] * mat_m[2, 1] + mat_l[3] * mat_m[3, 1]
            mat_lm[2] = mat_l[0] * mat_m[0, 2] + mat_l[1] * mat_m[1, 2] + mat_l[2] * mat_m[2, 2] + mat_l[3] * mat_m[3, 2]
            mat_lm[3] = mat_l[0] * mat_m[0, 3] + mat_l[1] * mat_m[1, 3] + mat_l[2] * mat_m[2, 3] + mat_l[3] * mat_m[3, 3]
            # dot(mat_lm, mat_r)
            dst[c_H, c_W] = mat_lm[0] * mat_r[0] + mat_lm[1] * mat_r[1] + mat_lm[2] * mat_r[2] + mat_lm[3] * mat_r[3]
            c_W += 1
        c_H += 1
    return np.asarray(dst)
