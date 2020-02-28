import socket
import logging
#  very simple server with 2 socket open: one for data stream and the other for commands

# TODO: check from abc import ABC


class ClientSocket:
    """
        Implementation of IGTL client

        :ivar socket.socket _clientSocket: The client TCP socket
    """

    def __init__(self):
        logging.info("Starting Socket Client ... ")
        self._clientSocket = None

    def connectToServer(self, serverAddress, port):
        """Connects to the IGTL server

            :param str serverAddress: Server Address
            :param int port: Server Port
        """
        self._clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._clientSocket.connect((serverAddress, port))

    def setTimeout(self, timeout=0):
        """Sets receive timeout

            :param int timeout: The receive timeout to be set
        """
        if self._clientSocket is not None:
            self._clientSocket.settimeout(timeout)

    def kill(self):
        """Shut down the connection and closes the socket
        """
        logging.info("shutting down connection")
        self._clientSocket.shutdown(socket.SHUT_RDWR)
        self._clientSocket.close()

    def receive(self, length):
        """Receives a message of <length> bytes from the IGTL server

            :param int length: The length of the message to be received

            :returns: The received message (a byte string)
        """
        res, recData = self._recvall(self._clientSocket, length)
        if not res:
            return None
        return recData

    def send(self, data):
        """Sends data to the IGTL server

            :param data: the message to be sent (as a byte string)
        """
        self._clientSocket.sendall(data)

    @staticmethod
    def _recvall(s, n):
        # Helper function to recv n bytes or return None if EOF is hit
        rawData = B''
        while len(rawData) < n:
            packet = s.recv(n - len(rawData))
            if not packet:
                return False, rawData
            rawData += packet
        return True, rawData
