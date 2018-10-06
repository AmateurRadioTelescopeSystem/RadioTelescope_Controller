from PyQt5 import QtCore
import time
import logging


class SimulHandler(QtCore.QObject):
    simStartSig = QtCore.pyqtSignal(tuple, name='simulationStarter')
    simStopSig = QtCore.pyqtSignal(name='stopCurrentSimulation')
    simFinishedSig = QtCore.pyqtSignal(name='simulationFinishedIndicator')

    def __init__(self, tcpStellarium, parent=None):
        super(SimulHandler, self).__init__(parent)
        self.tcpStell = tcpStellarium
        self.log = logging.getLogger(__name__)
        self.stopSim = False

    def start(self):
        self.simStartSig.connect(self.simulateScanning)
        self.simStopSig.connect(self.simStopper)
        self.log.debug("Simulation thread started. Thread ID = %d" % QtCore.QThread.currentThreadId())

    @QtCore.pyqtSlot(tuple, name='simulationStarter')
    def simulateScanning(self, map_points: tuple):
        self.stopSim = False
        num_points = len(map_points)
        if num_points > 0:
            for i in range(0, num_points):
                if self.stopSim is True:
                    break
                if map_points[i][0] < 0:
                    ra = (map_points[i][0] + 23.9997)/15.0
                else:
                    ra = map_points[i][0]/15.0
                self.tcpStell.sendDataStell.emit(ra, float(map_points[i][1]))
                time.sleep(0.1)
        if self.stopSim is False:
            self.simFinishedSig.emit()  # Indicate that sim has finished
        self.stopSim = False  # Execute that only if stop is requested

    @QtCore.pyqtSlot(name='stopCurrentSimulation')
    def simStopper(self):
        self.stopSim = True

