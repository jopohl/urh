# noinspection PyUnresolvedReferences
cimport numpy as np
import numpy as np

from libcpp cimport bool
from array import array

from urh.cythonext.util import crc

cpdef set find_longest_common_sub_sequence_indices(np.uint8_t[::1] seq1, np.uint8_t[::1] seq2):
    cdef unsigned int i, j, longest = 0, counter = 0, len_bits1 = len(seq1), len_bits2 = len(seq2)
    cdef unsigned short max_results = 10, current_result = 0

    cdef unsigned int[:, ::1] m = np.zeros((len_bits1+1, len_bits2+1), dtype=np.uint32, order="C")
    cdef unsigned int[:, ::1] result_indices = np.zeros((max_results, 2), dtype=np.uint32, order="C")

    for i in range(0, len_bits1):
        for j in range(0, len_bits2):
            if seq1[i] == seq2[j]:
                counter = m[i, j] + 1
                m[i+1, j+1] = counter

                if counter > longest:
                    longest = counter

                    current_result = 0
                    result_indices[current_result, 0] = i - counter + 1
                    result_indices[current_result, 1] = i + 1
                elif counter == longest:
                    if current_result < max_results - 1:
                        current_result += 1
                        result_indices[current_result, 0] = i - counter + 1
                        result_indices[current_result, 1] = i + 1

    cdef set result = set()
    for i in range(current_result+1):
        result.add((result_indices[i, 0], result_indices[i, 1]))

    return result

cpdef int find_first_difference(unsigned char[:] bits1, unsigned char[:] bits2):
    cdef int i
    cdef int smaller_len = min(len(bits1), len(bits2))

    for i in range(smaller_len):
        if bits1[i] != bits2[i]:
            return i

    return smaller_len


cpdef np.ndarray[np.float64_t] create_difference_histogram(list vectors, list active_indices):
    """
    Return a histogram of common ranges. E.g. [1, 1, 0.75, 0.8] means 75% of values at third column are equal
    
    :param vectors: Vectors over which differences the histogram will be created
    :param active_indices: Active indices of vectors. Vectors with index not in this list will be ignored
    :return: 
    """
    cdef unsigned long i,j,k,index_i,index_j, L = len(active_indices)
    cdef unsigned long longest = 0, len_vector
    for i in active_indices:
        len_vector = len(vectors[i])
        if len_vector > longest:
            longest = len_vector

    cdef np.ndarray[np.float64_t] histogram = np.zeros(longest, dtype=np.float64)
    cdef double n = (len(active_indices) * (len(active_indices) - 1)) // 2

    cdef np.ndarray[np.uint8_t] bitvector_i, bitvector_j

    for i in range(0, L - 1):
        index_i = active_indices[i]
        for j in range(i+1, L):
            index_j = active_indices[j]
            bitvector_i, bitvector_j = vectors[index_i], vectors[index_j]
            for k in range(0, <unsigned long>min(len(bitvector_i), len(bitvector_j))):
                if bitvector_i[k] == bitvector_j[k]:
                    histogram[k] += 1 / n
    return histogram

cpdef list find_occurrences(np.uint8_t[::1] a, np.uint8_t[::1] b,
                            unsigned long[:] ignore_indices=None, return_after_first=False):
    """
    Find the indices of occurrences of b in a. 
    
    :param a: Larger array
    :param b: Subarray to search for
    :return: List of start indices of b in a 
    """
    cdef unsigned long i, j
    cdef unsigned long len_a = len(a), len_b = len(b)

    if ignore_indices is None:
        ignore_indices = array("L", [])

    if len_b > len_a:
        return []

    cdef list result = []
    cdef bool found
    for i in range(0, (len_a-len_b) + 1):
        found = True
        for j in range(0, len_b):
            if a[i+j] != b[j] or i+j in ignore_indices:
                found = False
                break
        if found:
            if return_after_first:
                return [i]
            else:
                result.append(i)

    return result

cdef unsigned long long bit_array_to_number(unsigned char[:] bits, long long num_bits) nogil:
    if num_bits < 1:
        return 0

    cdef long long i, acc = 1
    cdef unsigned long long result = 0

    for i in range(0, num_bits):
        result += bits[num_bits-1-i] * acc
        acc *= 2

    return result

cpdef set check_crc_for_messages(unsigned long start, list message_indices, list bitvectors,
                                 unsigned long data_start, unsigned long data_stop,
                                 unsigned long crc_start, unsigned long crc_stop,
                                 unsigned char[:] crc_polynomial, unsigned char[:] crc_start_value,
                                 unsigned char[:] crc_final_xor,
                                 bool crc_lsb_first, bool crc_reverse_polynomial,
                                 bool crc_reverse_all, bool crc_little_endian):
    """
    Check a configurable subset of bitvectors for a matching CRC and return the indices of the 
    vectors who match the CRC with the given parameters
    :return: 
    """
    cdef set result = set()
    cdef unsigned long j, index, end = len(message_indices)
    cdef np.ndarray[np.uint8_t] bits
    cdef unsigned char[:] crc_input
    cdef unsigned long long check

    for j in range(start, end):
        index = message_indices[j]
        bits = bitvectors[index]
        crc_input = bits[data_start:data_stop]
        #check = int("".join(map(str, bits[crc_start:crc_stop])), 2)
        check = bit_array_to_number(bits[crc_start:crc_stop], crc_stop - crc_start)
        if crc(crc_input, crc_polynomial, crc_start_value, crc_final_xor,
               crc_lsb_first, crc_reverse_polynomial,
               crc_reverse_all, crc_little_endian) == check:
            result.add(index)

    return result
