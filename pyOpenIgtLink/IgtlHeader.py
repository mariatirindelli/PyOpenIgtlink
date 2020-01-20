from pyOpenIgtLink import *

IGTL_HEADER_VERSION = 1
IGTL_HEADER_SIZE = 58


class IgtlHeader(object):
    def __init__(self):
        self.version = IGTL_HEADER_VERSION  # version number
        self.type = ""
        self.devicename = ""
        self.timestamp_sec = 0
        self.timestamp_frac = 0
        self.body_size = 0  # the size of the binary body pack
        self.crc = CRC64(b"")

    def pack(self, endian=">"):

        return struct.pack(endian + 'H12s20sIIQQ',
                               self.version,
                               self.type.encode('utf-8'),
                               self.devicename.encode('utf-8'),
                               self.timestamp_sec,
                               self.timestamp_frac,
                               self.body_size,
                               self.crc)

    # TODO: add check on header length
    def unpack(self, binary_header, endian=">"):
        if len(binary_header) != IGTL_HEADER_SIZE:
            return False

        unpacked_header = struct.unpack(endian + 'H12s20sIIQQ', binary_header)

        self.version = unpacked_header[0]
        self.type = unpacked_header[1].decode('utf-8').strip('\x00')
        self.devicename = unpacked_header[2].decode('utf-8').strip('\x00')
        self.timestamp_sec = unpacked_header[3]
        self.timestamp_frac = unpacked_header[4]
        self.body_size = unpacked_header[5]
        self.crc = unpacked_header[6]
        return True
