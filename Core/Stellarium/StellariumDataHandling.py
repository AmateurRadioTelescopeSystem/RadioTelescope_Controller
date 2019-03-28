# Stellarium protocol: https://free-astro.org/images/b/b7/Stellarium_telescope_protocol.txt

import struct
import time


class StellariumData:
    @staticmethod
    def decode(data):
        """

        Args:
            data: Structured data package received from stellarium

        Returns:
            Decoded right ascension and declination
        """
        data = struct.unpack("3iIi", data)  # Unpack the data as we know the format from the link provided above
        ra_real = data[3]*(12.0/2147483648.0)  # Calculate the true value of the right ascension
        dec_real = data[4]*(90.0/1073741824.0)  # and the true value of the declination
        return [round(ra_real, 6), round(dec_real, 6)]

    @staticmethod
    def encode(ra_real, dec_real):
        """

        Todo:
            Write a very descriptive documentation for these two functions

        Todo:
            Add exception handling and logging of errors as part of this class

        Args:
            ra_real: A real valued RA
            dec_real: A real valued DEC

        Returns:
            Packaged version of the provided right ascension and declination
        """
        ra_integer = int(float(ra_real) * (2147483648.0 / 12.0))  # Calculate the Stellarium calibrated RA value
        dec_integer = int(float(dec_real) * (1073741824.0 / 90.0))  # Calculate the Stellarium calibrated DEC value
        data = struct.pack("3iIii", 24, 0, int(time.time()), ra_integer, dec_integer, 0)  # Package the data
        return data  # Return the packaged binary data
