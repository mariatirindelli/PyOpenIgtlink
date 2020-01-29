from pyOpenIgtLink import *

IGTL_STATUS_HEADER_SIZE = 30


class StatusMessage(MessageBase):
    """
            :ivar _code The command code (uint16)
            :ivar _subCode The command sub code (int64)
            :ivar _errorName The error name (char[20])
            :ivar _message The error message (char[BODY_SIZE - 30])
    """

    def __init__(self):
        MessageBase.__init__(self)

        # Setting std header
        self._messageType = "STATUS"
        self._headerVersion = IGTL_HEADER_VERSION_1

        # setting command header parameters
        self._code = 0  # uint16
        self._subCode = 0  # int 64
        self._errorName = ""  # char[20]
        self._message = ""  # TODO: implement message

    def setCode(self, code):
        """
        Sets the code
        :param code: The code
        """
        if code < 0:
            return
        self._code = int(code)

    def getCode(self):
        """
        Gets the code
        :return: The code
        """
        return self._code

    def setSubCode(self, subCode):
        """
        Sets the subcode
        :param subCode: The subcode
        """
        self._subCode = int(subCode)

    def getSubCode(self):
        """
        Gets the code
        :return: The code
        """
        return self._subCode

    def setErrorName(self, errorName):
        """
        Sets the error name
        :param errorName: The error name
        """
        self._errorName = str(errorName)

    def getErrorName(self):
        """
        Gets the command name
        :return: The command name
        """
        return self._errorName

    def _packContent(self, endian = ">"):

        # set the command header

        binary_cmd = struct.pack(endian + 'Hq20s',
                                 self._code,
                                 self._subCode,
                                 self._errorName.encode('utf-8'))

        self.body = binary_cmd
        self._bodySize = len(self.body)

    def _unpackContent(self,  endian = ">"):

        img_binary_header = self.body[0:IGTL_STATUS_HEADER_SIZE]
        unpacked_header = struct.unpack(endian + 'Hq20s', img_binary_header)

        self._code = unpacked_header[0]
        self._subCode = unpacked_header[1]
        self._errorName = unpacked_header[2].decode('utf-8').strip('\x00')