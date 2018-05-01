import StellariumDataHandling
from PyQt5 import QtCore


class StellThread(QtCore.QThread):
    def __init__(self, tcpStell, tcpClient, uiControl, parent = None):
        super(StellThread, self).__init__(parent)  # Get the parent
        self.tcp = tcpStell  # TCP handling object
        self.tcpClient = tcpClient  # TCP client object for radio telescope communication
        self.ui = uiControl  # GUI manipulation object
        self.dataHandle = StellariumDataHandling.StellariumData()  # Data conversion object
        self.clinetDiscon = True  # Client disconnection indicator
        self.stopExec = False  # Stop thread execution indicator
        # self.conStatSig = QtCore.pyqtSignal(name='stellTCPConStat')

    def run(self):
        self.stopExec = False  # Initialize it in every thread run to avoid problems
        while not self.stopExec:
            if self.clinetDiscon:
                # Indicate that we are waiting for a connection once we start the program
                self.ui.connectStellariumBtn.setText("Stop")  # Change user's selection
                self.ui.tcpStelServChkBox.setCheckState(QtCore.Qt.Unchecked)
                self.ui.stellConStatText.setText("<html><head/><body><p><span style=\" "
                                                 "color:#ffb400;\">Waiting...</span></p></body></html>")

                self.tcp.acceptConnection()  # Wait for a connection to come
                if self.stopExec:
                    break  # Exit immediately after request

                # If we have a connection, then we proceed and indicate that to the user
                self.clinetDiscon = False  # If we reach this point, then we have a connected client
                self.ui.connectStellariumBtn.setText("Disable")  # Change user's selection
                self.ui.tcpStelServChkBox.setCheckState(QtCore.Qt.Unchecked)
                self.ui.stellConStatText.setText("<html><head/><body><p><span style=\" "
                                                 "color:#00ff00;\">Connected</span></p></body></html>")
                self.ui.nextPageLabel.setEnabled(True)  # Enable the label to indicate functionality
                self.ui.stellNextPageBtn.setEnabled(True)  # Enable next page transition, since we have a connection
                self.ui.stackedWidget.setCurrentIndex(1)

            elif not self.stopExec:
                recData = self.tcp.receive()  # Start receiving the data from the client

                # If we receive zero length data, then that means the connection is broken
                if len(recData) != 0:
                    recData = self.dataHandle.decodeStell(recData)
                    self.ui.raPosInd_2.setText("%.5fh" %float(recData[0]))  # Update the corresponding field
                    self.ui.decPosInd_2.setText("%.5f" %float(recData[1]) + u"\u00b0")  # Update the corresponding field
                elif not self.stopExec:
                    self.tcp.releaseClient()  # Close all sockets since client is gone
                    self.clinetDiscon = True  # Tell that the client has disconnected
                    self.stopExec = False  # Continue in the loop since quit is not yet called
                    self.ui.nextPageLabel.setEnabled(False)  # Disable the next page label
                    self.ui.stellNextPageBtn.setEnabled(False)  # Disable the button to avoid changing to next page

    def quit(self):
        self.stopExec = True  # Raise the execution stop flag
        self.clinetDiscon = True  # Indicate a disconnected client
        self.tcp.releaseClient()  # Whenever this function is called we need to close the connection

        # Set the button to the default state
        self.ui.connectStellariumBtn.setText("Enable")
        self.ui.tcpStelServChkBox.setCheckState(QtCore.Qt.Unchecked)
        self.ui.stellConStatText.setText("<html><head/><body><p><span style=\" "
                                         "color:#ff0000;\">Disconnected</span></p></body></html>")
        self.ui.nextPageLabel.setEnabled(False)  # Disable the next page label
        self.ui.stellNextPageBtn.setEnabled(False)  # Disable the button to avoid changing to next page
        #self.ui.stackedWidget.setCurrentIndex(0)
