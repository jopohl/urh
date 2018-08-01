# noinspection PyUnresolvedReferences
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


def segment_messages_from_magnitudes(float[:] magnitudes, float noise_threshold, unsigned int q=2):
    """
    Get the list of start, end indices of messages

    :param magnitudes: Magnitudes of samples
    :param q: Factor which controls how many samples of previous above noise plateau must be under noise to be counted as noise
    :return:
    """
    cdef list result = []

    if len(magnitudes) == 0:
        return []

    cdef unsigned long i, N = len(magnitudes)

    # tolerance / robustness against outliers
    cdef unsigned int outlier_tolerance = 3
    cdef unsigned int conseq_above = 0, conseq_below = 0

    # total length of the current plateau i.e. length of current message and pause in samples
    cdef unsigned long above_total = 0, below_total = 0

    # Three states: 1 = above noise, 0 = in noise, but not yet above k threshold (k * above_total), -1 = in noise
    cdef int state
    state = 1 if magnitudes[0] > noise_threshold else -1
    start = 0

    cdef bint is_above_noise

    for i in range(N):
        # Process current sample, increase local and total counters depending on current state and sample
        is_above_noise = magnitudes[i] > noise_threshold
        if state == 1:
            above_total += 1
            if is_above_noise:
                conseq_below = 0
            else:
                conseq_below += 1
        elif state == 0 or state == -1:
            below_total += 1
            if is_above_noise:
                conseq_above += 1
            else:
                conseq_above = 0

        # Perform state change if necessary
        if state == 1 and conseq_below >= outlier_tolerance:
            # 1 -> 0
            state = 0
        elif state == 0 and conseq_above >= outlier_tolerance:
            # 0 -> 1
            state = 1
            above_total += below_total
            below_total = 0
        elif state == 0 and below_total >= q * above_total:
            # 0 -> -1
            state = -1
            result.append((start, start + above_total))
            above_total = 0
        elif state == -1 and conseq_above >= outlier_tolerance:
            # -1 -> 1
            state = 1
            start = i - conseq_above
            below_total = 0

    # append last message
    if state in (0, 1) and above_total >= 0:
        result.append((start, start + above_total))

    return result
