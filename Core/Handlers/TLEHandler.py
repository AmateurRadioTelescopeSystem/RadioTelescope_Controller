import logging
import time
import os
import urllib3
import certifi
from PyQt5 import QtCore


class TLEHandler(QtCore.QObject):
    def __init__(self, cfg_data, parent=None):
        super(TLEHandler, self).__init__(parent)
        self.logger = logging.getLogger(__name__)  # Create the logger for the file
        self.cfg_data = cfg_data

    def tle_expiry_checker(self):
        expiration = False  # Set the variable initially
        try:
            url = self.cfg_data.get_tle_url()  # Get the URL from the settings file
            file_dir = os.path.abspath("TLE/" + url.split("/")[-1])  # Directory for the saved file

            tle_mod_date = os.path.getmtime(file_dir)  # Get the last modified time in seconds
            cur_time = time.time()  # Get the current time in seconds
            delta_time = int((cur_time - tle_mod_date) / 86400)  # Get the time passed since last modification in days

            # Check whether the current TLEs have expired
            expiration = bool(delta_time >= int(self.cfg_data.get_tle_update_interval()))

            error_details = ""
            exit_code = True
        except FileNotFoundError:
            exit_code = False
            expiration = True
            error_details = "File not found"
        except Exception as exception:
            self.logger.exception("Error occurred when checking the TLE file. See traceback.")
            error_details = "%s\n\nProbably the required file does not exist!" % exception
            exit_code = False

        return [exit_code, expiration, error_details]

    def tle_retriever(self):
        # TODO improve the function
        # TODO Add exception handling code in case of empty URL string
        url = self.cfg_data.get_tle_url()  # Get the URL from the settings file
        file_dir = os.path.abspath("TLE/" + url.split("/")[-1])  # Directory for the saved file
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())  # Create the HTTP pool manager

        try:
            tle = http.request('GET', url)  # Try to retrieve the file

            with open(file_dir, 'wb') as tle_file:
                tle_file.write(tle.data)  # Save the TLE file contents
                tle_file.close()
            error_details = ""
            exit_code = True
        except Exception as exception:
            self.logger.exception("Error occurred acquiring TLE file. See traceback.")
            error_details = "%s" % exception
            exit_code = False

        return [exit_code, error_details]
