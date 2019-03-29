import os
import shutil

import pytest
from Core.Handlers import TLEHandler
from Core.Configuration import ConfigData


@pytest.fixture(scope="module")
def tle_handle_object():
    cfg_data = ConfigData.ConfData(os.path.abspath('Tests/Settings/settings.xml'))
    yield TLEHandler.TLEHandler(cfg_data, "Tests/TLE/")


def test_retriever(tle_handle_object):
    tle_status = tle_handle_object.tle_retriever()
    assert tle_status[0]
    assert tle_status[1] == ""


def test_expiry_checker(tle_handle_object):
    if not os.listdir("Tests/TLE"):
        tle_handle_object.tle_retriever()
    tle_status = tle_handle_object.tle_expiry_checker()

    assert tle_status[0]
    assert not tle_status[1]
    assert tle_status[2] == ""

    shutil.rmtree("Tests/TLE")
    exp_check = tle_handle_object.tle_expiry_checker()

    assert not exp_check[0]
    assert exp_check[1]
    assert exp_check[2] == "File not found"
