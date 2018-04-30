from PyQt5 import QtCore
import logData
import socket
import struct
import time
import threading
import queue

class TCPStellarium(object):
    def __init__(self, cfgData, mainUi):
        self.logd = logData.logData(__name__)
        self.sock_exst = False  # Indicate that a socket does not object exist
        self.sock_connected = False  # Indicate that there is currently no connection

        self.mainUi = mainUi  # Create a variable for the UI control
        self.btnStr = "Enable"  # String to hold the TCP connection button message
        '''autocon = cfgData.getTCPStellAutoConnStatus()  # See if auto-connection at startup is enabled
        if autocon == "yes":
            self.host = cfgData.getStellHost()
            self.port = cfgData.getStellPort()
            self.sock = self.createSocket()  # Create a socket upon the class instantiation
            if self.acceptConnection()[1]:
                self.logd.log("INFO", "Server successfully started." % (self.host, self.port), "constructor")
                self.connectButton(False, "Disable")
            else:
                self.logd.log("WARNING", "Server auto start failed.", "constructor")
                self.connectButton(False, "Enable")
        else:
            self.connectButton(False, "Enable")
        '''

    def createSocket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket
        sock.bind(("127.0.0.1", int(10002)))  # Bind to the socket
        sock.listen(1)  # Set the listening to one connection
        sock.settimeout(20)  # Set the timeout for the socket
        self.sock_exst = True
        return sock  # Return the socket object

    def acceptConnection(self):
        if not self.sock_exst:
            self.sock = self.createSocket()
        try:
            self.client, claddr = self.sock.accept()
            self.client_connected = True
            return claddr, self.client_connected
        except:
            self.logd.log("EXCEPT", "An exception occurred while waiting for a client to connect", "acceptConnection")
            self.sock.close()
            self.sock_exst = False
            return "", False

    def receive(self):
        if self.client_connected:
            try:
                return self.client.recv(1024).decode('utf-8')
            except ConnectionResetError:
                self.logd.log("EXCEPT", "A connected client abruptly disconnected. Returning to connection waiting", "receive")
                self.client_connected = False
                return ""
        else:
            return ""

    def releaseClient(self):
        if self.client_connected and self.sock_exst:
            self.client.close()  # Detach the client
            self.sock.close()  # Close the connection socket
            self.client_connected = False
            self.sock_exst = False
        else:
            self.client_connected = False
        return self.client_connected

    def sendResponse(self, response):
        if self.client_connected:
            try:
                self.client.send(response.encode('utf-8'))
                return response
            except:
                self.logd.log("EXCEPT", "There was an issue sending the response to the client", "sendResponse")

    def connectButton(self, actualPress, state = "Enable"):
        if actualPress:
            if self.btnStr == "Disable":
                self.releaseClient()
                self.logd.log("INFO", "Successfully disconnected from server.", "connectButton")

                self.btnStr = "Enable"
                self.mainUi.connectStellariumBtn.setText(self.btnStr)  # Change user's selection
            elif self.btnStr == "Enable":
                if self.acceptConnection():
                    self.logd.log("INFO", "Successfully established connection with Stellarium client.", "connectButton")
                    self.btnStr = "Disable"
                    self.mainUi.connectStellariumBtn.setText(self.btnStr)  # Change user's selection
                    self.mainUi.tcpStelServChkBox.setCheckState(QtCore.Qt.Unchecked)
        else:
            if state == "Enable":
                self.btnStr = state
                self.mainUi.connectStellariumBtn.setText(self.btnStr)
                self.mainUi.tcpStelServChkBox.setCheckState(QtCore.Qt.Checked)
            elif state == "Disable":
                self.btnStr = state
                self.mainUi.connectStellariumBtn.setText(self.btnStr)
                self.mainUi.tcpStelServChkBox.setCheckState(QtCore.Qt.Unchecked)


