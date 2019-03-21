import os
import gzip
import logging
import logging.handlers


# ============================================================================
# Define a Custom Log File Handler
# Initial code: https://mattgathu.github.io/multiprocessing-logging-in-python/
# Code for compression, retrieved from logging docs:
# https://docs.python.org/3/howto/logging-cookbook.html#using-a-rotator-and-namer-to-customize-log-rotation-processing
# ============================================================================
class CustomLogTimedRotationHandler(logging.Handler):
    """
    Customize the timed rotating file handler to include old log compression
    """
    def __init__(self, filename, when, backup_count, enc, utc):
        """
        Class constructor to make the necessary initializations.

        :param filename: The name of the logging file
        :param when: When to rotate
        :param backup_count: Max number of old files to keep
        :param enc: Log file's encoding
        :param utc: UTC to be used as logging time
        """
        logging.Handler.__init__(self)

        self._handler = logging.handlers.TimedRotatingFileHandler(
            filename, when, backupCount=backup_count, encoding=enc, utc=utc)
        self._handler.rotator = self.compressor  # Compress the old file in every rotation
        self._handler.namer = self.namer  # Name the compressed file

    def setFormatter(self, fmt):
        """
        Set the formatter for the file handler

        :param fmt: Formatter string as passed from the configuration
        :return: Nothing
        """
        logging.Handler.setFormatter(self, fmt)
        self._handler.setFormatter(fmt)

    def emit(self, record):
        """
        Emit the message to the new handler

        :param record: Message record
        :return: Nothing
        """
        try:
            self._handler.emit(record)  # Write to log file
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)

    def close(self):
        """
        Close the handler upon request.
        :return: Nothing
        """
        if self._handler is not None:
            self._handler.close()
        logging.Handler.close(self)

    def compressor(self, source, dest):
        """
        Compress the file on every rotation

        :param source: Source file name
        :param dest: Destination file name
        :return: Nothing
        """
        with open(source, "rb") as source_file:
            data = source_file.read()  # Read the data from file and compress them
            compressed = gzip.compress(data, 9)  # Get the compressed binary data
            with open(dest, "wb") as dest_file:
                dest_file.write(compressed)  # Save the compressed data to file
        os.remove(source)  # Remove uncompressed file

    def namer(self, name):
        """
        Append the appropriate suffix to the compressed file name

        :param name: File name to append suffix
        :return: Nothing
        """
        return name + ".gz"


class CustomLogRotationHandler(logging.Handler):
    """
    Customize the rotating file handler to include old log compression and size rotation
    """
    def __init__(self, filename, max_bytes, backup_count, enc, delay=False):
        """
        Class constructor to make the necessary initializations.

        :param filename: The name of the logging file
        :param when: When to rotate
        :param backup_count: Max number of old files to keep
        :param enc: Log file's encoding
        :param utc: UTC to be used as logging time
        """
        logging.Handler.__init__(self)

        self._handler = logging.handlers.RotatingFileHandler(
            filename, maxBytes=max_bytes, backupCount=backup_count, encoding=enc, delay=delay)
        self._handler.rotator = self.compressor  # Compress the old file in every rotation
        self._handler.namer = self.namer  # Name the compressed file

    def setFormatter(self, fmt):
        """
        Set the formatter for the file handler

        :param fmt: Formatter string as passed from the configuration
        :return: Nothing
        """
        logging.Handler.setFormatter(self, fmt)
        self._handler.setFormatter(fmt)

    def emit(self, record):
        """
        Emit the message to the new handler

        :param record: Message record
        :return: Nothing
        """
        try:
            self._handler.emit(record)  # Write to log file
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)

    def close(self):
        """
        Close the handler upon request.

        :return: Nothing
        """
        if self._handler is not None:
            self._handler.close()
        logging.Handler.close(self)

    def compressor(self, source, dest):
        """
        Compress the file on every rotation

        :param source: Source file name
        :param dest: Destination file name
        :return: Nothing
        """
        with open(source, "rb") as source_file:
            data = source_file.read()  # Read the data from file and compress them
            compressed = gzip.compress(data, 9)  # Get the compressed binary data
            with open(dest, "wb") as dest_file:
                dest_file.write(compressed)  # Save the compressed data to file
        os.remove(source)  # Remove uncompressed file

    def namer(self, name):
        """
        Append the appropriate suffix to the compressed file name

        :param name: File name to append suffix
        :return: Nothing
        """
        return name + ".gz"


'''
class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

    def close(self):
        pass
'''
