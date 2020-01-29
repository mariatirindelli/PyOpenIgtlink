import unittest
from pyOpenIgtLink import *


class TestHeader(unittest.TestCase):

    # checking the header gets correctly packed and unpacked
    def test_header(self):
        print("Testing OpenIGTLink Header")
        p1 = IGTL_HEADER_VERSION_1  # version number
        p2 = "IMAGE"  # message type
        p3 = "MARIA PC"  # device name
        p4 = 8000000  # timestamp seconds
        p5 = 6000000  # timestamp fractions
        p6 = 10  # body size
        p7 = CRC64(b"")  # crc

        in_header = IgtlHeader()
        in_header.version = p1
        in_header.type = p2
        in_header.devicename = p3
        in_header.timestamp_sec = p4
        in_header.timestamp_frac = p5
        in_header.body_size = p6
        in_header.crc = p7

        binary_header = in_header.pack()

        out_header = IgtlHeader()
        res = out_header.unpack(binary_header)

        self.assertTrue(res)
        self.assertEqual(out_header.version, p1)
        self.assertEqual(out_header.type, p2)
        self.assertEqual(out_header.devicename, p3)
        self.assertEqual(out_header.timestamp_sec, p4)
        self.assertEqual(out_header.timestamp_frac, p5)
        self.assertEqual(out_header.body_size, p6)
        self.assertEqual(out_header.crc, p7)


class TestMessageBase(unittest.TestCase):
    def test_unpack(self):
        print("Testing OpenIGTLink Base Message")
        # unpack must be always called on the header before and on the body in a second time, in order to be
        # sure all the information needed to unpack the body are available. These test check that if the header is not
        # unpacked, the method tries to unpack the header before doing anything else
        p1 = IGTL_HEADER_VERSION_1  # version number
        p2 = "IMAGE"  # message type
        p3 = "MARIA PC"  # device name
        p4 = 8000000  # timestamp seconds
        p5 = 6000000  # timestamp fractions
        p6 = 3  # body size
        p7 = CRC64(b"")  # crc

        in_header = IgtlHeader()
        in_header.version = p1
        in_header.type = p2
        in_header.devicename = p3
        in_header.timestamp_sec = p4
        in_header.timestamp_frac = p5
        in_header.body_size = p6
        in_header.crc = p7

        binary_header = in_header.pack()
        binary_body = b'\x00\x00\x00'

        message = MessageBase()
        message.header = binary_header
        r = message.unpack()
        self.assertEqual(r, UNPACK_HEADER)
        self.assertEqual(message.getHeaderVersion(), p1)
        self.assertEqual(message.getMessageType(), p2)
        self.assertEqual(message.getDeviceName(), p3)
        self.assertEqual(message.getTimeStampSecFrac()[0], p4)
        self.assertEqual(message.getTimeStampSecFrac()[1], p5)
        self.assertEqual(message.getPackBodySize(), p6)

        message.body = binary_body
        r = message.unpack()

        self.assertEqual(r, UNPACK_BODY)
        self.assertEqual(message.getPackSize(), len(binary_header) + len(binary_body), "mismatch in message size")


class TestImageMessage2(unittest.TestCase):

    def test_pack_unpack(self):
        print("Testing image message ")
        raw_img = np.zeros([100, 100], dtype = np.float32)

        img_msg = ImageMessage2()
        img_msg.setData(raw_img)
        img_msg.setSpacing([1, 2, 3])

        mat = np.array([ [1, 0, 0, 4], [0, 1, 0, 2], [0, 0, 1, 6], [0, 0, 0, 1] ])
        img_msg.setMatrix(mat)

        img_msg.pack()

        out_msg = ImageMessage2()
        out_msg.header = img_msg.header
        out_msg.body = img_msg.body

        # unpack header
        self.assertEqual(out_msg.unpack(), UNPACK_HEADER)

        # unpack body
        self.assertEqual(out_msg.unpack(), UNPACK_BODY)

        self.assertEqual(out_msg.getData().shape, (100, 100, 1))
        self.assertEqual(out_msg.getScalarType(), np.uint8)
        self.assertEqual(out_msg.getSpacing(), [1, 2, 3])


class TestCommandMessage(unittest.TestCase):

    def test_pack_unpack(self):
        print("Testing command message")
        cmd_msg = CommandMessage()
        cmd_msg.setCommandId(123)
        cmd_msg.setCommandName("cmdname")

        print("cmd id", cmd_msg.getCommandId())
        print("cmd name", cmd_msg.getCommandName())

        cmd_msg.pack()

        rcv_msg = CommandMessage()
        rcv_msg.header = cmd_msg.header
        rcv_msg.unpack()

        rcv_msg.body = cmd_msg.body
        rcv_msg.unpack()

        print("cmd id", rcv_msg.getCommandId())
        print("cmd name", rcv_msg.getCommandName())

    def test_unpack(self):
        header = b'\x00\x01\x000\x005\x00F\x00F\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        cmd_msg = CommandMessage()
        cmd_msg.header = header

        if cmd_msg.unpack() != UNPACK_HEADER:
            print("whaaat")
        print(cmd_msg.getDeviceName())


class TestStatusMessage(unittest.TestCase):

    def test_pack_unpack(self):
        print("Testing status message")
        status_msg = StatusMessage()
        status_msg.setCode(1)
        status_msg.setSubCode(1)
        status_msg.setErrorName("errorName")

        status_msg.pack()

        rcv_msg = CommandMessage()
        rcv_msg.header = status_msg.header
        rcv_msg.unpack()

        rcv_msg.body = status_msg.body
        rcv_msg.unpack()

        print("Code: ", status_msg.getCode())
        print("Sub Code: ", status_msg.getSubCode())
        print("Error name: ", status_msg.getErrorName())

    def test_unpack(self):
        print("Testing status message - unpack")
        rcv_msg = CommandMessage()
        rcv_msg.header = b'\x00\x01STATUS\x00\x00\x00\x00\x00\x00StreamerSocket\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\xfc\xe4lI~{\x03-'
        a = rcv_msg.unpack()
        print(a)


if __name__ == '__main__':
    unittest.main()