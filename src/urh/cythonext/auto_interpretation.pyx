# noinspection PyUnresolvedReferences
import itertools
cimport numpy as np
import numpy as np

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


def segment_messages_from_magnitudes(float[:] magnitudes, float noise_threshold):
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

cpdef unsigned long[:] filter_plateau_lengths(np.ndarray[np.uint64_t, ndim=1]  plateau_lengths):
    # Cython version of this python code
    # filtered = [
    #     min(x, y) for x, y in itertools.combinations(merged_plateau_lengths, 2)
    #     if x != 0 and y != 0 and max(x, y) / min(x, y) - int(max(x, y) / min(x, y)) < 0.2
    # ]

    cdef unsigned long num_lengths = len(plateau_lengths)
    cdef np.ndarray[np.npy_bool, ndim=1, cast=True] mask = np.zeros(num_lengths, dtype=np.bool)
    cdef unsigned long i, j, x, y, minimum, maximum, min_index, k=0

    for i in range(0, num_lengths):
        for j in range(i+1, num_lengths):
            x = plateau_lengths[i]
            y = plateau_lengths[j]
            if x == 0 or y == 0:
                continue

            if x < y:
                min_index = i
                minimum = x
                maximum = y
            else:
                min_index = j
                minimum = y
                maximum = x

            if maximum / <double>minimum - (maximum / minimum) < 0.2:
                mask[min_index] = 1

    return plateau_lengths[mask]