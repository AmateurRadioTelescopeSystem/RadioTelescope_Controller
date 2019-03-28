import os
import socket

import pytest
from PyQt5 import QtTest, QtNetwork
from Core.Networking import ClientThread
from Core.Configuration import ConfigData


@pytest.fixture(scope="module")
def client_object():
    cfg_data = ConfigData.ConfData(os.path.abspath('Tests/Settings/settings.xml'))
    client_thread = ClientThread.ClientThread(cfg_data)

    server_address = ('127.0.0.1', 10001)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_address)
    sock.settimeout(60)  # Add a timeout timer for 60 seconds
    sock.listen(1)  # Set the socket to listen
    yield client_thread

    sock.close()  # Close the socket on exit


def test_connect_client(client_object):
    client_object.sock = QtNetwork.QTcpSocket()
    client_object.connect_client()
    assert client_object.sock.state() == QtNetwork.QAbstractSocket.ConnectedState
