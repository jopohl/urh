import struct

from PyQt5.QtCore import QByteArray, QDataStream
from PyQt5.QtGui import QPainterPath

# noinspection PyUnresolvedReferences
import numpy as np
cimport numpy as np
import  cython
from cython.parallel import prange

from urh import constants

cpdef create_path(float[:] samples, long long start, long long end):
    cdef float[::1] values
    cdef long long[::1] sample_rng
    cdef float sample, minimum, maximum, tmp
    cdef long long i,j,index, chunk_end, num_samples, pixels_on_path, samples_per_pixel
    num_samples = end - start

    pixels_on_path = constants.PIXELS_PER_PATH

    samples_per_pixel = <long long>(num_samples / pixels_on_path)

    if samples_per_pixel > 1:
        sample_rng = np.arange(start, end, samples_per_pixel, dtype=np.int64)
        values = np.zeros(2 * len(sample_rng), dtype=np.float32, order="C")
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

        return array_to_QPath(np.repeat(sample_rng, 2).astype(np.int64), values)
    else:
        return array_to_QPath_mem_opt(start, end, samples)


cpdef create_live_path(float[:] samples, unsigned int start, unsigned int end):
    return array_to_QPath(np.arange(start, end).astype(np.int64), samples)

cdef array_to_QPath_mem_opt(long long start, long long end, float[:] samples):
    """
    Optimiert auf RAM-Verbrauch. Der Python Garbage-Collector "übersieht" kleine Arrays und
    gibt den Speicher dann nicht mehr frei. Deshalb übernimmt diese Methode nur das gesamte Array von Samples
    und bildet die Teilbereiche selbst lokal. Auf diese Weise wird es vermieden, kleine Kopien des Sample-Arrays anzulegen.
    """
    path = QPainterPath()
    cdef long long n = end - start
    # create empty array, pad with extra space on either end
    arr = np.empty(n + 2, dtype=[('x', '>f8'), ('y', '>f8'), ('c', '>i4')])
    #arr = arr.byteswap().newbyteorder() # force native byteorder
    # write first two integers
    byteview = arr.view(dtype=np.uint8)
    byteview[:12] = 0
    byteview.data[12:20] = struct.pack('>ii', n, 0)

    # t = time.time()
    # # Fill array with vertex values
    arr[1:-1]['x'] = np.arange(start, end).astype(np.int64)
    arr[1:-1]['y'] = np.negative(samples[start:end])  # y negieren, da Koordinatensystem umgedreht
    arr[1:-1]['c'] = 1
    # print("Insert:", time.time() - t)
    #
    # # write last 0
    cdef long long lastInd = 20 * (n + 1)
    byteview.data[lastInd:lastInd + 4] = struct.pack('>i', 0)


    # create datastream object and stream into path
    # path.strn = byteview.data[12:lastInd + 4]  # make sure data doesn't run away
    #
    # try:
    #     buf = QByteArray.fromRawData(path.strn)
    # except TypeError:
    #     buf = QByteArray(bytes(path.strn))

    try:
        buf = QByteArray.fromRawData(byteview.data[12:lastInd + 4])
    except TypeError:
        buf = QByteArray(byteview.data[12:lastInd + 4])

    ds = QDataStream(buf)
    ds >> path

    return path

cpdef array_to_QPath(np.int64_t[:] x, float[:] y):
    """Convert an array of x,y coordinates to QPainterPath as efficiently as possible.
    This method is taken from PyQtGraph.
    """
    # # Speed this up using >> operator
    # # Format is:
    # #    numVerts(i4)   0(i4)
    # #    x(f8)   y(f8)   0(i4)    <-- 0 means this vertex does not connect
    # #    x(f8)   y(f8)   1(i4)    <-- 1 means this vertex connects to the previous vertex
    ##    ...
    ##    0(i4)
    ##
    ## All values are big endian--pack using struct.pack('>d') or struct.pack('>i')

    path = QPainterPath()
    cdef long long n = x.shape[0]
    # create empty array, pad with extra space on either end
    arr = np.empty(n + 2, dtype=[('x', '>f8'), ('y', '>f8'), ('c', '>i4')])
    #arr = arr.byteswap().newbyteorder() # force native byteorder
    # write first two integers
    byteview = arr.view(dtype=np.uint8)
    byteview[:12] = 0
    byteview.data[12:20] = struct.pack('>ii', n, 0)

    # t = time.time()
    # # Fill array with vertex values
    arr[1:-1]['x'] = x
    arr[1:-1]['y'] = np.negative(y)  # y negieren, da Koordinatensystem umgedreht
    arr[1:-1]['c'] = 1
    # print("Insert:", time.time() - t)
    #
    # # write last 0
    cdef long long lastInd = 20 * (n + 1)
    byteview.data[lastInd:lastInd + 4] = struct.pack('>i', 0)


    # create datastream object and stream into path
    # path.strn = byteview.data[12:lastInd + 4]  # make sure data doesn't run away
    #
    # try:
    #     buf = QByteArray.fromRawData(path.strn)
    # except TypeError:
    #     buf = QByteArray(bytes(path.strn))

    try:
        buf = QByteArray.fromRawData(byteview.data[12:lastInd + 4])
    except TypeError:
        buf = QByteArray(byteview.data[12:lastInd + 4])

    ds = QDataStream(buf)
    ds >> path

    return path