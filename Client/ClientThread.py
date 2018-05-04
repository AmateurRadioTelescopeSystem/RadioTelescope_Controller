from PyQt5 import QtCore
from Client import TCPClient


class ClientThread(QtCore.QThread):
    # Create the signals to be used for data handling
    conStatSig = QtCore.pyqtSignal(str, name='conClientStat')  # Connection indication signal
    dataRcvSigC = QtCore.pyqtSignal(str, name='dataClientRX')  # Send the received data out

    def __init__(self, cfgData, ui, parent = None):
        super(ClientThread, self).__init__(parent)  # Get the parent of the class
        self.tcp = TCPClient.TCPClient(cfgData, ui)  # TCP handling object

    def run(self):
        if not self.tcp.sock_exst:
            # Indicate that we are waiting for a connection once we start the program
            self.conStatSig.emit("Connecting")  # Send the signal to indicate that we are waiting for connection
            self.tcp.connect()  # Try to connect to the server

            if self.tcp.sock_connected:
                # If we have a connection, then we proceed and indicate that to the user
                self.conStatSig.emit("Connected")  # Send the signal to indicate connection
        elif not self.tcp.stopExec and self.tcp.sock_exst and self.tcp.threadSendReq and self.tcp.sock_connected:
            recData = self.tcp.sendRequest(self.tcp.threadData)  # Send the request to the server
            self.tcp.threadSendReq = False  # Reset the data reception flag

            # If we receive zero length data, then that means the connection is broken
            if len(recData) != 0:
                self.dataRcvSigC.emit(recData)  # Send the data to be shown on the GUI widget
        elif self.tcp.stopExec:
            self.tcp.stopExec = False  # Reset the stopping flag
            self.tcp.closeConnection()  # Close all sockets since client is gone
            self.conStatSig.emit("Disconnected")  # Send the signal to indicate disconnectionS

    def connectButtonR(self):
        if self.tcp.sock_exst or self.tcp.sock_connected:
            self.tcp.stopExec = True  # If there is currently a socket, then the call is to terminate it
        else:
            self.tcp.stopExec = False  # If there is no socket, then the call is for its creation
        if not self.isRunning():
            self.start()  # Start the thread with the current conditions
