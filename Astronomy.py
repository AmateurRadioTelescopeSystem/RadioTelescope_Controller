from PyQt5 import QtCore
import logging
import ephem

_rad_to_deg = 57.2957795131  # Radians to degrees conversion factor


class Calculations(QtCore.QObject):
    def __init__(self, cfg_data, parent=None):
        super(Calculations, self).__init__(parent)
        self.logD = logging.getLogger(__name__)  # Create the logger for the file
        self.cfg_data = cfg_data

        self.latlon = cfg_data.getLatLon()  # Get the latitude and longitude
        self.alt = cfg_data.getAltitude()  # Get the observer's altitude in meters
        self.observer = ephem.Observer()  # Create the observer object
        self.observer.lat, self.observer.lon = self.latlon[0], self.latlon[1]  # Provide the observer's location
        self.observer.elevation = float(self.alt)  # Set the location's altitude in meters

    def hour_angle(self, date: str, obj_ra: float):
        self.observer.date = date
        return float(self.observer.sidereal_time())*_rad_to_deg - obj_ra  # Ephem sidereal returns in rad
