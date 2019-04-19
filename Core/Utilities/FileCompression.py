import os
import gzip


class FileCompression:
    """
    A helper class used in the custom logger to compress and save the past logs
    """
    @staticmethod
    def compressor(source: str, destination: str):
        """
        Compress the file on every rotation

        Args:
            source (str): The path of the file to be compressed
            destination (str): The destination path of the compressed file

        Todo:
            Add exception handling, if needed
        """
        with open(source, "rb") as source_file:
            source_data = source_file.read()  # Read the data from file and compress them
            compressed_data = gzip.compress(source_data, 9)  # Get the compressed binary data
        with open(destination, "wb+") as destination_file:
            destination_file.write(compressed_data)  # Save the compressed data to file
        os.remove(source)  # Remove uncompressed file

    @staticmethod
    def namer(name: str):
        """
        Append the appropriate suffix to the compressed file name

        Args:
            name (str): The file name at which the suffix will be appended
        """
        return name + ".gz"
