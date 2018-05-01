import StellariumDataHandling
from PyQt5 import QtCore
import queue


class StellThread(QtCore.QThread):
    def __init__(self, tcpStell, uiControl, parent = None):
        super(StellThread, self).__init__(parent)
        self.tcp = tcpStell
        self.ui = uiControl
        self.dataHandle = StellariumDataHandling.StellariumData()
        self.stopEnabled = False

    def run(self):
        # Indicate that we are waiting for a connection once we start the program
        self.ui.connectStellariumBtn.setText("Stop")  # Change user's selection
        self.ui.tcpStelServChkBox.setCheckState(QtCore.Qt.Unchecked)
        self.ui.stellConStatText.setText("<html><head/><body><p><span style=\" "
                                         "color:#ffb400;\">Waiting...</span></p></body></html>")

        self.tcp.acceptConnection()  # Wait for a connection to come

        # If we have a connection, then we proceed and indicate that to the user
        self.ui.connectStellariumBtn.setText("Disable")  # Change user's selection
        self.ui.tcpStelServChkBox.setCheckState(QtCore.Qt.Unchecked)
        self.ui.stellConStatText.setText("<html><head/><body><p><span style=\" "
                                         "color:#00ff00;\">Connected</span></p></body></html>")
        while(1):
            recData = self.tcp.receive()

            # If we receive zero length data, then that means the connection is broken
            if len(recData) != 0:
                recData = self.dataHandle.decodeStell(recData)
                self.ui.raPosInd_2.setText(str(recData[0]))  # Update the corresponding field
            else:
                self.ui.connectStellariumBtn.setText("Enable")
                self.ui.tcpStelServChkBox.setCheckState(QtCore.Qt.Unchecked)
                self.ui.stellConStatText.setText("<html><head/><body><p><span style=\" "
                                                 "color:#ff0000;\">Disconnected</span></p></body></html>")
                break  # Exit from the thread

    def quit(self):
        self.tcp.releaseClient()
        self.ui.connectStellariumBtn.setText("Enable")
        self.ui.tcpStelServChkBox.setCheckState(QtCore.Qt.Unchecked)
        self.ui.stellConStatText.setText("<html><head/><body><p><span style=\" "
                                         "color:#ff0000;\">Disconnected</span></p></body></html>")
