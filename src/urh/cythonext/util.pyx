# noinspection PyUnresolvedReferences
cimport numpy as np
import numpy as np

# As we do not use any numpy C API functions we do no import_array here,
# because it can lead to OS X error: https://github.com/jopohl/urh/issues/273
# np.import_array()

from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t, int64_t
from libc.stdlib cimport malloc, calloc, free
from cython.parallel import prange
from libc.math cimport log10,pow,sqrt
from libcpp cimport bool

from cpython cimport array
import array

from urh.cythonext.util cimport iq

cpdef tuple minmax(iq[:] arr):
    cdef long long i, ns = len(arr)
    if ns == 0:
        return 0, 0

    cdef iq maximum = arr[0]
    cdef iq minimum = arr[0]
    cdef iq e

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

cpdef uint64_t bit_array_to_number(uint8_t[:] bits, int64_t end, int64_t start=0) nogil:
    if end < 1:
        return 0

    cdef long long i, acc = 1
    cdef unsigned long long result = 0

    for i in range(start, end):
        result += bits[end-1-i+start] * acc
        acc *= 2

    return result

cpdef uint64_t arr_to_number(uint8_t[:] inpt, bool reverse = False, unsigned int start = 0):
    cdef uint64_t result = 0
    cdef unsigned int i, len_inpt = len(inpt)
    for i in range(start, len_inpt):
        if not reverse:
            if inpt[len_inpt - 1 - i + start]:
                result |= (1 << (i-start))
        else:
            if inpt[i]:
                result |= (1 << (i-start))
    return result

cpdef uint64_t crc(uint8_t[:] inpt, uint8_t[:] polynomial, uint8_t[:] start_value, uint8_t[:] final_xor, bool lsb_first, bool reverse_polynomial, bool reverse_all, bool little_endian):
    cdef unsigned int len_inpt = len(inpt)
    cdef unsigned int i, idx, poly_order = len(polynomial)
    cdef uint64_t crc_mask = <uint64_t> pow(2, poly_order - 1) - 1
    cdef uint64_t poly_mask = (crc_mask + 1) >> 1
    cdef uint64_t poly_int = arr_to_number(polynomial, reverse_polynomial, 1) & crc_mask
    cdef unsigned short j, x

    # start value
    cdef uint64_t temp, crc = arr_to_number(start_value, False, 0) & crc_mask

    for i in range(0, len_inpt+7, 8):
        for j in range(0, 8):
            if lsb_first:
                idx = i + (7 - j)
            else:
                idx = i + j

            # generic crc algorithm
            if idx >= len_inpt:
                break

            if (crc & poly_mask > 0) != inpt[idx]:
                crc = (crc << 1) & crc_mask
                crc ^= poly_int
            else:
                crc = (crc << 1) & crc_mask

    # final XOR
    crc ^= arr_to_number(final_xor, False, 0) & crc_mask

    # reverse all bits
    if reverse_all:
        temp = 0
        for i in range(0, poly_order - 1):
            if crc & (1 << i):
                temp |= (1 << (poly_order - 2 - i))
        crc = temp & crc_mask

    # little endian encoding, different for 16, 32, 64 bit
    if poly_order - 1 == 16 and little_endian:
        crc = ((crc << 8) & 0xFF00) | (crc >> 8)
    elif poly_order - 1 == 32 and little_endian:
        crc = ((crc << 24) & <uint64_t>0xFF000000) | ((crc << 8) & 0x00FF0000) | ((crc >> 8) & 0x0000FF00) | (crc >> 24)
    elif poly_order - 1 == 64 and little_endian:
        crc =   ((crc << 56) & <uint64_t>0xFF00000000000000) |  (crc >> 56) \
              | ((crc >> 40) & <uint64_t>0x000000000000FF00) | ((crc << 40) & <uint64_t>0x00FF000000000000) \
              | ((crc << 24) & <uint64_t>0x0000FF0000000000) | ((crc >> 24) & <uint64_t>0x0000000000FF0000) \
              | ((crc << 8)  & <uint64_t>0x000000FF00000000) | ((crc >> 8)  & <uint64_t>0x00000000FF000000)

    return crc & crc_mask


cpdef np.ndarray[np.double_t, ndim=1] get_magnitudes(IQ arr):
    cdef uint64_t i, n = len(arr)

    cdef np.ndarray[np.double_t, ndim=1] result = np.zeros(n, dtype = np.double)

    for i in range(0, n):
        result[i] = sqrt(arr[i][0] * arr[i][0] + arr[i][1] * arr[i][1])

    return result

cpdef np.ndarray[np.uint64_t, ndim=1] calculate_cache(uint8_t[:] polynomial, bool reverse_polynomial=False, uint8_t bits=8):
    cdef uint8_t j, poly_order = len(polynomial)
    cdef uint64_t crc_mask = <uint64_t> pow(2, poly_order - 1) - 1
    cdef uint64_t poly_mask = (crc_mask + 1) >> 1
    cdef uint64_t poly_int = arr_to_number(polynomial, reverse_polynomial, 1) & crc_mask
    cdef uint64_t crcv, i
    cdef np.ndarray[np.uint64_t, ndim=1] cache = np.zeros(<uint64_t> pow(2, bits), dtype = np.uint64)
    # Caching
    for i in range(0, <uint32_t> len(cache)):
        crcv = i << (poly_order - 1 - bits)
        for _ in range(0, bits):
            if (crcv & poly_mask) > 0:
                crcv = (crcv << 1) & crc_mask
                crcv ^= poly_int
            else:
                crcv = (crcv << 1) & crc_mask
        cache[i] = crcv
    return cache

cpdef uint64_t cached_crc(uint64_t[:] cache, uint8_t bits, uint8_t[:] inpt, uint8_t[:] polynomial, uint8_t[:] start_value, uint8_t[:] final_xor, bool lsb_first, bool reverse_polynomial, bool reverse_all, bool little_endian):
    cdef unsigned int len_inpt = len(inpt)
    cdef unsigned int i, poly_order = len(polynomial)
    cdef uint64_t crc_mask = <uint64_t> pow(2, poly_order - 1) - 1
    cdef uint64_t poly_mask = (crc_mask + 1) >> 1
    cdef uint64_t poly_int = arr_to_number(polynomial, reverse_polynomial, 1) & crc_mask
    cdef uint64_t temp, crcv, data, pos
    cdef uint8_t j

    # For inputs smaller than 8 bits, call normal function
    if len_inpt < bits:
        return crc(inpt, polynomial, start_value, final_xor, lsb_first, reverse_polynomial, reverse_all, little_endian)

    # CRC
    crcv = arr_to_number(start_value, False, 0) & crc_mask
    for i in range(0, len_inpt - bits + 1, bits):
        data = 0
        if lsb_first:
            for j in range(0, bits):
                if inpt[i + j]:
                    data |= (1 << j)
        else:
            for j in range(0, bits):
                if inpt[i + bits - 1 - j]:
                    data |= (1 << j)
        pos = (crcv >> (poly_order - bits - 1)) ^ data
        crcv = ((crcv << bits) ^ cache[pos]) & crc_mask

    # Are we done?
    if len_inpt % bits > 0:
        # compute rest of crc inpt[-(len_inpt%8):] with normal function
        # Set start_value to current crc value
        for i in range(0, len(start_value)):
            start_value[len(start_value) - 1 - i] = True if (crcv & (1 << i)) > 0 else False
        crcv = crc(inpt[len_inpt-(len_inpt%bits):len_inpt], polynomial, start_value, final_xor, lsb_first, reverse_polynomial, reverse_all, little_endian)
    else:
        # final XOR
        crcv ^= arr_to_number(final_xor, False, 0) & crc_mask

        # reverse all bits
        if reverse_all:
            temp = 0
            for i in range(0, poly_order - 1):
                if crcv & (1 << i):
                    temp |= (1 << (poly_order - 2 - i))
            crcv = temp & crc_mask

        # little endian encoding, different for 16, 32, 64 bit
        if poly_order - 1 == 16 and little_endian:
            crcv = ((crcv << 8) & 0xFF00) | (crcv >> 8)
        elif poly_order - 1 == 32 and little_endian:
            crcv = ((crcv << 24) & <uint64_t>0xFF000000) | ((crcv << 8) & 0x00FF0000) | ((crcv >> 8) & 0x0000FF00) | (crcv >> 24)
        elif poly_order - 1 == 64 and little_endian:
            crcv =  ((crcv << 56) & <uint64_t>0xFF00000000000000) |  (crcv >> 56) \
                  | ((crcv >> 40) & <uint64_t>0x000000000000FF00) | ((crcv << 40) & <uint64_t>0x00FF000000000000) \
                  | ((crcv << 24) & <uint64_t>0x0000FF0000000000) | ((crcv >> 24) & <uint64_t>0x0000000000FF0000) \
                  | ((crcv << 8)  & <uint64_t>0x000000FF00000000) | ((crcv >> 8)  & <uint64_t>0x00000000FF000000)
    return crcv & crc_mask

cpdef tuple get_crc_datarange(uint8_t[:] inpt, uint8_t[:] polynomial, uint64_t vrfy_crc_start, uint8_t[:] start_value, uint8_t[:] final_xor, bool lsb_first, bool reverse_polynomial, bool reverse_all, bool little_endian):
    cdef uint32_t len_inpt = len(inpt), poly_order = len(polynomial)
    cdef uint8_t j = 0, len_crc = poly_order - 1

    if vrfy_crc_start-1+len_crc >= len_inpt or vrfy_crc_start < 2:
        return 0, 0

    cdef uint64_t* steps = <uint64_t*>calloc(len_inpt+2, sizeof(uint64_t))
    cdef uint64_t temp
    cdef uint64_t crc_mask = <uint64_t> pow(2, poly_order - 1) - 1
    cdef uint64_t poly_mask = (crc_mask + 1) >> 1
    cdef uint64_t poly_int = arr_to_number(polynomial, reverse_polynomial, 1) & crc_mask
    cdef uint64_t final_xor_int = arr_to_number(final_xor, False, 0) & crc_mask
    cdef uint64_t vrfy_crc_int = arr_to_number(inpt[vrfy_crc_start:vrfy_crc_start+len_crc], False, 0) & crc_mask
    cdef uint64_t crcvalue = arr_to_number(start_value, False, 0) & crc_mask
    cdef bool found
    cdef uint32_t i, idx, offset, data_end = vrfy_crc_start
    cdef uint8_t* step = <uint8_t*>calloc(len_inpt, sizeof(uint8_t))
    step[0] = 1

    # crcvalue is initialized with start_value
    for i in range(0, data_end+7, 8):
        for j in range(0, 8):
            if lsb_first:
                idx = i + (7 - j)
            else:
                idx = i + j

            # generic crc algorithm
            if idx >= data_end:
                break

            if (crcvalue & poly_mask > 0) != step[idx]:
                crcvalue = (crcvalue << 1) & crc_mask
                crcvalue ^= poly_int
            else:
                crcvalue = (crcvalue << 1) & crc_mask
            # Save steps XORed with final_xor
            steps[idx] = crcvalue ^ final_xor_int

    free(step)

    # Reverse and little endian
    if reverse_all or little_endian:
        for i in range(0, data_end):
            # reverse all bits
            if reverse_all:
                temp = 0
                for j in range(0, poly_order - 1):
                    if steps[i] & (1 << j):
                        temp |= (1 << (poly_order -2  - j))
                steps[j] = temp & crc_mask

            # little endian encoding, different for 16, 32, 64 bit
            if poly_order - 1 == 16 and little_endian:
                steps[i] = ((steps[i] << 8) & <uint64_t> 0xFF00) | (steps[i] >> 8)
            elif poly_order - 1 == 32 and little_endian:
                steps[i] = ((steps[i] << 24) & <uint64_t> 0xFF000000) | ((steps[i] << 8) & <uint64_t> 0x00FF0000) | ((steps[i] >> 8) &  <uint64_t> 0x0000FF00) | (steps[i] >> 24)
            elif poly_order - 1 == 64 and little_endian:
                steps[i] =  ((steps[i] << 56) & <uint64_t> 0xFF00000000000000) |  (steps[i] >> 56) \
                          | ((steps[i] >> 40) & <uint64_t> 0x000000000000FF00) | ((steps[i] << 40) & <uint64_t> 0x00FF000000000000) \
                          | ((steps[i] << 24) & <uint64_t> 0x0000FF0000000000) | ((steps[i] >> 24) & <uint64_t> 0x0000000000FF0000) \
                          | ((steps[i] << 8)  & <uint64_t> 0x000000FF00000000) | ((steps[i] >> 8)  & <uint64_t> 0x00000000FF000000)

    # Test data range from 0...start_crc until start_crc-1...start_crc
    # Compute start value
    crcvalue = crc(inpt[:data_end], polynomial, start_value, final_xor, lsb_first, reverse_polynomial, reverse_all, little_endian)
    try:
        if vrfy_crc_int == crcvalue:
            return 0, data_end
        found = False

        i = 0
        while i < data_end - 1:
            offset = 0
            while inpt[i + offset] == False and i+offset < data_end - 1:  # skip leading 0s in data (doesn't change crc...)
                offset += 1
            # XOR delta=crc(10000...) to last crc value to create next crc value
            crcvalue ^= steps[data_end-i-offset-1]
            if found:
                return i, data_end  # Return start_data, end_data
            if vrfy_crc_int == crcvalue:
                found = True
            i += 1 + offset

        # No beginning found
        return 0, 0
    finally:
        free(steps)

cdef db(unsigned int t, unsigned int p, unsigned int k, unsigned int n,
        uint8_t* a, uint8_t* sequence, uint64_t* current_index):
    cdef unsigned int i,j

    if t > n:
        if n % p == 0:
            for i in range(1, p+1):
                sequence[current_index[0]] = a[i]
                current_index[0] += 1
    else:
        a[t] = a[t - p]
        db(t + 1, p, k, n, a, sequence, current_index)
        for j in range(a[t - p] + 1, k):
            a[t] = j
            db(t+1, t, k, n, a, sequence, current_index)

cpdef array.array de_bruijn(unsigned int n):
    cdef unsigned int k = 2  #  Alphabet size is 2 because our alphabet is [0, 1]
    cdef uint64_t len_sequence = k ** n

    cdef uint8_t* a = <uint8_t*>calloc(k*n, sizeof(uint8_t))

    cdef array.array array_template = array.array('B', [])
    cdef array.array sequence
    sequence = array.clone(array_template, len_sequence, zero=False)

    cdef uint64_t* current_index = <uint64_t*>calloc(1, sizeof(uint64_t))

    db(1, 1, k, n, a, sequence.data.as_uchars, current_index)

    try:
        return sequence
    finally:
        free(a)
        free(current_index)
