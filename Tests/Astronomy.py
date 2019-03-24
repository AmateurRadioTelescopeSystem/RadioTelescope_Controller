import os
import sys
import unittest
import time
from Core.Astronomy import Astronomy
from Core.Configuration import ConfigData


class TestConversions(unittest.TestCase):
    def setUp(self):
        cfgData = ConfigData.Confdata(os.path.abspath('Tests/Settings/settings.xml'))
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
        hour_angle = self.astronomy.hour_angle((2019, 3, 23.916667,), 85.18975, -1.9425)
        self.assertEqual(88.62399, round(hour_angle, 5), "The calculated hour angle is incorrect")

    def test_hour_angle_to_ra(self):
        hour_angle = self.astronomy.hour_angle_to_ra(88.62399, (2019, 3, 23.916667,))
        self.assertEqual(88.62399, round(hour_angle, 5), "The calculated right ascension is incorrect")

