from pyOpenIgtLink import *

# Unpack status. They are returned by the Unpack() function.

UNPACK_UNDEF = 1,
UNPACK_HEADER = 2,
UNPACK_BODY = 3


class MessageBase(object):
    """
        Description for class

        :ivar _messageSize The size of the message
        :ivar _header: A pointer to the byte array for the serialized header. To prevent large
        copy of the byte array in the Pack() function, header byte array is concatenated to the byte array for the body.
                in cpp : unsigned char* m_Header;

        :ivar _body:A pointer to the byte array for the serialized body. To prevent large copy of the byte array in
        the Pack() function, header byte array is concatenated to the byte array for the header.
                in cpp : unsigned char* m_Body;

        :ivar _content:A pointer to the underlying content of a message
                in cpp : unsigned char* m_Body;

        :ivar _bodySize:The size of the body to be read. This function must be called after the message header is set.
                in cpp :an int

        :ivar _messageType:The message type

        :ivar _headerVersion : An unsigned short for the message format version
                in cpp :a unsigned short

        :ivar _deviceName : A character string for the device name (message name).
                in cpp :a string

        :ivar _timeStampSec : A time stamp (second) for message creation. It consists of fields for seconds
        (m_TimeStampSec)and fractions of a second (m_TimeStampSecFraction).
                in cpp :a unsigned int

        :ivar _timeStampFraction : A time stamp (second) for message creation. It consists of fields for seconds
        (m_TimeStampSec)and fractions of a second (m_TimeStampSecFraction).
                in cpp :a unsigned int

        :ivar _isHeaderUnpacked : Unpacking (deserialization) status for the header
                in cpp :a bool

        :ivar _isBodyUnpacked : Unpacking (deserialization) status for the body
                in cpp :a bool

        :ivar _isBodyPacked : Packing (deserialization) status for the body
                in cpp :a bool
        """

    def __init__(self):
        self.header = None  # binary header
        self.body = None  # binary body

        self._messageSize = 0
        self._content = None  # for some messages it makes sense also to have the content variable - not for the easiest
        self._bodySize = 0
        self._messageType = ""
        self._headerVersion = IGTL_HEADER_VERSION
        self._deviceName = ""
        self._timeStampSec = 0
        self._timeStampFraction = 0
        self._receivedBodyCrc = 0
        self._isHeaderUnpacked = False
        self._isBodyUnpacked = False
        self._isBodyPacked = False

    # TODO: implement for OpenIGTLink_HEADER_VERSION >= 2

    def setHeaderVersion(self, header_version):
        """Sets the message version number"""

        self._headerVersion = int(header_version)
        self._isBodyPacked = False

    def getHeaderVersion(self):
        """Gets the message version number"""
        return self._headerVersion

    def setDeviceName(self, device_name):
        """Sets the device name"""
        self._deviceName = str(device_name)
        self._isBodyPacked = False

    def setMessageType(self, msg_type):
        """Sets the device (message) type"""
        self._messageType = str(msg_type)
        self._isBodyPacked = False

    def getDeviceName(self):
        """Gets the device name"""
        return self._deviceName

    def getMessageType(self):
        """Gets the device type"""
        return self._messageType

    # TODO: implement for OpenIGTLink_HEADER_VERSION >= 2

    def setTimeStamp(self, timestamp):
        """Sets the message timestamp
        :param timestamp timestamp in seconds since the epoch as a floating point number. The epoch is the point where
         the time starts, and is platform dependent. For Unix, the epoch is January 1, 1970, 00:00:00 (UTC).
         To find out what the epoch is on a given platform, look at time.gmtime(0). Can be obtained using the python
         function time.time() from the time module
         """
        self._timeStampSec = int(timestamp)
        self._timeStampFraction = igtl_nanosec_to_frac(int((timestamp - self._timeStampSec) * 10 ** 9))

    def getTimeStamp(self):
        """Gets the message timestamp
        :return The timestamp in seconds since the epoch as a floating point number. The epoch is the point where
         the time starts, and is platform dependent. For Unix, the epoch is January 1, 1970, 00:00:00 (UTC).
         To find out what the epoch is on a given platform, look at time.gmtime(0).
        """
        timestamp = (float(self._timeStampSec) + float(igtl_frac_to_nanosec(self._timeStampFraction)) / 10 ** 9)
        return timestamp

    def getTimeStampSecFrac(self):
        """Gets the message timestamp
        :return The timestamp expressed in second and fraction
        """
        return self._timeStampSec, self._timeStampFraction

    def pack(self):
        """serializes the header and body based on the member variables.
            PackContent() must be implemented in the child class.

            :return 0 in case of error, 1 if the message was successfully packed
            """

        if self._isBodyPacked:
            return 1

        # if no message type is indicated, returns with error message
        if len(self._messageType) == 0:
            return 0

        self._packContent()
        self._isBodyPacked = True

        header = IgtlHeader()
        header.version = self._headerVersion
        header.timestamp_sec = self._timeStampSec
        header.timestamp_frac = self._timeStampFraction
        header.body_size = self.getPackBodySize()
        header.crc = CRC64(self.body)  # TODO: check this crc
        header.type = self._messageType
        header.devicename = self._deviceName

        self.header = header.pack()
        self._messageSize = len(self.header) + len(self.body)
        return 1

    def unpack(self, crccheck = 0):
        """Unpack() deserializes the header and/or body, extracting data from
        the byte stream. If the header has already been deserialized, Unpack()
        deserializes only the body part. UnpackBody() must be implemented to
        deserialize the body part. Unpack() performs 64-bit CRC check,
        when crccheck = 1. It returns (an int):

        UNPACK_UNDEF             : Nothing deserialized
        UNPACK_HEADER            : The header has been deserialized.
        UNPACK_BODY              : The body has been deserialized.
                                    If CRC check fails, Unpack() doesn't deserialize the body, thus it doesn't
                                    return UNPACK_BODY flag.
        UNPACK_HEADER|UNPACK_BODY: Both the header and body have been deserialized"""

        r = UNPACK_UNDEF
        if self.header is not None and not self._isHeaderUnpacked:
            self.initBuffer() # if I call the unpack on the received header, it reinit the buffer -> it won't read
            # the body, I have to get the body and re-unpack to have the body as well - done to follow the c++ structure
            r = self._unpackHeader()
            return r

        if self.getPackBodySize() <= 0 or self._isBodyUnpacked:
            return r

        r = self._unpackBody(crccheck, r)

        return r

    @staticmethod
    def getHeaderSize():
        return IGTL_HEADER_SIZE

    #TODO: THINK ABOUT THOSE
    def getPackSize(self):
        """Gets the size of the serialized message data"""
        return self._messageSize

    def getPackBodySize(self):
        """Gets the size of the serialized body data"""
        return self._bodySize

    def getBodySizeToRead(self):
        """
        returns the size of the body to be read. This function must be called after the message header is set.
        /:return an int"""
        return self._bodySize

    def initBuffer(self):
        self._isHeaderUnpacked = False
        self._isBodyPacked = False
        self._isBodyUnpacked = False
        self._bodySize = 0
        self._deviceName = ""
        self._messageType = ""

    # PROTECTED FUNCTIONS

    def _unpackHeader(self):
        """
        Unpack the first 58 bytes 
        /:return r the status of the unpack operation""" # TODO: check it

        unpacked_header = IgtlHeader()

        # unpack the binary header
        if not unpacked_header.unpack(self.header):
            self._isHeaderUnpacked = False
            return UNPACK_UNDEF

        self._headerVersion = unpacked_header.version
        self._messageType = unpacked_header.type
        self._deviceName = unpacked_header.devicename
        self._timeStampSec = unpacked_header.timestamp_sec
        self._timeStampFraction = unpacked_header.timestamp_frac
        self._bodySize = unpacked_header.body_size
        self._receivedBodyCrc = unpacked_header.crc

        self._messageSize = self.getHeaderSize() + self._bodySize

        self._isHeaderUnpacked = True
        return UNPACK_HEADER

    def _unpackBody(self, crccheck, r):
        """
        Unpack the body (no idea what r is but is a int - int& r, crccheck is the crc to check)
        If it's a v3 message, body is ext header + content + metadataheader + metadata<optional>
        /:return r the status of the unpack operation""" # TODO: check it
        if self.body is None:
            self._isBodyUnpacked = False
            return r

        if self._bodySize != len(self.body):
            self._isBodyUnpacked = False
            return r

        if crccheck:
            # Calculate CRC of the body
            crc = CRC64(self.body)
        else:
            crc = self._receivedBodyCrc

        if not crc == self._receivedBodyCrc:
            self._isBodyUnpacked = False
            return

        # deserialize the body
        self._unpackContent()
        self._isBodyUnpacked = True
        self._isBodyPacked = False

        return UNPACK_BODY

    def _packContent(self):
        """
        Packs (serialize) the content. Must be implemented in all child classes
        /:return an int"""
        return 0

    def _unpackContent(self):
        """
        Unpacks (deserialize) the content. Must be implemented in all child classes.
        /:return an int"""
        return 0

    #TODO: maybe not needed
    def _calculateContentBufferSize(self):
        """
        Gets the size of the serialized content
        /:return an int"""
        return 0
