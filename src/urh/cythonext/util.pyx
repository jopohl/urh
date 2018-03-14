# noinspection PyUnresolvedReferences
cimport numpy as np
import numpy as np

# As we do not use any numpy C API functions we do no import_array here,
# because it can lead to OS X error: https://github.com/jopohl/urh/issues/273
# np.import_array()

cimport cython
from cython.parallel import prange
from libc.math cimport log10

cpdef tuple minmax(float[:] arr):
    cdef long long i, ns = len(arr)
    if ns == 0:
        return 0,0

    cdef float maximum = arr[0]
    cdef float minimum = arr[0]
    cdef float e

    for i in range(1, ns):
        e = arr[i]
        if e > maximum:
            maximum = e
        if e < minimum:
            minimum = e

    return minimum, maximum

cpdef np.ndarray[np.float32_t, ndim=2] arr2decibel(np.ndarray[np.complex64_t, ndim=2] arr):
    cdef long long x = arr.shape[0]
    cdef long long y  = arr.shape[1]
    cdef long long i, j = 0
    cdef np.ndarray[np.float32_t, ndim=2] result = np.empty((x,y), dtype=np.float32)
    cdef np.float32_t factor = 10.0

    for i in prange(x, nogil=True, schedule='static'):
        for j in range(y):
            result[i, j] = factor * log10(arr[i, j].real * arr[i, j].real + arr[i, j].imag * arr[i, j].imag)
    return result
