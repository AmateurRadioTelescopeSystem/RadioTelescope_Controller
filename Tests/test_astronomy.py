import os
import sys
import unittest
import time
from Core.Astronomy import Astronomy
from Core.Configuration import ConfigData


class TestConversions(unittest.TestCase):
    def setUp(self):
        cfgData = ConfigData.ConfData(os.path.abspath('Tests/Settings/settings.xml'))
        self.astronomy = Astronomy.Calculations(cfgData)

    def test_hour_angle(self):
        """
        Use Alnitak as a testing object.
        RA: 85.18975deg or 5h40m45.54s in J2000
        DEC: -1.9425deg or -1d56m32.2s in J2000
        Date: 23/03/2019 22:00:00 UTC

        Returns:
            Nothing
        """
        hour_angle = self.astronomy.hour_angle(85.18975, -1.9425, (2019, 3, 23.916667,))
        self.assertEqual(hour_angle, 88.622679, "The calculated hour angle is incorrect")

    def test_hour_angle_to_ra(self):
        right_ascension = self.astronomy.hour_angle_to_ra(88.622679, -1.9425, (2019, 3, 23, 22, 0, 0))
        self.assertEqual(right_ascension, 85.189772, "The calculated right ascension is incorrect")

    def test_current_time(self):
        current_time_test = self.astronomy.current_time()  # Get the current time under test
        current_time = time.gmtime()  # Get the actual current time
        self.assertEqual(current_time_test[0], current_time.tm_year, "Years do not match")
        self.assertEqual(current_time_test[1], current_time.tm_mon, "Months do not match")
        self.assertEqual(current_time_test[2], current_time.tm_mday, "Days do not match")
        self.assertEqual(current_time_test[3], current_time.tm_hour, "Hours do not match")
        self.assertEqual(current_time_test[4], current_time.tm_min, "Minutes do not match")
        self.assertEqual(current_time_test[5], current_time.tm_sec, "Seconds do not match")

    def test_transit(self):
        """
        Provide a dummy right ascension and declination, because it varies from different runs. The dummy right
        ascension provided is the hour angle of the specified day.
        """
        target_ha, object_dec = self.astronomy.transit(85.18975, -1.9425, 1900, -6789, 20, (2019, 3, 23.916667,))
        self.assertEqual(object_dec, -1.9425, "Objects declinations do not match")
        self.assertEqual(target_ha, 93.887052, "Hour angles do not match")

    def test_transit_planetary(self):
        """
        Use mars as the testing object.
        """
        target_ha, object_dec = self.astronomy.transit_planetary('mars', 0, 0, 0, (2019, 3, 23.916667,))
        self.assertEqual(target_ha, 125.22636, "Planet's right ascension mismatch")
        self.assertEqual(object_dec, -19.880418, "Planet's declination mismatch")

    def test_tracking_planetary(self):
        target_ha, object_dec, roc_ra, roc_dec = self.astronomy.tracking_planetary('mars', 0, 0, (2019, 3, 23.916667,))
        self.assertEqual(target_ha, 125.22636, "Planet's right ascension mismatch")
        self.assertEqual(object_dec, -19.880418, "Planet's declination mismatch")
        self.assertEqual(roc_ra, 0.000434, "The rate of change for the right ascension is not correct")
        self.assertEqual(roc_dec, -0.000106, "The rate of change for the declination is not correct")


if __name__ == "__main__":
    unittest.main()
