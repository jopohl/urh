# noinspection PyUnresolvedReferences
cimport numpy as np
import numpy as np

# As we do not use any numpy C API functions we do no import_array here,
# because it can lead to OS X error: https://github.com/jopohl/urh/issues/273
# np.import_array()

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


cpdef np.ndarray[np.int8_t, ndim=3] build_xor_matrix(list bitvectors):
    cdef int maximum = 0
    cdef np.int8_t[:] bitvector_i, bitvector_j
    cdef int i, j, l
    for i in range(0, len(bitvectors)):
        bitvector_i = bitvectors[i]
        if maximum < len(bitvector_i):
            maximum = len(bitvector_i)

    cdef np.ndarray[np.int8_t, ndim=3] result = np.full((len(bitvectors), len(bitvectors), maximum), -1, dtype=np.int8, order="C")

    for i in range(len(bitvectors)):
        bitvector_i = bitvectors[i]
        for j in range(i+1, len(bitvectors)):
            bitvector_j = bitvectors[j]
            l = min(len(bitvector_i), len(bitvector_j))
            for k in range(0, l):
                result[i,j,k] = bitvector_i[k] ^ bitvector_j[k]

    return result


cpdef str longest_common_substring(str s1, str s2):
    cdef int len_s1 = len(s1)
    cdef int len_s2 = len(s2)
    cdef np.int_t[:, ::1] m = np.zeros((len_s1+1, len_s2+1), dtype=np.int, order="C")
    cdef int longest = 0
    cdef int x_longest = 0
    cdef int x, y

    for x in range(1, 1 + len_s1):
        for y in range(1, 1 + len_s2):
            if s1[x - 1] == s2[y - 1]:
                m[x, y] = m[x - 1, y - 1] + 1
                if m[x, y] > longest:
                    longest = m[x, y]
                    x_longest = x
            else:
                m[x, y] = 0
    return s1[x_longest - longest: x_longest]
