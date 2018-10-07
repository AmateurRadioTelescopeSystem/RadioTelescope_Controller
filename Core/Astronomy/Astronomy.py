from PyQt5 import QtCore
import numpy as np
import logging
import ephem
import math
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
        :param points: Initial box points at four corners. Coordinate system and epoch is included
        :param step_size: Stepping size for each axis (a tuple)
        :param direction: Direction of scanning with respect to the first point
        :return: A tuple containing the point map
        """
        epoch = points[5]  # Get the epoch provided
        coord_system = points[4]  # Get the coordinate system of the provided coordinates

        direct = direction.split(": ")[1]  # Get the direction string
        second_axis = False
        if direct == "R-Down":
            initial_point = points[0]
            second_point = points[1]
            third_point = points[2]
            fourth_point = points[3]
        elif direct == "R-Up":
            initial_point = points[3]
            second_point = points[2]
            third_point = points[1]
            fourth_point = points[0]
        elif direct == "L-Down":
            initial_point = points[1]
            second_point = points[0]
            third_point = points[3]
            fourth_point = points[2]
        elif direct == "L-Up":
            initial_point = points[2]
            second_point = points[3]
            third_point = points[0]
            fourth_point = points[1]
        elif direct == "Up-R":
            initial_point = points[3]
            second_point = points[0]
            third_point = points[1]
            fourth_point = points[2]
            second_axis = True
        elif direct == "Up-L":
            initial_point = points[2]
            second_point = points[1]
            third_point = points[0]
            fourth_point = points[3]
            second_axis = True
        elif direct == "Down-R":
            initial_point = points[0]
            second_point = points[3]
            third_point = points[2]
            fourth_point = points[1]
            second_axis = True
        elif direct == "Down-L":
            initial_point = points[1]
            second_point = points[2]
            third_point = points[3]
            fourth_point = points[0]
            second_axis = True
        # TODO implement a fix to include the last box without overlap
        num_boxes_x = math.floor(abs(second_point[0] - initial_point[0])/step_size[0])
        num_boxes_y = math.floor(abs(second_point[1] - third_point[1])/step_size[1])

        # Generate the point map in the Equatorial coordinate system
        x_point = initial_point[0]  # Get the first coordinate before the loop
        y_point = initial_point[1]
        raw_points = ((x_point, y_point), )
        transformed = self.coordinate_transform((x_point, y_point,), (coord_system, epoch,))
        map_points = ((round(transformed[0], 6), round(transformed[1], 6)),)

        if not second_axis:
            if second_point[0] - initial_point[0] < 0:
                fill_reverse = False  # Indicate reverse direction filling of the tuple with points (inverse logic)
            else:
                fill_reverse = True

            for i in range(0, int(num_boxes_y)):
                if i is not 0:
                    y_point -= step_size[1]  # Don't deduct the step on the first point
                fill_reverse = not fill_reverse  # Negate the direction of point filling

                for j in range(0, int(num_boxes_x)):
                    if not (j == 0 and i != 0):
                        if fill_reverse is True:
                            x_point -= step_size[0]
                        else:
                            x_point += step_size[0]
                    raw_points += ((round(x_point, 6), round(y_point, 6)),)

                    transformed = self.coordinate_transform((x_point, y_point,), (coord_system, epoch,))
                    map_points += ((round(transformed[0], 6), round(transformed[1], 6)),)
        else:
            if second_point[1] - initial_point[1] < 0:
                fill_reverse = False  # Indicate reverse direction filling of the tuple with points (inverse logic)
            else:
                fill_reverse = True

            for i in range(0, int(num_boxes_x)):
                if i is not 0:
                    x_point -= step_size[0]  # Don't deduct the step on the first point
                fill_reverse = not fill_reverse  # Negate the direction of point filling

                for j in range(0, int(num_boxes_y)):
                    if not (j == 0 and i != 0):
                        if fill_reverse is True:
                            y_point -= step_size[1]
                        else:
                            y_point += step_size[1]
                    raw_points += ((round(x_point, 6), round(y_point, 6)),)

                    transformed = self.coordinate_transform((x_point, y_point,), (coord_system, epoch,))
                    map_points += ((round(transformed[0], 6), round(transformed[1], 6)),)
        # TODO Remove print statement
        print("Raw points:")
        print(raw_points)
        print("Mapped points")
        print(map_points)

        return [map_points, raw_points]

    def scanning_point_calculator(self, map_points: tuple, init_steps: tuple, step_size: tuple,
                                  int_time=0.0, objec=None):
        """
        Generate the scanning map in HA and DEC
        :param map_points:
        :param init_steps: Initial steps from home in RA and DEC axis
        :param step_size:
        :param int_time:
        :param objec: Planetary object passing. Default is none.
        :return: The calculated position of the points for scanning
        """
        if objec is None:
            first_point = self.transit(map_points[0][0], map_points[0][1], init_steps[0], init_steps[1], 0)
            roc_ra = roc_dec = 0  # Not rate of change for the non-planetary bodies
        else:
            first_point = self.tracking_planetary(objec, init_steps[0], init_steps[1])  # Get also the rate of change
            roc_ra = first_point[2]  # Get the rate of change for RA as returned from the tracking calculation
            roc_dec = first_point[3]  # Get the rate of change for DEC as returned from the tracking calculation
        calc_points = "%f_%f" % (first_point[0], first_point[1])

        # Initialize the variable with the initial steps from home
        step_incr_dec = init_steps[1]
        step_incr_ra = init_steps[0]
        for i in range(1, len(map_points)):  # Exclude first point
            try:
                if map_points[i][1] != map_points[i + 1][1]:
                    step_incr_dec += step_size[1] * _motor_DEC_steps_per_deg
                if map_points[i][0] != map_points[i + 1][0]:
                    step_incr_ra += step_size[0] * _motor_RA_steps_per_deg
            except IndexError:
                pass
            step_incr = (step_incr_ra, step_incr_dec, )

            if int(int_time * 60.0) is not 0:
                tr_time = int(int_time * 60.0)
            else:
                tr_time = 0

            # Account for planetary object coordinates
            # TODO Test how the planetary selection is functioning
            if objec is None:
                transit_point = self.transit(map_points[i][0], map_points[i][1], step_incr[0], step_incr[1], tr_time)
            else:
                transit_point = self.transit_planetary(objec, step_incr[0], step_incr[1], tr_time)
            calc_points += "_%f_%f" % (transit_point[0], transit_point[1])  # Save the points as a string

        return [calc_points, (roc_ra, roc_dec, )]

    def coordinate_transform(self, coordinates: tuple, system_and_date: tuple):
        position = np.radians(coordinates)  # Convert coordinates from degrees to radians
        if system_and_date[0] == "Equatorial":
            ra, dec = coordinates
        elif system_and_date[0] == "Horizontal":
            ra, dec = np.degrees(map(float, self.observer.radec_of(position[0], position[1])))
        elif system_and_date[0] == "Galactic":
            galactic_posit = ephem.Galactic(position[0], position[1], epoch=system_and_date[1])
            ra, dec = np.degrees(galactic_posit.to_radec())  # Convert point from Galactic to RA and DEC
        elif system_and_date[0] == "Ecliptical":
            ecliptical_posit = ephem.Ecliptic(position[0], position[1], epoch=system_and_date[1])
            ra, dec = np.degrees(ecliptical_posit.to_radec())  # Convert to RA and DEC from Ecliptic coordinate system

        return ra, dec  # Return the coordinate tuple
