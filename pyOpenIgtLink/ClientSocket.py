import socket
import logging

#  very simple server with 2 socket open: one for data stream and the other for commands

# TODO: check from abc import ABC


class ClientSocket:

    def __init__(self):
        logging.info("Starting Socket Client ... ")
        self._clientSocket = None

    def connectToServer(self, serverAddress, port):
        self._clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._clientSocket.connect( (serverAddress, port) )

    def setTimeout(self, timeout=0):
        if self._clientSocket is not None:
            self._clientSocket.settimeout(timeout)

    def kill(self):
        logging.info("shutting down connection")
        self._clientSocket.shutdown(socket.SHUT_RDWR)
        self._clientSocket.close()

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
        rawData = B''
        while len(rawData) < n:
            packet = s.recv(n - len(rawData))
            if not packet:
                return False, rawData
            rawData += packet
        return True, rawData
