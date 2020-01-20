import struct
import crcmod
import numpy as np

# http://slicer-devel.65872.n3.nabble.com/OpenIGTLinkIF-and-CRC-td4031360.html
CRC64 = crcmod.mkCrcFun(0x142F0E1EBA9EA3693, rev=False, initCrc=0x0000000000000000, xorOut=0x0000000000000000)


# https://github.com/openigtlink/OpenIGTLink/blob/cf9619e2fece63be0d30d039f57b1eb4d43b1a75/Source/igtlutil/igtl_util.c#L168
def igtl_nanosec_to_frac(nanosec):
    base = 1000000000  # 10^9
    mask = 0x80000000
    r = 0x00000000
    while mask:
        base += 1
        base >>= 1
        if nanosec >= base:
            r |= mask
            nanosec = nanosec - base
        mask >>= 1
    return r


def igtl_frac_to_nanosec(frac):
    base = 1000000000  # 10^9

    mask = 0x80000000
    r = 0x00000000

    while mask:
        base += 1
        base >>= 1

        tmp = base if (frac & mask) else 0
        r = r + tmp
        mask >>= 1

    return r

"""
TERNARY OPERATOR 
C++; 
tmp = (frac & mask)? base : 0

PYTHON:
f frac and mask:
    tmp = base
else:
    tmp = 0



self._timestamp = 1579184266653.1284 (time.time() * 1000)
timestamp1 = int(self._timestamp / 1000) = 1579184266


self._timestamp / 1000.0 = 1579184266.6531284
self._timestamp / 1000.0 - _timestamp1 = 0.6531284
(self._timestamp / 1000.0 - _timestamp1) * 10 ** 9 = 653128400

_timestamp2 = _igtl_nanosec_to_frac(int((self._timestamp / 1000.0 - _timestamp1) * 10 ** 9))

backward:

_igtl_frac_to_nanosec / 10**9




"""


class Roi:

    # TODO: add guards
    def __init__(self, vertexes=(0, 0, 0), size=(0, 0, 0)):
        self.v1 = vertexes[0]
        self.v2 = vertexes[1]
        self.v3 = vertexes[2]

        self.width = size[1]
        self.height = size[0]
        self.depth = size[2]

    def pack(self, fmt):
        b_roi_v1 = struct.pack(fmt, self.v1)
        b_roi_v2 = struct.pack(fmt, self.v2)
        b_roi_v3 = struct.pack(fmt, self.v3)
        b_roi_width = struct.pack(fmt, self.width)
        b_roi_height = struct.pack(fmt, self.height)
        b_roi_depth = struct.pack(fmt, self.depth)

        b_roi = b_roi_v1 + b_roi_v2 + b_roi_v3 + b_roi_width + b_roi_height + b_roi_depth
        return b_roi


class TransformMatrix(object):
    def __init__(self, matrix = None, spacing=None):
        self._matrix = matrix
        self._spacing = spacing

        if self._matrix is None:
            self._matrix = np.identity(4)

        if self._spacing is None:
            self.set_spacing([1, 1, 1])

    def set_spacing(self, spacing):
        self._spacing = spacing

    def pack(self, fmt):
        # first column of the matrix (only first three rows, the last one is always 0, 0, 0, 1)
        m11 = struct.pack(fmt, self._matrix[0, 0] * self._spacing[0])
        m21 = struct.pack(fmt, self._matrix[1, 0] * self._spacing[0])
        m31 = struct.pack(fmt, self._matrix[2, 0] * self._spacing[0])

        # second column of the matrix
        m12 = struct.pack(fmt, self._matrix[0, 1] * self._spacing[1])
        m22 = struct.pack(fmt, self._matrix[1, 1] * self._spacing[1])
        m32 = struct.pack(fmt, self._matrix[2, 1] * self._spacing[1])

        # third column of the matrix
        m13 = struct.pack(fmt, self._matrix[0, 2] * self._spacing[2])
        m23 = struct.pack(fmt, self._matrix[1, 2] * self._spacing[2])
        m33 = struct.pack(fmt, self._matrix[2, 2] * self._spacing[2])

        #TODO: check this carefully
        # fourth column of the matrix - position vector
        m14 = struct.pack(fmt, self._matrix[0, 3])
        m24 = struct.pack(fmt, self._matrix[1, 3])
        m34 = struct.pack(fmt, self._matrix[2, 3])

        binary_matrix = m11 + m21 + m31 + m12 + m22 + m32 + m13 + m23 + m33 + m14 + m24 + m34
        return binary_matrix


class Size3D:
    width = 0
    height = 0
    depth = 0

    def __init__(self, size=(0, 0, 0)):

        if len(size) == 1:
            self.width = size[0]
            self.height = 1
            self.depth = 1

        elif len(size) == 2:
            self.width = size[0]
            self.height = size[1]
            self.depth = 1

        else:
            self.width = size[0]
            self.height = size[1]
            self.depth = size[2]

    def tuple(self):
        return self.width, self.height, self.depth

    def tuple_np(self):
        return self.height, self.width, self.depth

    def pack(self, fmt):
        b_width = struct.pack(fmt, self.width)
        b_height = struct.pack(fmt, self.height)
        b_depth = struct.pack(fmt, self.depth)

        b_size3d = b_width + b_height + b_depth
        return b_size3d