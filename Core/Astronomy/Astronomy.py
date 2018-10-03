from PyQt5 import QtCore
import logging
import ephem
import time

_rad_to_deg = 57.2957795131  # Radians to degrees conversion factor
_sec_to_day = 1.1574074e-5  # How many days a second has

# TODO add them to a file to be easily changed
_motor_RA_steps_per_deg = 43200.0/15.0  # 43200 is in steps per hour of right ascension
_motor_DEC_steps_per_deg = 10000.0  # Steps per degree
_max_step_frq = 200.0  # Maximum stepping frequency of the motors in Hz


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
        calculated_ha = float(self.observer.sidereal_time())*_rad_to_deg - obj_ra  # Ephem sidereal returns in rad
        return calculated_ha

    def hour_angle_to_ra(self, obj_ha: float):
        """
        Return the current RA of an object provided its HA and having properly calibrated ephem.
        :param obj_ha: Hour angle of the desired object
        :return: The current right ascension of the object in JNOW
        """
        self.observer.date = self.current_time()  # Get the current time and date as needed by ephem
        calculated_ra = float(self.observer.sidereal_time())*_rad_to_deg - obj_ha  # Calculate the right ascension

        if calculated_ra < 0.0:
            calculated_ra = calculated_ra + 359.9955
        return calculated_ra

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
        time_tuple = (gmt.tm_year, gmt.tm_mon, decimal_day)

        return time_tuple

    def transit(self, obj_ra: float, obj_dec: float, stp_to_home_ra: int, stp_to_home_dec: int, transit_time: int):
        """
        Transit final hour angle calculation.
        The final hour angle is calculated for a stationary object. We add the maximum time taken by any motor
        to go to the desired position, to the current time and then the hour angle at the latter position is calculated.
        Home position of the dish is considered to be 0h hour angle and 0 degrees declination.
        :param obj_ra: Provide the objects right ascension in degrees
        :param obj_dec: Provide the objects declination in degrees
        :param stp_to_home_ra: Give the number o steps away from home position for the right ascension motor
        :param stp_to_home_dec: Enter the number of steps away from home for the declination motor
        :param transit_time: Enter the time to transit is seconds
        :return: A list containing the hour angle at the target location and the dec of the object
        """
        # TODO may be needed to add some "safety" seconds
        cur_time = self.current_time()  # Get the current time in tuple
        cur_ha = self.hour_angle(cur_time, obj_ra)  # Get the current object hour angle
        step_distance_ra = abs(stp_to_home_ra + cur_ha * _motor_RA_steps_per_deg)
        step_distance_dec = abs(stp_to_home_dec + obj_dec * _motor_DEC_steps_per_deg)

        max_distance = max(step_distance_ra, step_distance_dec)  # Calculate the maximum distance, to calculate max time
        max_move_time = max_distance / _max_step_frq  # Maximum time required for any motor, calculated in seconds
        target_time = (cur_time[0], cur_time[1], cur_time[2] + (max_move_time + transit_time) * _sec_to_day)
        target_ha = self.hour_angle(target_time, obj_ra)  # Calculate the hour angle at the target location

        # self.logD.debug("RA %f, DEC %f, time %f" % (target_ha, obj_dec, cur_time[1]))  # Debugging log

        return [target_ha, obj_dec]

    def transit_planetary(self, objec, stp_to_home_ra: int, stp_to_home_dec: int, transit_time: int):
        """
        Calculate object's position when the dish arrives at position.
        This function calculates the coordinates of the requested object, taking into account the delay of the dish
        until it moves to the desired position.
        :param objec: pyephem object type, which is the object of interest (e.g. ephem.Jupiter())
        :param stp_to_home_ra: Number of steps from home position for the right ascension motor
        :param stp_to_home_dec: Number of steps from home position for the declination motor
        :param transit_time: Enter the time to transit is seconds
        :return: Object's coordinates at the dish arrival position
        """
        if objec == "Sun":
            objec = ephem.Sun()  # Select the Sun object
        elif objec == "Jupiter":
            objec = ephem.Jupiter()  # Select Jupiter as object
        elif objec == "Mars":
            objec = ephem.Mars()  # Select Mars as the object
        elif objec == "Venus":
            objec = ephem.Venus()  # Select Venus as the object
        elif objec == "Moon":
            objec = ephem.Moon()  # Select moon as the object

        cur_time = self.current_time()  # Get the current time in tuple
        date = "%.0f/%.0f/%.6f" % (cur_time[0], cur_time[1], cur_time[2])  # Get the current date
        objec.compute(cur_time, epoch=date)  # Compute the object's coordinates

        # Get the current coordinates for the planetary body
        obj_ra = float(objec.a_ra)*_rad_to_deg
        obj_dec = float(objec.a_dec)*_rad_to_deg

        cur_ha = self.hour_angle(cur_time, obj_ra)  # Get the current object hour angle
        step_distance_ra = abs(stp_to_home_ra + cur_ha * _motor_RA_steps_per_deg)
        step_distance_dec = abs(stp_to_home_dec + obj_dec * _motor_DEC_steps_per_deg)

        max_distance = max(step_distance_ra, step_distance_dec)  # Calculate the maximum distance, to calculate max time
        max_move_time = max_distance / _max_step_frq  # Maximum time required for any motor, calculated in seconds
        target_time = (cur_time[0], cur_time[1], cur_time[2] + (max_move_time + transit_time) * _sec_to_day)

        # Recalculate the coordinates for the new time
        objec.compute(cur_time, epoch=date)
        obj_ra = float(objec.a_ra) * _rad_to_deg
        obj_dec = float(objec.a_dec) * _rad_to_deg
        target_ha = self.hour_angle(target_time, obj_ra)  # Calculate the hour angle at the target location

        return [target_ha, obj_dec]

    def tracking_planetary(self, objec, stp_to_home_ra: int, stp_to_home_dec: int):
        """
        Calculate the rate of change for the coordinates of different planetary bodies.
        :param objec: pyephem object type, which is the object of interest (e.g. ephem.Jupiter())
        :param stp_to_home_ra: Number of steps from home position for the right ascension motor
        :param stp_to_home_dec: Number of steps from home position for the declination motor
        :return: Object's coordinates on transit and the rate of change
        """
        sum_ra = sum_dec = 0.0  # Variable to hold the sum for averaging
        prev_ra = prev_dec = 0.0  # Initialize the variables
        count = 0  # Counting variable used in the loop and averaging
        transit_coords = self.transit_planetary(objec, stp_to_home_ra, stp_to_home_dec, 0)  # Calculate transit first

        # Get the right object
        if objec == "Sun":
            objec = ephem.Sun()  # Select the Sun object
        elif objec == "Jupiter":
            objec = ephem.Jupiter()  # Select Jupiter as object
        elif objec == "Mars":
            objec = ephem.Mars()  # Select Mars as the object
        elif objec == "Venus":
            objec = ephem.Venus()  # Select Venus as the object
        elif objec == "Moon":
            objec = ephem.Moon()  # Select moon as the object

        cur_time = self.current_time()  # Get the current time in tuple
        epoch_date = "%.0f/%.0f/%.6f" % (cur_time[0], cur_time[1], cur_time[2])  # Get the current date
        comp_date = epoch_date  # Set the dates to equal at first

        # Iterate for 24 hours to get enough points
        for count in range(0, 24):
            objec.compute(comp_date, epoch=epoch_date)
            cur_ra = float(objec.a_ra)
            cur_dec = float(objec.a_dec)

            if count > 0:
                sum_ra += (cur_ra - prev_ra)
                sum_dec += (cur_dec - prev_dec)
            prev_ra = cur_ra
            prev_dec = cur_dec
            comp_date = "%.0f/%.0f/%.6f" % (cur_time[0], cur_time[1], cur_time[2] + 0.04166666667)  # One hour increment

        roc_ra = ((sum_ra/count)*_rad_to_deg)/3600.0  # Return degrees per second for the RA
        roc_dec = ((sum_dec/count)*_rad_to_deg)/3600.0  # Return degrees per second for the DEC

        return [transit_coords[0], transit_coords[1], roc_ra, roc_dec]

    def scanning_map_generator(self, points: tuple, step_size: tuple, direction: str):
        """
        Generate a sky map of points to be scanned.
        :param points: Initial box points at four corners. Counting direction clock-wise (a tuple)
        :param step_size: Stepping size for each axis (a tuple)
        :param direction: Direction of scanning with respect to the first point
        :return: A tuple containing the point map
        """
