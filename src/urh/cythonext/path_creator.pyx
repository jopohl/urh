import struct
# noinspection PyUnresolvedReferences
cimport numpy as np
import numpy as np


# As we do not use any numpy C API functions we do no import_array here,
# because it can lead to OS X error: https://github.com/jopohl/urh/issues/273
# np.import_array()

from cython.parallel import prange
from urh.cythonext.util cimport iq
from urh.ui.painting.path_painter import array_to_QPath

from urh import constants
import math
import cython

cpdef create_path(iq[:] samples, long long start, long long end, list subpath_ranges=None):
    cdef iq[:] values
    cdef long long[::1] sample_rng
    cdef np.int64_t[::1] x
    cdef iq sample, minimum, maximum, tmp
    cdef float scale_factor
    cdef long long i,j,index, chunk_end, num_samples, pixels_on_path, samples_per_pixel
    num_samples = end - start

    cdef dict type_lookup = {"char[:]": np.int8, "unsigned char[:]": np.uint8,
                             "short[:]": np.int16, "unsigned short[:]": np.uint16,
                             "float[:]": np.float32, "double[:]": np.float64}

    subpath_ranges = [(start, end)] if subpath_ranges is None else subpath_ranges
    pixels_on_path = constants.PIXELS_PER_PATH

    samples_per_pixel = <long long>(num_samples / pixels_on_path)

    cdef int num_threads = 0
    if samples_per_pixel < 20000:
        num_threads = 1

    if samples_per_pixel > 1:
        sample_rng = np.arange(start, end, samples_per_pixel, dtype=np.int64)
        values = np.zeros(2 * len(sample_rng), dtype=type_lookup[cython.typeof(samples)], order="C")
        scale_factor = num_samples / (2.0 * len(sample_rng))  # 2.0 is important to make it a float division!
        for i in prange(start, end, samples_per_pixel, nogil=True, schedule='static', num_threads=num_threads):
            chunk_end = i + samples_per_pixel
            if chunk_end >= end:
                chunk_end = end

            tmp = samples[i]
            minimum = tmp
            maximum = tmp

            for j in range(i + 1, chunk_end):
                sample = samples[j]
                if sample < minimum:
                    minimum = sample
                elif sample > maximum:
                    maximum = sample

            index = <long long>(2*(i-start)/samples_per_pixel)
            values[index] = minimum
            values[index + 1] = maximum

        x = np.repeat(sample_rng, 2)
    else:
        x = np.arange(start, end, dtype=np.int64)
        values = samples[start:end]
        scale_factor = 1.0

    cdef list result = []
    if scale_factor == 0:
        scale_factor = 1  # prevent division by zero

    for subpath_range in subpath_ranges:
        sub_start = ((((subpath_range[0]-start)/scale_factor) * scale_factor) - 2*scale_factor) / scale_factor
        sub_start =int(max(0, math.floor(sub_start)))
        sub_end = ((((subpath_range[1]-start)/scale_factor) * scale_factor) + 2*scale_factor) / scale_factor
        sub_end = int(max(0, math.ceil(sub_end)))
        result.append(array_to_QPath(x[sub_start:sub_end], values[sub_start:sub_end]))

    return result


cpdef create_live_path(iq[:] samples, unsigned int start, unsigned int end):
    return array_to_QPath(np.arange(start, end).astype(np.int64), samples)
