# noinspection PyUnresolvedReferences
cimport numpy as np
import numpy as np

# As we do not use any numpy C API functions we do no import_array here,
# because it can lead to OS X error: https://github.com/jopohl/urh/issues/273
# np.import_array()

cimport cython
from cython.parallel import prange
from libc.math cimport log10
from libcpp cimport bool

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
    cdef unsigned int maximum = 0
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

cpdef unsigned long long arr_to_number(unsigned char[:] inpt, bool reverse, unsigned int start = 0):
    cdef unsigned long long result = 0
    cdef unsigned int i, len_inpt = len(inpt)

    str_obj = (map(str, inpt))
    if reverse:
        return int("".join(reversed(str_obj)), 2)
    else:
        return int("".join(str_obj), 2)

cpdef unsigned long long crc(unsigned char[:] inpt, unsigned char[:] polynomial, unsigned char[:] start_value, unsigned char[:] final_xor, bool lsb_first, bool reverse_polynomial, bool reverse_all, bool little_endian):
    cdef unsigned int len_inpt = len(inpt)
    cdef unsigned int len_data = len_inpt
    if len_data % 8 != 0:
        len_data += 8 - (len_data % 8)
    cdef unsigned long long temp, crc = arr_to_number(start_value, False, 0)
    cdef unsigned int i, idx, poly_order = len(polynomial)
    cdef unsigned long long crc_mask = (2**(poly_order - 1) - 1)
    cdef unsigned long long poly_mask = (crc_mask + 1) >> 1
    cdef unsigned long long poly_int = arr_to_number(polynomial, reverse_polynomial, 1) & crc_mask
    cdef unsigned short j, x
    cdef unsigned char current_bit

    print("Inpt:", np.asarray(inpt, dtype=np.uint8))
    print("Poly:", np.asarray(polynomial, dtype=np.uint8), hex(crc_mask))
    print("Start:", np.asarray(start_value, dtype=np.uint8))
    print("Final:", np.asarray(final_xor, dtype=np.uint8))
    print("--> ", lsb_first, reverse_polynomial, reverse_all, little_endian)

    for i in range(0, len_data, 8):
        for j in range(0, 8):
            if lsb_first:
                idx = i + (7 - j)
            else:
                idx = i + j

            current_bit = inpt[idx] if idx < len_inpt else 0
            print(">>>", crc & poly_mask, current_bit, (crc & poly_mask) != current_bit)
            if (crc & poly_mask == 1) != current_bit:
                #crc[0:self.poly_order - 2] = crc[1:self.poly_order - 1]
                print(hex(crc))
                crc = (crc << 1) & crc_mask
                #for x in range(0, poly_order - 1):
                #    if reverse_polynomial:
                #        crc[x] ^= polynomial[poly_order - 1 - x]
                #    else:
                #        crc[x] ^= polynomial[x + 1]
                print(hex(crc), "XOR with", hex(poly_int))
                crc ^= poly_int
                print("Nach XOR:\n", hex(crc))
            else:
                crc = (crc << 1) & crc_mask
            print(current_bit, hex(crc))

    print("VOR FINAL XOR:", hex(crc))
    crc ^= arr_to_number(final_xor, False, 0)
    print("NACH FINAL XOR:", hex(crc))

    if reverse_all:
        temp = 0
        for i in range(0, poly_order - 1):
            if (crc & ((poly_order - 2 - i) << 1)):
                temp |= (1 << i)
        crc = temp & crc_mask

    if poly_order - 1 == 16 and little_endian:
        crc = ((crc << 8) & 0xFF00) | (crc >> 8)
    elif poly_order - 1 == 32 and little_endian:
        crc = ((crc << 24) & 0xFF000000) | ((crc << 8) & 0x00FF0000) | ((crc >> 8) & 0x0000FF00) | (crc >> 24)
    elif poly_order - 1 == 64 and little_endian:
        crc =   ((crc << 56) & 0xFF00000000000000) |  (crc >> 56) \
              | ((crc >> 40) & 0x000000000000FF00) | ((crc << 40) & 0x00FF000000000000) \
              | ((crc << 24) & 0x0000FF0000000000) | ((crc >> 24) & 0x0000000000FF0000) \
              | ((crc << 8)  & 0x000000FF00000000) | ((crc >> 8)  & 0x00000000FF000000)

    return crc