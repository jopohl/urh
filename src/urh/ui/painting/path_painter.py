import struct

from PySide2.QtCore import QByteArray, QDataStream
from PySide2.QtGui import QPainterPath
import numpy as np


def array_to_QPath(x, y):
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
    path = QPainterPath()

    n = x.shape[0]
    arr = np.empty(n+2, dtype=[('x', '>f8'), ('y', '>f8'), ('c', '>i4')])
    byteview = arr.view(dtype=np.uint8)
    byteview[:12] = 0
    byteview.data[12:20] = struct.pack('>ii', n, 0)
    arr[1:-1]['x'] = x
    arr[1:-1]['y'] = y
    arr[1:-1]['c'] = 1

    lastInd = 20*(n+1)
    byteview.data[lastInd:lastInd+4] = struct.pack('>i', 0)

    path.strn = byteview.data[12:lastInd+4]   # make sure data doesn't run away
    try:
        buf = QByteArray.fromRawData(path.strn)
    except TypeError:
        buf = QByteArray(bytes(path.strn))
    ds = QDataStream(buf)
    ds >> path

    return path
