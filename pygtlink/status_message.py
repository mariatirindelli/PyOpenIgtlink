from pygtlink import *
import numpy as np


__all__ = ['StatusMessage']

IGTL_STATUS_HEADER_SIZE = 30


class StatusMessage(MessageBase):
    """
            :ivar int _code: The command code (uint16)
            :ivar int _subCode: The command sub code (int64)
            :ivar str _errorName: The error name (char[20])
            :ivar str _message: The error message (char[BODY_SIZE - 30])
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
        Sets the status code

        :param code: The status code to be set
        """
        if code < 0:
            return
        self._code = int(code)

    def getCode(self):
        """
        Gets the status code

        :returns: The status code
        """
        return self._code

    def setSubCode(self, subCode):
        """
        Sets the status subcode

        :param subCode: The status subcode
        """
        self._subCode = int(subCode)

    def getSubCode(self):
        """
        Gets the status subcode

        :returns: The status subcode
        """
        return self._subCode

    def setErrorName(self, errorName):
        """
        Sets the status error name

        :param errorName: The status error name to be set
        """
        self._errorName = str(errorName)

    def getErrorName(self):
        """
        Gets the status error name

        :returns: The status error name
        """
        return ''.join(self._errorName)

    def setMessage(self, message):
        """
        Sets the status message

        :param message: The status message to be set
        """
        if len(message) > 30:
            return
        self._message = str(message)

    def getMessage(self):
        """
        Gets the status message

        :returns: The status message
        """
        return ''.join(self._message)

    # TODO add message content
    def _packContent(self, endian = ">"):

        # set the command header

        binary_cmd = struct.pack(endian + 'Hq',
                                 self._code,
                                 self._subCode)

        s = bytes(self._errorName.ljust(20), 'ascii')  # Or other appropriate encoding
        binary_cmd += struct.pack(endian + "%ds" % (len(s),), s)

        s = bytes(self._message, 'ascii')  # Or other appropriate encoding
        binary_cmd += struct.pack(endian + "%ds" % (len(s),), s)

        self.body = binary_cmd
        self._bodySize = len(self.body)

    def _unpackContent(self,  endian=">"):

        img_binary_header = self.body[0:IGTL_STATUS_HEADER_SIZE]
        unpacked_header = struct.unpack(endian + 'Hq20s', img_binary_header)

        self._code = unpacked_header[0]
        self._subCode = unpacked_header[1]
        self._errorName = unpacked_header[2].decode('ascii').rstrip()

        b_body = self.body[IGTL_STATUS_HEADER_SIZE::]
        lbody = len(b_body)
        unpacked_body = struct.unpack(endian + str(lbody) + "s", b_body)[0].decode('ascii')
        self._message = unpacked_body
