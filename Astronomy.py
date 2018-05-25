from PyQt5 import QtCore
import logging
import ephem
import time

_rad_to_deg = 57.2957795131  # Radians to degrees conversion factor
_sec_to_day = 1.1574074e-5

# TODO add them to a file to be easily changed
_motor_RA_steps_per_deg = 43200.0
_motor_DEC_steps_per_deg = 10000.0
_max_step_frq = 400.0  # Maximum stepping frequency of the motors in Hz


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

    def hour_angle(self, date: tuple, obj_ra: float):
        self.observer.date = date
        return float(self.observer.sidereal_time())*_rad_to_deg - obj_ra  # Ephem sidereal returns in rad

    def current_time(self):
        """
        Get the current time in GMT without daylight saving.
        Calculate the current day in decimal, which is needed for other calculations
        :return time_tuple: A tuple containing the year, month and decimal day
        """
        gmt = time.gmtime()  # Get the current time
        day = gmt.tm_mday  # Save the current day
        hour = gmt.tm_hour  # Save the current hour
        mint = gmt.tm_min  # Save the current minute
        decimal_day = float(day) + float(hour)/24.0 + float(mint)/(24.0*60.0) + float(gmt.tm_sec)/(24.0*60.0*60.0)
        time_tuple = (gmt.tm_yday, gmt.tm_mon, decimal_day)

        return time_tuple

    def transit(self, obj_ra: float, obj_dec: float, stp_to_home_ra: int, stp_to_home_dec: int):
        """
        Transit final hour angle calculation.
        The final hour angle is calculated for a stationary object. We add the maximum time taken by any motor
        to go to the desired position, to the current time and then the hour angle at the latter position is calculated.
        :param obj_ra: Provide the objects right ascension in degrees
        :param obj_dec: Provide the objects declination in degrees
        :param stp_to_home_ra: Give the number o steps away from home position for the right ascension motor
        :param stp_to_home_dec: Enter the number of steps away from home for the declination motor
        :return: A list containing the hour angle at the target location and the dec of the object
        """
        step_distance_ra = abs(stp_to_home_ra + obj_ra*_motor_RA_steps_per_deg)  # Negative signs are included in values
        step_distance_dec = abs(stp_to_home_dec + obj_dec*_motor_DEC_steps_per_deg)
        max_distance = max(step_distance_ra, step_distance_dec)  # Calculate the maximum distance, to calculate max time
        max_move_time = max_distance/_max_step_frq  # Maximum time required for any motor, calculated in seconds
        # TODO may be needed to add some "safety" seconds
        cur_time = self.current_time()  # Get the current time in tuple
        target_time = (cur_time[0], cur_time[1], cur_time[2] + max_move_time*_sec_to_day)  # Add the necessary time
        hour_angl = self.hour_angle(target_time, obj_ra)  # Calculate the hour angle at the target location

        return [hour_angl, obj_dec]

