import unittest
from pygtlink import *


class TestStatusMessage(unittest.TestCase):

    def test_pack_unpack(self):
        print("Testing status message")
        status_msg = StatusMessage()
        status_msg.setCode(1)
        status_msg.setSubCode(1)
        status_msg.setErrorName("errorName")
        status_msg.setMessage("Status Message")

        status_msg.pack()

        rcv_msg = StatusMessage()
        rcv_msg.header = status_msg.header
        rcv_msg.unpack()

        rcv_msg.body = status_msg.body
        rcv_msg.unpack()

        print(rcv_msg.getErrorName())
        print(rcv_msg.getMessage())



if __name__ == '__main__':
    unittest.main()