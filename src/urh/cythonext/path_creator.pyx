import struct
# noinspection PyUnresolvedReferences
cimport numpy as np
import numpy as np
from PyQt5.QtCore import QByteArray, QDataStream
from PyQt5.QtGui import QPainterPath

# As we do not use any numpy C API functions we do no import_array here,
# because it can lead to OS X error: https://github.com/jopohl/urh/issues/273
# np.import_array()

from cython.parallel import prange

from urh import constants
import math

cpdef create_path(float[:] samples, long long start, long long end, list subpath_ranges=None):
    cdef float[:] values
    cdef long long[::1] sample_rng
    cdef np.int64_t[::1] x
    cdef float sample, minimum, maximum, tmp, scale_factor
    cdef long long i,j,index, chunk_end, num_samples, pixels_on_path, samples_per_pixel
    num_samples = end - start

    subpath_ranges = [(start, end)] if subpath_ranges is None else subpath_ranges
    pixels_on_path = constants.PIXELS_PER_PATH

    samples_per_pixel = <long long>(num_samples / pixels_on_path)

    if samples_per_pixel > 1:
        sample_rng = np.arange(start, end, samples_per_pixel, dtype=np.int64)
        values = np.zeros(2 * len(sample_rng), dtype=np.float32, order="C")
        scale_factor = num_samples / (2.0 * len(sample_rng))  # 2.0 is important to make it a float division!
        for i in prange(start, end, samples_per_pixel, nogil=True, schedule='static'):
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


cpdef create_live_path(float[:] samples, unsigned int start, unsigned int end):
    return array_to_QPath(np.arange(start, end).astype(np.int64), samples)

cpdef array_to_QPath(np.int64_t[:] x, float[:] y):
    """
    Convert an array of x,y coordinates to QPainterPath as efficiently as possible.

    Speed this up using >> operator
    Format is:
        numVerts(i4)   0(i4)
        x(f8)   y(f8)   0(i4)    <-- 0 means this vertex does not connect
        x(f8)   y(f8)   1(i4)    <-- 1 means this vertex connects to the previous vertex
        ...
        0(i4)

     All values are big endian--pack using struct.pack('>d') or struct.pack('>i')
    """
    cdef long long n = x.shape[0]
    # create empty array, pad with extra space on either end
    arr = np.zeros(n + 2, dtype=[('x', '>f8'), ('y', '>f8'), ('c', '>i4')])
    #arr = arr.byteswap().newbyteorder() # force native byteorder

    # write first two integers
    byte_view = arr.view(dtype=np.uint8)
    byte_view[:12] = 0
    byte_view.data[12:20] = struct.pack('>ii', n, 0)

    arr[1:-1]['x'] = x
    arr[1:-1]['y'] = np.negative(y)  # y negieren, da Koordinatensystem umgedreht
    arr[1:-1]['c'] = 1

    cdef long long last_index = 20 * (n + 1)
    byte_view.data[last_index:last_index + 4] = struct.pack('>i', 0)

    try:
        buf = QByteArray.fromRawData(byte_view.data[12:last_index + 4])
    except TypeError:
        buf = QByteArray(byte_view.data[12:last_index + 4])

    path = QPainterPath()
    ds = QDataStream(buf)
    ds >> path

    return path
