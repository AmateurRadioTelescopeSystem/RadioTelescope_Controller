from PyQt5 import QtCore
import time
import logging


class SimulHandler(QtCore.QObject):
    simStartSig = QtCore.pyqtSignal(tuple, name='simulationStarter')
    simFinishedSig = QtCore.pyqtSignal(name='simulationFinishedIndicator')

    def __init__(self, tcpStellarium, parent=None):
        super(SimulHandler, self).__init__(parent)
        self.tcpStell = tcpStellarium
        self.log = logging.getLogger(__name__)

    def start(self):
        self.simStartSig.connect(self.simulateScanning)
        self.log.debug("Simulation thread started. Thread ID = %d" % QtCore.QThread.currentThreadId())

    @QtCore.pyqtSlot(tuple, name='simulationStarter')
    def simulateScanning(self, map_points: tuple):
        num_points = len(map_points)
        if num_points > 0:
            for i in range(0, num_points):
                self.tcpStell.sendDataStell.emit(float(map_points[i][0]) / 15.0, float(map_points[i][1]))
                time.sleep(0.1)
        self.simFinishedSig.emit()  # Indicate that sim has finished

