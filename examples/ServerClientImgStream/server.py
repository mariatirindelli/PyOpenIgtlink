import pyOpenIgtLink as igtl
import numpy as np
import time
import matplotlib.pyplot as plt


def main():
    server = igtl.SocketServer()
    server.setAddress(address="127.0.0.1", port=9004)
    server.start()
    server.waitForConnection()

    # Create a simple image
    img = np.zeros([100, 100], dtype = np.uint8)
    img[0:50, :] = 255

    # 1. SEND THE IMAGE MESSAGE TO THE CLIENT

    # Prepare the image message
    img_msg = igtl.ImageMessage2()
    img_msg.setDeviceName("Python IGTL Server")
    img_msg.setTimeStamp(time.time())
    img_msg.setData(img)

    # Pack the message and send it to the openigtl client
    if img_msg.pack():
        print("The image message was correctly packed and it is ready to be sent")
    server.send(img_msg.header + img_msg.body)

    # 2. RECEIVE THE IMAGE MESSAGE FROM THE CLIENT WITH THE MODIFIED IMAGE

    recv_msg = igtl.ImageMessage2()

    # Receive the header
    recv_msg.header = server.receive(recv_msg.getHeaderSize())

    # Unpack the header
    res = recv_msg.unpack()
    if res != igtl.UNPACK_HEADER:
        print("Error while unpacking header")
        return

    # Receive the body
    recv_msg.body = server.receive(recv_msg.getPackBodySize())

    # Unpack the body
    res = recv_msg.unpack()
    if res != igtl.UNPACK_BODY:
        print("Error while unpacking body")
        return

    print("Message Received: \nDevice: {} \nTimestamp: {}".format(recv_msg.getDeviceName(), recv_msg.getTimeStamp()))

    # Finally show the received image
    recv_img = np.squeeze(recv_msg.getData())
    plt.subplot(1, 2, 1)
    plt.imshow(img)
    plt.title("Sent image")

    plt.subplot(1, 2, 2)
    plt.imshow(recv_img)
    plt.title("Received image")
    plt.show()


if __name__ == "__main__":
    main()
