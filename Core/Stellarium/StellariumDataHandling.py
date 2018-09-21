# Stellarium protocol: https://free-astro.org/images/b/b7/Stellarium_telescope_protocol.txt

import struct
import time


class StellariumData(object):
    def decodeStell(self, data):
        data = struct.unpack("3iIi", data)  # Unpack the data as we know the format from the link provided above
        ra = data[3]*(12.0/2147483648.0)  # Calculate the true value of the right ascension
        dec = data[4]*(90.0/1073741824.0)  # and the true value of the declination
        return [ra, dec]

    def encodeStell(self, ra, dec):
        RaInt = int(float(ra) * (2147483648.0 / 12.0))  # Calculate the Stellarium calibrated RA value
        DecInt = int(float(dec) * (1073741824.0 / 90.0))  # Calculate the Stellarium calibrated DEC value
        data = struct.pack("3iIii", 24, 0, int(time.time()), RaInt, DecInt, 0)  # Pack the data in the correct format
        return data  # Return the packaged binary data
