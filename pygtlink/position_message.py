from pygtlink import *

__all__ = ['PositionMessage']

IGTL_STATUS_HEADER_SIZE = 30

# TODO: add documentation


class PositionMessage(MessageBase):
    """
        The class implements the openIgtLink position message

        :ivar float _x: The x component of the position
        :ivar float _y: The y component of the position
        :ivar float _z: The z component of the position
        :ivar float _ox: The first component of the orientation quaternion
        :ivar float _oy: The second component of the orientation quaternion
        :ivar float _oz: The third component of the orientation quaternion
        :ivar float _w: The fourth component of the orientation quaternion
    """

    def __init__(self):
        MessageBase.__init__(self)

        # Setting std header
        self._messageType = "POSITION"
        self._headerVersion = IGTL_HEADER_VERSION_1

        # setting command header parameters
        self._x = 0  # float32
        self._y = 0  # float32
        self._z = 0  # float32
        self._ox = 0  # float32
        self._oy = 0   # float32
        self._oz = 0   # float32
        self._w = 0  # float32

    def setPosition(self, pos):
        """
        Sets the position

        :param pos: The position to be set. It can be a 3-element list or nd.array
        """
        if len(pos) != 3:
            return
        self._x = float(pos[0])
        self._y = float(pos[1])
        self._z = float(pos[2])

    def setQuaternion(self, quat):
        """
        Sets the quaternion

        :param quat: The quaternion to be set. It can be a 4-element list or nd.array
        """
        if len(quat) != 4:
            return
        self._ox = float(quat[0])
        self._oy = float(quat[1])
        self._oz = float(quat[2])
        self._w = float(quat[3])

    def getPosition(self):
        """
        Gets the position

        :returns: The position as a list [x, y, z]
        """
        return [self._x, self._y, self._z]

    def getQuaternion(self):
        """
        Sets the quaternion

        :returns: The quaternion as a list [ox, oy, oz, w]
        """
        return [self._ox, self._oy, self._oz, self._w]

    def _packContent(self, endian=">"):

        # set the command header

        self.body = struct.pack(endian + '7f',
                                 self._x,
                                 self._y,
                                 self._z,
                                 self._ox,
                                 self._oy,
                                 self._oz,
                                 self._w)

        self._bodySize = len(self.body)

    def _unpackContent(self,  endian=">"):

        img_binary_header = self.body[0:IGTL_STATUS_HEADER_SIZE]
        unpacked_header = struct.unpack(endian + '7f', img_binary_header)

        self._x = unpacked_header[0]
        self._y = unpacked_header[1]
        self._z = unpacked_header[2]
        self._ox = unpacked_header[3]
        self._oy = unpacked_header[4]
        self._oz = unpacked_header[5]
        self._w = unpacked_header[6]
