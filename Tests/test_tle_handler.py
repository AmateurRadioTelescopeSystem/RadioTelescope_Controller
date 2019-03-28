import os
import time

import pytest
from Core.Handlers import TLEHandler
from Core.Configuration import ConfigData


@pytest.fixture(scope="module")
def tle_handle_object():
    cfg_data = ConfigData.ConfData(os.path.abspath('Tests/Settings/settings.xml'))
    yield TLEHandler.TLEHandler(cfg_data)


def test_expiry_retriever(tle_handle_object):
    tle_status = tle_handle_object.tle_retriever()
    assert tle_status[0]
    assert tle_status[1] == ""


def test_tle_expiry_checker(tle_handle_object):
    tle_status = tle_handle_object.tle_expiry_checker()
    assert tle_status[0]
