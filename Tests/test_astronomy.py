import os
import time

import pytest
from Core.Astronomy import Astronomy
from Core.Configuration import ConfigData


@pytest.fixture(scope="module")
def astro_object():
    cfg_data = ConfigData.ConfData(os.path.abspath('Tests/Settings/settings.xml'))
    yield Astronomy.Calculations(cfg_data)


def test_hour_angle(astro_object):
    """
    Use Alnitak as a testing object.
    RA: 85.18975deg or 5h40m45.54s in J2000
    DEC: -1.9425deg or -1d56m32.2s in J2000
    Date: 23/03/2019 22:00:00 UTC

    Returns:
        Nothing
    """
    hour_angle = astro_object.hour_angle(85.18975, -1.9425, (2019, 3, 23.916667,))
    assert hour_angle == 88.622679


def test_hour_angle_to_ra(astro_object):
    right_ascension = astro_object.hour_angle_to_ra(88.622679, -1.9425, (2019, 3, 23.916667,))
    assert right_ascension == 85.189772


def test_current_time(astro_object):
    current_time_test = astro_object.current_time()  # Get the current time under test
    current_time = time.gmtime()  # Get the actual current time
    assert current_time_test[0] == current_time.tm_year
    assert current_time_test[1] == current_time.tm_mon
    assert current_time_test[2] == current_time.tm_mday
    assert current_time_test[3] == current_time.tm_hour
    assert current_time_test[4] == current_time.tm_min
    assert current_time_test[5] == current_time.tm_sec


def test_transit(astro_object):
    """
    Provide a dummy right ascension and declination, because it varies from different runs. The dummy right
    ascension provided is the hour angle of the specified day.
    """
    target_ha, object_dec = astro_object.transit(85.18975, -1.9425, 1900, -6789, 20, (2019, 3, 23.916667,))
    assert object_dec == -1.9425
    assert target_ha == 93.887052


def test_transit_planetary(astro_object):
    """
    Use mars as the testing object.
    """
    target_ha, object_dec = astro_object.transit_planetary('mars', 0, 0, 0, (2019, 3, 23.916667,))
    assert target_ha == 125.22636
    assert object_dec == -19.880418

    # Check if providing a wrong object works as expected
    no_coordinates = astro_object.transit_planetary('wrong_object', 0, 0, 0)
    assert no_coordinates == []


def test_tracking_planetary(astro_object):
    target_ha, object_dec, roc_ra, roc_dec = astro_object.tracking_planetary('mars', 0, 0, (2019, 3, 23.916667,))
    assert target_ha == 125.22636
    assert object_dec == -19.880418
    assert roc_ra == 0.000434
    assert roc_dec == -0.000106

    # Check if providing a wrong object works as expected
    no_coordinates = astro_object.tracking_planetary('wrong_object', 0, 0)
    assert no_coordinates == []
