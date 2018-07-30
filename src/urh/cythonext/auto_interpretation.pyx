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