# noinspection PyUnresolvedReferences
cimport numpy as np
import numpy as np


from libc.math cimport floor, ceil
from libc.stdlib cimport malloc, free

from libcpp cimport bool
from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t, int32_t, int8_t, int64_t

from array import array


from urh.cythonext.util import crc

cpdef np.ndarray[np.uint8_t, ndim=3] build_xor_matrix(list bitvectors):
    cdef unsigned int maximum = 0
    cdef np.uint8_t[:] bitvector_i, bitvector_j
    cdef int i, j, l
    for i in range(0, len(bitvectors)):
        bitvector_i = bitvectors[i]
        if maximum < len(bitvector_i):
            maximum = len(bitvector_i)

    cdef np.ndarray[np.uint8_t, ndim=3] result = np.full((len(bitvectors), len(bitvectors), maximum), -1, dtype=np.uint8, order="C")

    for i in range(len(bitvectors)):
        bitvector_i = bitvectors[i]
        for j in range(i+1, len(bitvectors)):
            bitvector_j = bitvectors[j]
            l = min(len(bitvector_i), len(bitvector_j))
            for k in range(0, l):
                result[i,j,k] = bitvector_i[k] ^ bitvector_j[k]

    return result

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

cpdef uint32_t find_first_difference(uint8_t[::1] bits1, uint8_t[::1] bits2, uint32_t len_bits1, uint32_t len_bits2) nogil:
    cdef uint32_t i, smaller_len = min(len_bits1, len_bits2)

    for i in range(0, smaller_len):
        if bits1[i] != bits2[i]:
            return i

    return smaller_len

cpdef np.ndarray[np.uint32_t, ndim=2, mode="c"] get_difference_matrix(list bitvectors):
    cdef uint32_t i, j, N = len(bitvectors)
    cdef np.ndarray[np.uint32_t, ndim=2, mode="c"] result = np.zeros((N, N), dtype=np.uint32, order="C")

    cdef uint8_t[::1] bitvector_i
    cdef uint32_t len_bitvector_i

    for i in range(N):
        bitvector_i = bitvectors[i]
        len_bitvector_i = len(bitvector_i)
        for j in range(i + 1, N):
            result[i, j] = find_first_difference(bitvector_i, bitvectors[j], len_bitvector_i, len(bitvectors[j]))

    return result

cpdef list get_hexvectors(list bitvectors):
    cdef list result = []
    cdef uint8_t[::1] bitvector
    cdef size_t i, j, M, N = len(bitvectors)

    cdef np.ndarray[np.uint8_t, mode="c"] hexvector
    cdef size_t len_bitvector

    for i in range(0, N):
        bitvector = bitvectors[i]
        len_bitvector = len(bitvector)

        M = <size_t>ceil(len_bitvector / 4)
        hexvector = np.zeros(M, dtype=np.uint8, order="C")

        for j in range(0, M):
            hexvector[j] = bit_array_to_number(bitvector, min(len_bitvector, 4*j+4), 4*j)

        result.append(hexvector)

    return result


cdef int lower_multiple_of_n(int number, int n) nogil:
        return n * <int>floor(number / n)

cdef int64_t find(uint8_t[:] data, int64_t len_data, uint8_t element, int64_t start=0) nogil:
    cdef int64_t i
    for i in range(start, len_data):
        if data[i] == element:
            return i
    return -1

cpdef tuple get_raw_preamble_position(uint8_t[:] bitvector):
    cdef int64_t N = len(bitvector)
    cdef int64_t i, j, n, m, start = -1
    cdef double k = 0

    cdef int64_t lower = 0, upper = 0
    cdef uint8_t a, b

    cdef uint8_t* preamble_pattern
    cdef int64_t len_preamble_pattern, preamble_end

    cdef bool preamble_end_reached

    if N == 0:
        return lower, upper

    while k < 2 and start < N:
        start += 1

        a = bitvector[start]
        b = 1 if a == 0 else 0

        # now we search for the pattern a^n b^m
        n = find(bitvector, N, b, start) - start

        if n <= 0:
            return 0, 0, 0

        m = find(bitvector, N, a, start+n) - n - start

        if m <= 0:
            return 0, 0, 0

        #preamble_pattern = a * n + b * m
        len_preamble_pattern = n + m
        preamble_pattern = <uint8_t*> malloc(len_preamble_pattern * sizeof(uint8_t))
        for j in range(0, n):
            preamble_pattern[j] = a
        for j in range(n, len_preamble_pattern):
            preamble_pattern[j] = b

        preamble_end = start
        preamble_end_reached = False
        for i in range(start, N, len_preamble_pattern):
            if preamble_end_reached:
                break
            for j in range(0, len_preamble_pattern):
                if bitvector[i+j] != preamble_pattern[j]:
                    preamble_end_reached = True
                    preamble_end = i
                    break

        free(preamble_pattern)

        upper = start + lower_multiple_of_n(preamble_end + 1 - start, len_preamble_pattern)
        lower = upper - len_preamble_pattern

        k = (upper - start) / len_preamble_pattern

    if k > 2:
        return start, lower, upper
    else:
        # no preamble found
        return 0, 0, 0


cpdef dict find_possible_sync_words(np.ndarray[np.uint32_t, ndim=2] difference_matrix,
                               np.ndarray[np.uint32_t, ndim=2] raw_preamble_positions,
                               list bitvectors, int n_gram_length):
    cdef dict possible_sync_words = dict()

    cdef uint32_t i, j, num_rows = difference_matrix.shape[0], num_cols = difference_matrix.shape[1]
    cdef uint32_t sync_len, sync_end, start, index, k, n

    cdef bytes sync_word

    cdef np.ndarray[np.uint8_t] bitvector

    cdef uint8_t ij_ctr = 0
    cdef uint32_t* ij_arr = <uint32_t*>malloc(2 * sizeof(uint32_t))

    cdef uint8_t* temp

    for i in range(0, num_rows):
        for j in range(i + 1, num_cols):
            # position of first difference between message i and j
            sync_end = difference_matrix[i, j]

            if sync_end == 0:
                continue

            ij_arr[0] = i
            ij_arr[1] = j

            for k in range(0, 2):
                for ij_ctr in range(0, 2):
                    index = ij_arr[ij_ctr]
                    start = raw_preamble_positions[index, 0] + raw_preamble_positions[index, k + 1]

                    # We take the next lower multiple of n for the sync len
                    # In doubt, it is better to under estimate the sync len to prevent it from
                    # taking needed values from other fields e.g. leading zeros for a length field
                    sync_len = max(0, lower_multiple_of_n(sync_end - start, n_gram_length))

                    if sync_len >= 2:
                        bitvector = bitvectors[index]
                        if sync_len == 2:
                            # Sync word must not be empty or just two bits long and "10" or "01" because
                            # that would be indistinguishable from the preamble
                            if bitvector[start] == 0 and bitvector[start+1] == 1:
                                continue
                            if bitvector[start] == 1 and bitvector[start+1] == 0:
                                continue

                        temp = <uint8_t*>malloc(sync_len * sizeof(uint8_t))
                        for n in range(0, sync_len):
                            temp[n] = bitvector[start+n]
                        sync_word = <bytes> temp[:sync_len]
                        free(temp)

                        possible_sync_words.setdefault(sync_word, 0)
                        if (start + sync_len) % n_gram_length == 0:
                            # if sync end aligns nicely at n gram length give it a larger score
                            possible_sync_words[sync_word] += 1
                        else:
                            possible_sync_words[sync_word] += 0.5

    free(ij_arr)

    return possible_sync_words


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
                            unsigned long[:] ignore_indices=None, bool return_after_first=False):
    """
    Find the indices of occurrences of b in a. 
    
    :param a: Larger array
    :param b: Subarray to search for
    :return: List of start indices of b in a 
    """
    cdef unsigned long i, j
    cdef unsigned long len_a = len(a), len_b = len(b)

    cdef bool ignore_indices_present = ignore_indices is not None

    if len_b > len_a:
        return []

    cdef list result = []
    cdef bool found
    for i in range(0, (len_a-len_b) + 1):
        found = True
        for j in range(0, len_b):
            if ignore_indices_present:
                if i+j in ignore_indices:
                    found = False
                    break

            if a[i+j] != b[j]:
                found = False
                break
        if found:
            if return_after_first:
                return [i]
            else:
                result.append(i)

    return result

cdef unsigned long long bit_array_to_number(uint8_t[::1] bits, int64_t end, int64_t start=0) nogil:
    if end < 1:
        return 0

    cdef long long i, acc = 1
    cdef unsigned long long result = 0

    for i in range(start, end):
        result += bits[end-1-i+start] * acc
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
