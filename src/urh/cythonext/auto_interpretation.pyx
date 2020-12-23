# noinspection PyUnresolvedReferences
cimport numpy as np
import numpy as np
from cpython cimport array
import array
import cython

from cython.parallel import prange
from libc.stdlib cimport malloc, free
from libcpp.algorithm cimport sort
from libc.stdint cimport uint64_t

cpdef tuple k_means(float[:] data, unsigned int k=2):
    cdef float[:] centers = np.empty(k, dtype=np.float32)
    cdef list clusters = []
    cdef set unique = set(data)
    cdef unsigned long i

    if len(unique) < k:
        print("Warning: less different values than k")
        k = len(unique)

    for i in range(k):
        centers[i] = unique.pop()
        clusters.append([])

    cdef float[:] old_centers = np.array(centers, dtype=np.float32)
    cdef float distance, min_distance, error = 1.0
    cdef unsigned int j, index = 0, N = len(data)

    while error != 0:
        for i in range(k):
            clusters[i].clear()

        for i in range(N):
            min_distance = 999999999
            for j in range(k):
                distance = (centers[j] - data[i]) * (centers[j] - data[i])
                if distance < min_distance:
                    min_distance = distance
                    index = j
            clusters[index].append(data[i])

        old_centers = np.array(centers)
        for i in range(k):
            centers[i] = np.mean(clusters[i])

        error = 0.0
        for i in range(k):
            error += old_centers[i] * old_centers[i] - centers[i] * centers[i]

    return centers, clusters


def segment_messages_from_magnitudes(cython.floating[:] magnitudes, float noise_threshold):
    """
    Get the list of start, end indices of messages

    :param magnitudes: Magnitudes of samples
    :param q: Factor which controls how many samples of previous above noise plateau must be under noise to be counted as noise
    :return:
    """
    cdef list result = []

    if len(magnitudes) == 0:
        return []

    cdef unsigned long i, N = len(magnitudes), start = 0
    cdef unsigned long summed_message_samples = 0

    # tolerance / robustness against outliers
    cdef unsigned int outlier_tolerance = 10
    cdef unsigned int conseq_above = 0, conseq_below = 0

    # Three states: 1 = above noise, 0 = in noise, but not yet above k threshold (k * above_total), -1 = in noise
    cdef int state
    state = 1 if magnitudes[0] > noise_threshold else -1

    cdef bint is_above_noise

    for i in range(N):
        is_above_noise = magnitudes[i] > noise_threshold
        if state == 1:
            if is_above_noise:
                conseq_below = 0
            else:
                conseq_below += 1
        elif state == -1:
            if is_above_noise:
                conseq_above += 1
            else:
                conseq_above = 0

        # Perform state change if necessary
        if state == 1 and conseq_below >= outlier_tolerance:
            # 1 -> -1
            state = -1
            result.append((start, i - conseq_below))
            summed_message_samples += (i-conseq_below) - start
            conseq_below = conseq_above = 0
        elif state == -1 and conseq_above >= outlier_tolerance:
            # -1 -> 1
            state = 1
            start = i - conseq_above
            conseq_below = conseq_above = 0

    # append last message
    if state == 1 and start < N - conseq_below:
        result.append((start, N - conseq_below))

    return result

cpdef uint64_t[:] get_threshold_divisor_histogram(uint64_t[:] plateau_lengths, float threshold=0.2):
    """
    Get a histogram (i.e. count) how many times a value is a threshold divisor for other values in given data
    
    Threshold divisible is defined as having a decimal place less than .2 (threshold)
    
    :param plateau_lengths: 
    :return: 
    """
    cdef uint64_t i, j, x, y, minimum, maximum, num_lengths = len(plateau_lengths)

    cdef np.ndarray[np.uint64_t, ndim=1] histogram = np.zeros(int(np.max(plateau_lengths)) + 1, dtype=np.uint64)

    for i in range(0, num_lengths):
        for j in range(i+1, num_lengths):
            x = plateau_lengths[i]
            y = plateau_lengths[j]
            if x == 0 or y == 0:
                continue

            if x < y:
                minimum = x
                maximum = y
            else:
                minimum = y
                maximum = x

            if maximum / <double>minimum - (maximum / minimum) < threshold:
                histogram[minimum] += 1

    return histogram

cpdef np.ndarray[np.uint64_t, ndim=1] merge_plateaus(np.ndarray[np.uint64_t, ndim=1] plateaus,
                                                     uint64_t tolerance,
                                                     uint64_t max_count):
    cdef uint64_t j, n, L = len(plateaus), current = 0, i = 1, tmp_sum
    if L == 0:
        return np.zeros(0, dtype=np.uint64)

    cdef np.ndarray[np.uint64_t, ndim=1] result = np.empty(L, dtype=np.uint64)
    if plateaus[0] <= tolerance:
        result[0] = 0
    else:
        result[0] = plateaus[0]

    while i < L and current < max_count:
        if plateaus[i] <= tolerance:
            # Look ahead to see whether we need to merge a larger window e.g. for 67, 1, 10, 1, 21
            n = 2
            while i + n < L and plateaus[i + n] <= tolerance:
                n += 2

            tmp_sum = 0
            for j in range(i - 1, min(L, i + n)):
                tmp_sum += plateaus[j]

            result[current] = tmp_sum
            i += n
        else:
            current += 1
            result[current] = plateaus[i]
            i += 1

    return result[:current+1]


cpdef np.ndarray[np.uint64_t, ndim=1] get_plateau_lengths(float[:] rect_data, float center, int percentage=25):
    if len(rect_data) == 0 or center is None:
        return np.array([], dtype=np.uint64)

    cdef int state, new_state
    state = -1 if rect_data[0] <= center else 1
    cdef unsigned long long plateau_length = 0
    cdef unsigned long long current_sum = 0
    cdef unsigned long long i = 0
    cdef unsigned long long len_data = len(rect_data)
    cdef float sample

    cdef array.array result = array.array('Q', [])

    for i in range(0, len_data):
        if current_sum >= percentage * len_data / 100:
            break

        sample = rect_data[i]
        new_state = -1 if sample <= center else 1

        if state == new_state:
            plateau_length += 1
        else:
            result.append(plateau_length)
            current_sum += plateau_length
            state = new_state
            plateau_length = 1

    return np.array(result, dtype=np.uint64)


cdef float median(double[:] data, unsigned long start, unsigned long data_len, unsigned int k=3) nogil:
    cdef unsigned long i, j

    if start + k > data_len:
        k = data_len - start

    cdef float* buffer = <float *>malloc(k * sizeof(float))
    for i in range(0, k):
        buffer[i] = data[start+i]

    sort(&buffer[0], (&buffer[0]) + k)
    try:
        return buffer[k//2]
    finally:
        free(buffer)

cpdef np.ndarray[np.float32_t, ndim=1] median_filter(double[:] data, unsigned int k=3):
    cdef long long start, end, i, n = len(data)

    cdef np.ndarray[np.float32_t, ndim=1] result = np.zeros(n, dtype=np.float32)

    for i in prange(0, n, nogil=True, schedule='static'):
        if i < k // 2:
            start = 0
        else:
            start = i - k // 2

        result[i] = median(data, start=i, data_len=n, k=k)

    return result
