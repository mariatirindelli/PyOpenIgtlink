from pygtlink import *
import numpy as np

IGTL_SENSOR_HEADER_SIZE = 10


class SensorMessage(MessageBase):
    """
            :ivar int _larray: The sensor array len (uint8)
            :ivar int _status: The status (uint8)
            :ivar int _unit: The unit (uint64)
            :ivar list _data: The sensor data (float64[Larray])
    """

    def __init__(self):
        MessageBase.__init__(self)

        # Setting std header
        self._messageType = "SENSOR"
        self._headerVersion = IGTL_HEADER_VERSION_1

        # setting command header parameters
        self._larray = 3  # uint8
        self._status = 0  # uint8
        self._unit = 0  # uint64
        self._data = []  # float64[Larray]

    def setLength(self, length):
        """Sets sensor data length (num elements)

        :param length: The array or list of spacing values
        """
        self._larray = length

    def getLength(self):
        """Gets sensor data length (num elements)

        :returns: The sensor data length
        """

        return self._larray

    def setData(self, data):
        """Sets sensor data

        :param data: The list or array of sensor data
        """
        if isinstance(data, np.ndarray):
            data = data.tolist()
        self._data = data

    def getData(self):
        """Gets sensor data

        :returns: The sensor data
        """
        return self._data

    def setUnit(self, unit):
        """Sets unit

        :param unit: The sensor data unit to be set (must be an int)
        """
        if isinstance(unit, int) and unit > 0:
            self._unit = unit

    def getUnit(self):
        """Gets sensor data unit

        :returns: The sensor data unit
        """
        return self._unit

    def setStatus(self, status):
        """Sets status

        :param status: The status to be set
        """
        if isinstance(status, int) and status > 0:
            self._status = status

    def getStatus(self):
        """Gets sensor status

        :returns: The sensor status
        """
        return self._status

    def _packContent(self, endian=">"):

        b_body_header = struct.pack(endian + 'BBQ', self._larray, self._status, self._unit)
        b_data = struct.pack(endian + 'd' * len(self._data), *self._data)
        self.body = b_body_header + b_data

        self._bodySize = len(self.body)

    def _unpackContent(self,  endian=">"):

        b_body_header = self.body[0:IGTL_SENSOR_HEADER_SIZE]
        unpacked_body_header = struct.unpack(endian + 'BBQ', b_body_header)

        self._larray = unpacked_body_header[0]
        self._status = unpacked_body_header[1]
        self._unit = unpacked_body_header[2]

        b_body = self.body[IGTL_SENSOR_HEADER_SIZE::]
        unpacked_body = struct.unpack(endian + str(self._larray) + "d", b_body)
        data_list = list()
        data_list.append(unpacked_body)
        self._data = np.array(data_list).flatten()
