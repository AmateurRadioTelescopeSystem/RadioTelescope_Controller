from PyQt5 import QtCore
import logData
import socket


class TCPClient(QtCore.QObject):
    def __init__(self, cfgData, mainUi):
        super(TCPClient, self).__init__()
        self.logd = logData.logData(__name__)
        self.cfgData = cfgData
        self.sock_exst = False  # Indicate that a socket does not object exist
        self.sock_connected = False  # Indicate that there is currently no connection
        self.threadSendReq = False
        self.threadData = ""
        self.stopExec = False
        self.mainUi = mainUi  # Create a variable for the UI control

    def createSocket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object
        #sock.settimeout(20)  # Set the timeout to 20 seconds
        self.sock_exst = True  # Indicate that a socket object exists
        return sock

    def connect(self):
        host = self.cfgData.getHost()
        port = self.cfgData.getPort()
        if not self.sock_exst:
            self.sock = self.createSocket()
        try:
            self.sock.connect((host, int(port)))
            self.sock_connected = True
        except (OSError, InterruptedError):
            self.sock_connected = False
        return self.sock_connected

    def closeConnection(self):
        if self.sock_exst or self.sock_connected:
            self.sock.close()
            self.sock_exst = False
            self.sock_connected = False
        else:
            self.sock_exst = False  # A new socket is needed to successfully connect to a server after a lost connection
            self.sock_connected = False  # Indicate a disconnected socket
        return self.sock_connected

    def sendRequest(self, request: str):
        if self.sock_connected:
            try:
                self.sock.send(request.encode('utf-8'))
                response = self.sock.recv(1024).decode('utf-8')
                return response
            except (OSError, InterruptedError, ConnectionResetError):
                return "No answer"
        else:
            return "No answer"

    def connectButtonR(self, thread=None):
        if self.sock_exst or self.sock_connected:
            self.stopExec = True  # If there is currently a socket, then the call is to terminate it
        else:
            self.stopExec = False  # If there is no socket, then the call is for its creation
        if not thread.isRunning():
            thread.start()  # Start the thread with the current conditions

    @QtCore.pyqtSlot(list, name='clientCommandSendStell')
    def stellCommSend(self, radec: list, thread=None):
        if thread is not None:
            if self.mainUi.stellariumOperationSelect.currentText() == "Transit":
                self.threadData = "TRNST_RA_%.5f_DEC_%.5f" % (radec[0], radec[1])
                self.threadSendReq = True
            elif self.mainUi.stellariumOperationSelect.currentText() == "Aim and track":
                self.threadData = "TRK %f %f" % (radec[0], radec[1])
                self.threadSendReq = True

            if not thread.isRunning():
                thread.start()  # Start the thread with the current conditions

    @QtCore.pyqtSlot(name='stopRadioTele')
    def stopMovingRT(self, thread=None):
        self.threadData = "STOP"
        self.threadSendReq = True
        if not thread.isRunning():
            thread.start()  # Start the thread with the current conditions
