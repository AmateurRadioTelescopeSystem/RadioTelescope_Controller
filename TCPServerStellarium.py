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
        self.sock = self.createSocket()  # Create a socket upon the class instantiation
        self.mainUi = mainUi  # Create a variable for the UI control
        self.btnStr = "Disconnect"  # String to hold the TCP connection button message
        '''autocon = cfgData.getTCPAutoConnStatus()  # See if auto-connection at startup is enabled
        if autocon == "yes":
            self.host = cfgData.getHost()
            self.port = cfgData.getPort()
            if self.connect(self.host, self.port):
                self.logd.log("INFO", "Client successfully connected to %s:%s." % (self.host, self.port), "constructor")
                self.connectButton(False, "Disconnect")
            else:
                self.logd.log("WARNING", "Autoconnection with client was impossible.", "constructor")
                self.connectButton(False, "Connect")
        '''

    def createSocket(self):
        # Get hostname of the current machine
        sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sck.connect(("8.8.8.8", 80))
        hostname = sck.getsockname()[0]  # Get the local IP returned
        sck.close()  # Release the socket created for getting the local IP

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket
        sock.bind((hostname, int(self.port)))  # Bind to the socket
        sock.listen(1)  # Set the listening to one connection
        return sock  # Return the socket object

    def acceptConnection(self):
        try:
            self.client, claddr = self.sock.accept()
            self.client_connected = True
            return claddr, self.client_connected
        except:
            self.logd.log("EXCEPT", "An exception occurred while waiting for a client to connect", "acceptConnection")
            self.sock.close()
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
        if self.client_connected:
            self.client.close()
            self.client_connected = False
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

    def connectButton(self, actualPress, state = "Connect"):
        if actualPress:
            if self.btnStr == "Disable":
                self.releaseClient()  # Close the connection
                self.logd.log("INFO", "Successfully disconnected from server.", "connectButton")

                self.btnStr = "Enable"
                self.mainUi.connectRadioTBtn.setText(self.btnStr)  # Change user's selection
            elif self.btnStr == "Enable":
                if self.connect(self.host, self.port):
                    self.logd.log("INFO", "Client successfully connected to %s:%s." % (self.host, self.port), "connectButton")
                    self.btnStr = "Disconnect"
                    self.mainUi.connectRadioTBtn.setText(self.btnStr)
                    self.mainUi.tcpConRTChkBox.toggle()
                    self.mainUi.tcpConRTChkBox.setCheckState(QtCore.Qt.Unchecked)
                else:
                    self.logd.log("WARNING", "Problem establishing connection with %s:%s." % (self.host, self.port), "connectButton")
                    self.btnStr = "Connect"
                    self.mainUi.connectRadioTBtn.setText(self.btnStr)
        else:
            if state == "Enable":
                self.btnStr = state
                self.mainUi.connectRadioTBtn.setText(self.btnStr)
                self.mainUi.tcpConRTChkBox.setCheckState(QtCore.Qt.Checked)
            elif state == "Disable":
                self.btnStr = state
                self.mainUi.connectRadioTBtn.setText(self.btnStr)
                self.mainUi.tcpConRTChkBox.setCheckState(QtCore.Qt.Unchecked)


