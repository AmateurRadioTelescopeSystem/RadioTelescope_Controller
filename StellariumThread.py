import StellariumDataHandling
from PyQt5 import QtCore


class StellThread(QtCore.QThread):
    # Create the signals to be used for data handling
    conStatSig = QtCore.pyqtSignal(str, name='conStellStat')  # Stellarium connection status indication signal
    dataShowSig = QtCore.pyqtSignal(float, float, name='dataStellShow')  # Coordinates show in the GUI
    sendClientConn = QtCore.pyqtSignal(list, name='clientCommandSendStell')  # Send the command to the radio telescope

    def __init__(self, tcpStell, parent = None):
        super(StellThread, self).__init__(parent)  # Get the parent of the class
        self.tcp = tcpStell  # TCP handling object
        self.dataHandle = StellariumDataHandling.StellariumData()  # Data conversion object

        self.clinetDiscon = True  # Client disconnection indicator
        self.stopExec = False  # Stop thread execution indicator

    def run(self):
        self.stopExec = False  # Initialize it in every thread run to avoid problems
        while not self.stopExec:
            if self.clinetDiscon:
                # Indicate that we are waiting for a connection once we start the program
                self.conStatSig.emit("Waiting")  # Send the signal to indicate that we are waiting for connection

                self.tcp.acceptConnection()  # Wait for a connection to come
                if self.stopExec:
                    break  # Exit immediately after request

                # If we have a connection, then we proceed and indicate that to the user
                self.clinetDiscon = False  # If we reach this point, then we have a connected client
                self.conStatSig.emit("Connected")  # Send the signal to indicate connection

            elif not self.stopExec:
                recData = self.tcp.receive()  # Start receiving the data from the client

                # If we receive zero length data, then that means the connection is broken
                if len(recData) != 0:
                    recData = self.dataHandle.decodeStell(recData)
                    self.dataShowSig.emit(recData[0], recData[1])  # Send the data to be shown on the GUI widget
                    self.sendClientConn.emit(recData)  # Emit the signal to send the data to the raspberry pi
                elif not self.stopExec:
                    self.tcp.releaseClient()  # Close all sockets since client is gone
                    self.clinetDiscon = True  # Tell that the client has disconnected
                    self.stopExec = False  # Continue in the loop since quit is not yet called

    def quit(self):
        self.stopExec = True  # Raise the execution stop flag
        self.clinetDiscon = True  # Indicate a disconnected client
        self.tcp.releaseClient()  # Whenever this function is called we need to close the connection
        self.conStatSig.emit("Disconnected")  # Send the signal to indicate disconnection
