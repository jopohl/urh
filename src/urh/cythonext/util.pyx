# noinspection PyUnresolvedReferences
import numpy as np

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