from PySide2 import QtCore
import logging


class SimulHandler(QtCore.QObject):
    simStartSig = QtCore.Signal(tuple, float, name='simulationStarter')
    simStopSig = QtCore.Signal(name='stopCurrentSimulation')

    def __init__(self, tcpStellarium, parent=None):
        super(SimulHandler, self).__init__(parent)
        self.tcpStell = tcpStellarium
        self.log = logging.getLogger(__name__)
        self.stopSim = False
        self.counter = 0
        self.map_points = ()

    def start(self):
        self.timer = QtCore.QTimer()  # Simulation timer

        self.simStartSig.connect(self.simStarter)
        self.simStopSig.connect(self.simStopper)
        self.timer.timeout.connect(self.simulateScanning)

        self.log.info("Simulation handler thread started")

    def simulateScanning(self):
        num_points = len(self.map_points)
        if num_points > 0 and self.counter < num_points:
            if self.map_points[self.counter][0] < 0:
                ra = (self.map_points[self.counter][0] + 23.9997)/15.0
            else:
                ra = self.map_points[self.counter][0]/15.0
            self.tcpStell.sendDataStell.emit(ra, float(self.map_points[self.counter][1]))
            self.counter += 1  # Increment the counter variable
        else:
            self.timer.stop()  # Stop the timer
            self.counter = 0  # Reset the count

    @QtCore.Slot(tuple, float, name='simulationStarter')
    def simStarter(self, points: tuple, speed: float):
        self.map_points = points  # Save the map points
        self.counter = 0  # Reset the counter variable
        self.timer.setInterval(speed)  # Set the interval at which the point will move
        self.timer.start()  # Start the simulation timer

    @QtCore.Slot(name='stopCurrentSimulation')
    def simStopper(self):
        self.timer.stop()  # Stop the timer as requested
        self.counter = 0  # Reset the counter

    def close(self):
        self.timer.stop()  # Stop the timer before exiting the thread
        self.log.info("Simulation handler thread closed")
