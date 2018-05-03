from Server import TCPServerRPi
from PyQt5 import QtCore
import logData


class RPiServerThread(QtCore.QThread):
    # Create the signals to be used for data handling
    conStatSigR = QtCore.pyqtSignal(str, name='conRPiStat')  # Raspberry pi connection indicator
    #dataShowSig = QtCore.pyqtSignal(float, float, name='dataStellShow')  # Coordinates show in the GUI
    #sendClientConn = QtCore.pyqtSignal(list, name='clientCommandSendStell')  # Send the command to the radio telescope

    def __init__(self, cfgData, parent = None):
        super(RPiServerThread, self).__init__(parent)  # Get the parent of the class
        self.tcp = TCPServerRPi.TCPServerRpi(cfgData)  # TCP handling object
        self.logD = logData.logData(__name__)  # Create the logger

        self.clinetDiscon = True  # Client disconnection indicator
        self.stopExec = False  # Stop thread execution indicator

    def run(self):
        self.stopExec = False  # Initialize it in every thread run to avoid problems
        while not self.stopExec:
            if self.clinetDiscon:
                # Indicate that we are waiting for a connection once we start the program
                self.conStatSigR.emit("Waiting")  # Send the signal to indicate that we are waiting for connection

                self.tcp.acceptConnection()  # Wait for a connection to come
                if self.stopExec:
                    break  # Exit immediately after request

                # If we have a connection, then we proceed and indicate that to the user
                self.clinetDiscon = False  # If we reach this point, then we have a connected client
                self.conStatSigR.emit("Connected")  # Send the signal to indicate connection

            elif not self.stopExec:
                # Handle the possible exceptions, to avoid app crash
                try:
                    recData = self.tcp.receive()  # Start receiving the data from the client
                except (OSError, ConnectionResetError):
                    self.logD.log("EXCEPT", "Stellarium server thread stopped.", "run")
                    self.quit()  # Call quit to be sure that we close properly
                    break

                # If we receive zero length data, then that means the connection is broken
                if len(recData) != 0:
                    recData = self.dataHandle.decodeStell(recData)
                    self.dataShowSig.emit(recData[0], recData[1])  # Send the data to be shown on the GUI widget
                    self.sendClientConn.emit(recData)  # Emit the signal to send the data to the raspberry pi
                else:
                    self.tcp.releaseClient()  # Close all sockets since client is gone
                    self.clinetDiscon = True  # Tell that the client has disconnected
                    self.stopExec = False  # Continue in the loop since quit is not yet called

    def quit(self):
        self.stopExec = True  # Raise the execution stop flag
        self.clinetDiscon = True  # Indicate a disconnected client
        self.tcp.releaseClient()  # Whenever this function is called we need to close the connection
        self.conStatSigR.emit("Disconnected")  # Send the signal to indicate disconnection

    def connectButtonRPi(self):
        if self.isRunning():
            self.quit()  # Quit the currently running thread
            self.logD.log("INFO", "The thread for the server was closed", "connectButton")
        else:
            self.logD.log("INFO", "Started a thread for the server", "connectButton")
            self.start()  # Initiate the server to its thread
