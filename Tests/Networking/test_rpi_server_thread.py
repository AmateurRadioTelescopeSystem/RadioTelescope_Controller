import os
import sys
import socket

import pytest
from PyQt5 import QtTest, QtNetwork, QtCore
from Core.Networking import RPiServerThread
from Core.Configuration import ConfigData


@pytest.fixture(scope="module")
def server_object():
    cfg_data = ConfigData.ConfData(os.path.abspath('Tests/Settings/settings.xml'))
    server_thread = RPiServerThread.RPiServerThread(cfg_data)
    server_thread.connect_server()

    return server_thread


def test_connect_client(server_object):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(10.0)

        #sock.connect(('localhost', 10003))
        #QtTest.QTest.qWait(5)
        #server_object._new_connection()

        #assert server_object.socket.state() == QtNetwork.QAbstractSocket.ConnectedState
