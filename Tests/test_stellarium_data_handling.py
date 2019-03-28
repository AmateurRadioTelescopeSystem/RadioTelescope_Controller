import time
import struct
from Core.Stellarium.StellariumDataHandling import StellariumData


def test_decode():
    data = struct.pack("3iIi", 24, 0, int(time.time()), int(2486607107), int(-279864841))
    decoded_packet = StellariumData.decode(data)

    assert decoded_packet[0] == 13.895
    assert decoded_packet[1] == -23.458


def test_encode():
    encoded_packet = StellariumData.encode(13.895, -23.458)
    containing_data = struct.unpack("3iIii", encoded_packet)

    assert containing_data[0] == 24
    assert containing_data[1] == 0
    assert containing_data[2] == int(time.time())
    assert containing_data[3] == int(2486607107)
    assert containing_data[4] == int(-279864841)
    assert containing_data[5] == 0
