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
    for i in range(start, len_inpt):
        if reverse == False:
            if inpt[len_inpt - 1 - i + start]:
                result |= (1 << (i-start))
        else:
            if inpt[i]:
                result |= (1 << (i-start))
    return result

cpdef unsigned long long crc(unsigned char[:] inpt, unsigned char[:] polynomial, unsigned char[:] start_value, unsigned char[:] final_xor, bool lsb_first, bool reverse_polynomial, bool reverse_all, bool little_endian):
    cdef unsigned int len_inpt = len(inpt)
    cdef unsigned int i, idx, poly_order = len(polynomial)
    cdef unsigned long long crc_mask = (2**(poly_order - 1) - 1)
    cdef unsigned long long poly_mask = (crc_mask + 1) >> 1
    cdef unsigned long long poly_int = arr_to_number(polynomial, reverse_polynomial, 1) & crc_mask
    cdef unsigned short j, x

    # start value
    cdef unsigned long long temp, crc = arr_to_number(start_value, False, 0) & crc_mask

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
                temp |= (1 << (poly_order -2  -i))
        crc = temp & crc_mask

    # little endian encoding, different for 16, 32, 64 bit
    if poly_order - 1 == 16 and little_endian:
        crc = ((crc << 8) & 0xFF00) | (crc >> 8)
    elif poly_order - 1 == 32 and little_endian:
        crc = ((crc << 24) & 0xFF000000) | ((crc << 8) & 0x00FF0000) | ((crc >> 8) & 0x0000FF00) | (crc >> 24)
    elif poly_order - 1 == 64 and little_endian:
        crc =   ((crc << 56) & 0xFF00000000000000) |  (crc >> 56) \
              | ((crc >> 40) & 0x000000000000FF00) | ((crc << 40) & 0x00FF000000000000) \
              | ((crc << 24) & 0x0000FF0000000000) | ((crc >> 24) & 0x0000000000FF0000) \
              | ((crc << 8)  & 0x000000FF00000000) | ((crc >> 8)  & 0x00000000FF000000)

    return crc & crc_mask

cpdef tuple get_crc_datarange(unsigned char[:] inpt, unsigned char[:] polynomial, unsigned char[:] vrfy_crc, unsigned char[:] start_value, unsigned char[:] final_xor, bool lsb_first, bool reverse_polynomial, bool reverse_all, bool little_endian):
    cdef unsigned int len_inpt = len(inpt)
    cdef unsigned int i, idx, offset, data_end = 0, poly_order = len(polynomial)
    cdef np.ndarray[np.uint64_t, ndim=1] steps = np.empty(len_inpt+2, dtype=np.uint64)
    cdef unsigned long long temp
    cdef unsigned long long crc_mask = (2**(poly_order - 1) - 1)
    cdef unsigned long long poly_mask = (crc_mask + 1) >> 1
    cdef unsigned long long poly_int = arr_to_number(polynomial, reverse_polynomial, 1) & crc_mask
    cdef unsigned long long final_xor_int = arr_to_number(final_xor, False, 0) & crc_mask
    cdef unsigned long long vrfy_crc_int = arr_to_number(vrfy_crc, False, 0) & crc_mask
    cdef unsigned long long crcvalue = arr_to_number(start_value, False, 0) & crc_mask
    cdef unsigned short j = 0, len_crc = poly_order - 1
    cdef bool found

    # Find data_end (beginning of crc)
    if len_inpt <= len_crc or len_crc != len(vrfy_crc):
        return 0, 0
    for data_end in range(len_inpt - len_crc, -1, -1):
        i = 0
        for j in range(0, len_crc):
            if vrfy_crc[j] == inpt[data_end+j]:
                i += 1
            else:
                continue
        if i == len_crc:
            break
    if data_end <= 0:  # Could not find crc position
        return 0, 0

    step = [1] + [0] * (len_inpt - 1)

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

    # Reverse and little endian
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
            steps[i] = ((steps[i] << 8) & 0xFF00) | (steps[i] >> 8)
        elif poly_order - 1 == 32 and little_endian:
            steps[i] = ((steps[i] << 24) & 0xFF000000) | ((steps[i] << 8) & 0x00FF0000) | ((steps[i] >> 8) & 0x0000FF00) | (steps[i] >> 24)
        elif poly_order - 1 == 64 and little_endian:
            steps[i] =  ((steps[i] << 56) & 0xFF00000000000000) |  (steps[i] >> 56) \
                      | ((steps[i] >> 40) & 0x000000000000FF00) | ((steps[i] << 40) & 0x00FF000000000000) \
                      | ((steps[i] << 24) & 0x0000FF0000000000) | ((steps[i] >> 24) & 0x0000000000FF0000) \
                      | ((steps[i] << 8)  & 0x000000FF00000000) | ((steps[i] >> 8)  & 0x00000000FF000000)

    # Test data range from 0...start_crc until start_crc-1...start_crc
    # Compute start value
    crcvalue = crc(inpt[:data_end], polynomial, start_value, final_xor, lsb_first, reverse_polynomial, reverse_all, little_endian)
    if vrfy_crc_int == crcvalue:
        return 0, data_end
    found = False
    i = 0
    while i < data_end - 1:
        offset = 0
        while (inpt[i + offset] == False and i+offset < data_end - 1):  # skip leading 0s in data (doesn't change crc...)
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