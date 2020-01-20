import socket
import logging

#  very simple server with 2 socket open: one for data stream and the other for commands

# TODO: check from abc import ABC


class SocketServer:

    def __init__(self):
        logging.info("Starting Socket Server ... ")
        self._serverSocket = None
        self._clientSocket = None
        self._serverAddress = ""
        self._serverPort = None

    def setAddress(self, address, port):
        self._serverAddress = address
        self._serverPort = port

    def setTimeout(self, timeout=0):
        if self._clientSocket is not None:
            self._clientSocket.settimeout(timeout)

    def start(self):

        self._serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._serverSocket.bind((self._serverAddress, self._serverPort))

    def waitForConnection(self):
        self._serverSocket.listen(1)
        self._clientSocket, client_data_address = self._serverSocket.accept()
        logging.info("Connection established at ip:{}".format(client_data_address))

    def kill(self):
        logging.info("shutting down connection")
        self._clientSocket.shutdown(socket.SHUT_RDWR)
        self._clientSocket.close()

        self._serverSocket.shutdown(socket.SHUT_RDWR)
        self._serverSocket.close()

    def receive(self, length):
        res, recData = self._recvall(self._clientSocket, length)
        if not res:
            return None
        return recData

    def send(self, data):
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