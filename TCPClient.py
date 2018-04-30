from PyQt5 import QtCore
import logData
import socket


class TCPClient(object):
    def __init__(self, cfgData, mainUi):
        self.logd = logData.logData(__name__)
        self.sock_exst = False  # Indicate that a socket does not object exist
        self.sock_connected = False  # Indicate that there is currently no connection
        self.sock = self.createSocket()  # Create a socket upon the class instantiation
        self.mainUi = mainUi  # Create a variable for the UI control
        self.btnStr = "Disconnect"  # String to hold the TCP connection button message
        autocon = cfgData.getTCPAutoConnStatus()  # See if auto-connection at startup is enabled
        if autocon == "yes":
            self.host = cfgData.getHost()
            self.port = cfgData.getPort()
            if self.connect(self.host, self.port):
                self.logd.log("INFO", "Client successfully connected to %s:%s." % (self.host, self.port), "constructor")
                self.connectButton(False, "Disconnect")
            else:
                self.logd.log("WARNING", "Autoconnection with client was impossible.", "constructor")
                self.connectButton(False, "Connect")


    def createSocket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object
        sock.settimeout(20)  # Set the timeout to 20 seconds
        self.sock_exst = True  # Indicate that a socket object exists
        return sock

    def connect(self, host, port):
        if not self.sock_exst:
            self.sock = self.createSocket()
        try:
            self.sock.connect((host, int(port)))
            self.sock_connected = True
            self.connectButton(False, "Disconnect")
        except (OSError, InterruptedError):
            self.sock_connected = False
            self.connectButton(False, "Connect")
        return self.sock_connected

    def disconnect(self):
        if self.sock_exst and self.sock_connected:
            self.sock.close()
            self.sock_exst = False
            self.sock_connected = False
        else:
            self.sock_exst = False  # A new socket is needed to successfully connect to a server after a lost connection
            self.sock_connected = False  # Indicate a disconnected socket
            self.connectButton(False, "Connect")
        return self.sock_connected

    def sendRequest(self, request):
        if self.sock_connected:
            try:
                self.sock.send(request.encode('utf-8'))
                response = self.sock.recv(1024).decode('utf-8')
                return response
            except (OSError, InterruptedError):
                return "No answer"
        else:
            return "No answer"

    def longWait_rcv(self, time):
        if self.sock_connected:
            self.sock.settimeout(time)  # Set the timeout as the user requests
            try:
                response = self.sock.recv(1024).decode('utf-8')
                self.sock.settimeout(20)  # Reset the socket timeout before exiting
                return response
            except (OSError, InterruptedError):
                self.sock.settimeout(20)  # Reset the socket timeout before exiting
                return "No answer"  # Indicate that nothing was received

    def connectButton(self, actualPress, state = "Connect"):
        if actualPress:
            if self.btnStr == "Disconnect":
                if self.sendRequest("Terminate") == "Bye":
                    self.logd.log("INFO", "Successfully disconnected from server.", "connectButton")
                else:
                    self.logd.log("WARNING",
                                  "There was a problem contacting the server, although the connection was closed.",
                                  "connectButton")
                self.disconnect()  # Close the connection
                self.btnStr = "Connect"
                self.mainUi.connectRadioTBtn.setText(self.btnStr)  # Change user's selection
            elif self.btnStr == "Connect":
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
            if state == "Connect":
                self.btnStr = state
                self.mainUi.connectRadioTBtn.setText(self.btnStr)
                self.mainUi.tcpConRTChkBox.setCheckState(QtCore.Qt.Checked)
            elif state == "Disconnect":
                self.btnStr = state
                self.mainUi.connectRadioTBtn.setText(self.btnStr)
                self.mainUi.tcpConRTChkBox.setCheckState(QtCore.Qt.Unchecked)
