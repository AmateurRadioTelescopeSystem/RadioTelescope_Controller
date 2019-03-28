import os
import socket
import unittest
from PyQt5 import QtTest, QtNetwork
from Core.Networking import ClientThread
from Core.Configuration import ConfigData


class TestTCPClientThread(unittest.TestCase):
    def setUp(self) -> None:
        cfg_data = ConfigData.ConfData(os.path.abspath('Tests/Settings/settings.xml'))
        self.client_thread = ClientThread.ClientThread(cfg_data)

        server_address = ('127.0.0.1', 10001)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(server_address)
        self.sock.settimeout(60)  # Add a timeout timer for 60 seconds
        self.sock.listen(1)  # Set the socket to listen

    def tearDown(self) -> None:
        self.sock.close()

    def test_connect_client(self):
        self.client_thread.sock = QtNetwork.QTcpSocket()
        self.client_thread.connect_client()
        self.assertTrue(self.client_thread.sock.state() == QtNetwork.QAbstractSocket.ConnectedState,
                        "Unable to connect to server.")
