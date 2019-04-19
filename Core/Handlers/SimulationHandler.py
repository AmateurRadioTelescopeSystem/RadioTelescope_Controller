import logging
from PyQt5 import QtCore
from Core.Networking import StellariumThread


class SimulHandler(QtCore.QObject):
    simStartSig = QtCore.pyqtSignal(tuple, float, name='simulationStarter')
    simStopSig = QtCore.pyqtSignal(name='stopCurrentSimulation')

    def __init__(self, tcp_stellarium: StellariumThread.StellThread, parent=None):
        super(SimulHandler, self).__init__(parent)
        self.tcp_stell = tcp_stellarium
        self.logger = logging.getLogger(__name__)
        self.stop_sim = False
        self.counter = 0
        self.map_points = ()

    def start(self):
        self.timer = QtCore.QTimer()  # Simulation timer

        self.simStartSig.connect(self.sim_starter)
        self.simStopSig.connect(self.sim_stopper)
        self.timer.timeout.connect(self.simulate_scanning)

        self.logger.info("Simulation handler thread started")

    def simulate_scanning(self):
        num_points = len(self.map_points)
        if num_points > 0 and self.counter < num_points:
            if self.map_points[self.counter][0] < 0:
                ra_degrees = (self.map_points[self.counter][0] + 23.9997)/15.0
            else:
                ra_degrees = self.map_points[self.counter][0]/15.0
            self.tcp_stell.sendDataStell.emit(ra_degrees, float(self.map_points[self.counter][1]))
            self.counter += 1  # Increment the counter variable
        else:
            self.timer.stop()  # Stop the timer
            self.counter = 0  # Reset the count

    @QtCore.pyqtSlot(tuple, float, name='simulationStarter')
    def sim_starter(self, points: tuple, speed: float):
        self.map_points = points  # Save the map points
        self.counter = 0  # Reset the counter variable
        self.timer.setInterval(speed)  # Set the interval at which the point will move
        self.timer.start()  # Start the simulation timer

    @QtCore.pyqtSlot(name='stopCurrentSimulation')
    def sim_stopper(self):
        self.timer.stop()  # Stop the timer as requested
        self.counter = 0  # Reset the counter

    def close(self):
        self.timer.stop()  # Stop the timer before exiting the thread
        self.logger.info("Simulation handler thread closed")
