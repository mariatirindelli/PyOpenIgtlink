import socket
import logging

#  very simple server with 2 socket open: one for data stream and the other for commands

# TODO: check from abc import ABC


class SocketServer:
    """
        Implementation of IGTL Server

        :ivar socket.socket _serverSocket: The server TCP socket listening for incoming connection
        :ivar socket.socket _clientSocket: The TCP socket the server opens with the client when a connection request
            is received over the _serverSocket
        :ivar str _serverAddress: The server address
        :ivar int _serverPort: The server port
    """

    def __init__(self):
        logging.info("Starting Socket Server ... ")
        self._serverSocket = None
        self._clientSocket = None
        self._serverAddress = ""
        self._serverPort = None

    def setAddress(self, address, port):
        """Sets the Server address and port

            :param str address: The server address to be set
            :param int port: The server port to be set
        """
        self._serverAddress = address
        self._serverPort = port

    def setTimeout(self, timeout=0):
        """Sets receive timeout

            :param int timeout: The receive timeout to be set
        """
        if self._clientSocket is not None:
            self._clientSocket.settimeout(timeout)

    def start(self):
        """Creates the server socket and binds it with the server address set with
            :func:`~pygtlink.SocketServer.setAddress`
        """

        self._serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._serverSocket.bind((self._serverAddress, self._serverPort))

    def waitForConnection(self):
        """Waits for a connection request to be sent from the client
        """
        self._serverSocket.listen(1)
        self._clientSocket, client_data_address = self._serverSocket.accept()
        logging.info("Connection established at ip:{}".format(client_data_address))

    def kill(self):
        """Shut down the socket connection with the client and closes the server socket
        """
        logging.info("shutting down connection")
        self._clientSocket.shutdown(socket.SHUT_RDWR)
        self._clientSocket.close()

        self._serverSocket.shutdown(socket.SHUT_RDWR)
        self._serverSocket.close()

    def receive(self, length):
        """Receives a message of <length> bytes from the IGTL client

            :param int length: The length of the message to be received

            :returns: The received message (a byte string)
        """
        res, recData = self._recvall(self._clientSocket, length)
        if not res:
            return None
        return recData

    def send(self, data):
        """Sends data to the IGTL client

            :param data: the message to be sent (as a byte string)
        """
        self._clientSocket.sendall(data)

    @staticmethod
    def _recvall(s, n):
        # Helper function to recv n bytes or return None if EOF is hit
        raw_data = B''
        while len(raw_data) < n:
            packet = s.recv(n - len(raw_data))
            if not packet:
                return False, raw_data
            raw_data += packet
        return True, raw_data