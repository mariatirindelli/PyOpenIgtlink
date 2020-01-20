import pyOpenIgtLink as igtl
import time
import matplotlib.pyplot as plt

SERVER_ADDRESS = "127.0.0.1"
PORT = 5001


def main():
    client = igtl.ClientSocket()
    client.connectToServer(SERVER_ADDRESS, PORT)

    # 1. RECEIVE THE IMAGE MESSAGE FROM THE CLIENT WITH THE MODIFIED IMAGE

    recv_msg = igtl.ImageMessage2()

    # Receive the header
    recv_msg.header = client.receive(recv_msg.getHeaderSize())

    # Unpack the header
    res = recv_msg.unpack()
    if res != igtl.UNPACK_HEADER:
        print("Error while unpacking header")
        return

    # Receive the body
    recv_msg.body = client.receive(recv_msg.getPackBodySize())

    # Unpack the body
    res = recv_msg.unpack()
    if res != igtl.UNPACK_BODY:
        print("Error while unpacking body")
        return

    print("Message Received: \nDevice: {} \nTimestamp: {}".format(recv_msg.getDeviceName(), recv_msg.getTimeStamp()))

    # receive the image data and copy the data
    recv_img = recv_msg.getData()
    img_copy = recv_img.copy()

    # invert the image values
    img_copy[recv_img == 0] = 255
    img_copy[recv_img == 255] = 0

    # 2. Change the device name, timestamp and data
    recv_msg.setDeviceName("IGTL Client")
    recv_msg.setTimeStamp(time.time())
    recv_msg.setData(img_copy)

    # pack the modified message
    recv_msg.pack()

    # send the message
    client.send(recv_msg.header + recv_msg.body)


if __name__ == "__main__":
    main()
