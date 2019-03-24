import xml.etree.ElementTree as etree
import logging


class Confdata:
    # Class constructor
    def __init__(self, filename):
        self.filename = filename  # Create a variable with the given filename
        self.logger = logging.getLogger(__name__)  # Create the logger for this module
        try:
            self.tree = etree.parse(self.filename)  # Try to parse the given file
            self.root = self.tree.getroot()  # Get the root from the XML file
        except Exception:
            self.logger.exception("There is an issue with the XML settings file. See traceback below.")

    def parse(self):
        try:
            self.tree = etree.parse(self.filename)  # Try to parse the given file
            self.root = self.tree.getroot()  # Get the root from the XML file
        except Exception:
            self.logger.exception("There is an issue with the XML settings file. See traceback below.")

    def get_config(self, child, subchild):
        children = list(self.root.find(child))
        for item in children:
            if item.tag == subchild:
                return item.text
            else:
                continue

    def set_config(self, element, child, value):
        elm = self.root.find(element)  # Get the required element from the tree
        children = list(elm)  # List the children of the element
        for item in children:
            if item.tag == child:
                item.text = value
                self.tree.write(self.filename)
                break
            else:
                continue

    def get_maps_selection(self):
        return self.root.find("location").get("gmaps")

    def set_maps_selection(self, stat):
        self.root.find("location").set("gmaps", stat)
        self.tree.write(self.filename)

    def get_server_remote(self, element):
        return self.root.find(element).get("remote")

    def set_server_remote(self, element, status):
        self.root.find(element).set("remote", status)
        self.tree.write(self.filename)

    def get_lat_lon(self):
        lat = self.get_config("location", "latitude")
        lon = self.get_config("location", "longitude")
        return [lat, lon]

    def set_lat_lon(self, location):
        self.set_config("location", "latitude", str(location[0]))
        self.set_config("location", "longitude", str(location[1]))

    def get_altitude(self):
        return self.get_config("location", "altitude")

    def set_altitude(self, altitude):
        self.set_config("location", "altitude", str(altitude))

    # TCP client data
    def get_tcp_client_host(self):
        return self.get_config("TCP", "host")

    def set_tcp_client_host(self, host):
        self.set_config("TCP", "host", host)

    def get_tcp_client_port(self):
        return self.get_config("TCP", "port")

    def set_tcp_client_port(self, port):
        self.set_config("TCP", "port", str(port))

    def get_tcp_client_auto_conn_status(self):
        return self.root.find("TCP").get("autoconnect")

    def tcp_client_auto_conn_enable(self):
        self.root.find("TCP").set("autoconnect", "yes")
        self.tree.write(self.filename)

    def tcp_client_auto_conn_disable(self):
        self.root.find("TCP").set("autoconnect", "no")
        self.tree.write(self.filename)

    # TCP Stellarium server data
    def get_stell_host(self):
        return self.get_config("TCPStell", "host")

    def set_stell_host(self, host):
        self.set_config("TCPStell", "host", host)

    def get_stell_port(self):
        return self.get_config("TCPStell", "port")

    def set_stell_port(self, port):
        self.set_config("TCPStell", "port", str(port))

    def get_tcp_stell_auto_conn_status(self):
        return self.root.find("TCPStell").get("autoconnect")

    def tcp_stell_auto_conn_enable(self):
        self.root.find("TCPStell").set("autoconnect", "yes")
        self.tree.write(self.filename)

    def tcp_stell_auto_conn_disable(self):
        self.root.find("TCPStell").set("autoconnect", "no")
        self.tree.write(self.filename)

    # TCP RPi server data (Auto-connection is dependant on the client)
    def get_rpi_host(self):
        return self.get_config("TCPRPiServ", "host")

    def set_rpi_host(self, host):
        self.set_config("TCPRPiServ", "host", host)

    def get_rpi_port(self):
        return self.get_config("TCPRPiServ", "port")

    def set_rpi_port(self, port):
        self.set_config("TCPRPiServ", "port", str(port))

    # Get the currently saved object
    def get_object(self):
        stat_obj = self.root.find("object").get("stationary")
        if stat_obj == "no":
            return [self.get_config("object", "name"), -1]
        else:
            name = self.get_config("object", "name")
            ra = self.get_config("object", "RA")
            dec = self.get_config("object", "DEC")
            return [name, ra, dec]

    def set_object(self, name, ra=-1, dec=-1):
        if (ra == -1) or (dec == -1):
            self.root.find("object").set("stationary", "no")
            self.set_config("object", "name", name)
            self.set_config("object", "RA", str(-1))
            self.set_config("object", "DEC", str(-1))
        else:
            self.root.find("object").set("stationary", "yes")
            self.set_config("object", "name", name)
            self.set_config("object", "RA", str(ra))
            self.set_config("object", "DEC", str(dec))

    def get_home_steps(self):
        ra = self.root.find("Steps").get("ra_to_home")
        dec = self.root.find("Steps").get("dec_to_home")
        return [ra, dec]

    def set_home_steps(self, ra, dec):
        self.root.find("Steps").set("ra_to_home", str(ra))
        self.root.find("Steps").set("dec_to_home", str(dec))
        self.tree.write(self.filename)

    def get_tle_url(self):
        url = self.get_config("TLE", "url")
        return url

    def set_tle_url(self, url: str):
        self.set_config("TLE", "url", url)

    def get_tle_auto_update(self):
        return self.root.find("TLE").get("autoupdate")

    def set_tle_auto_update(self, status: bool):
        if status is True:
            val = "yes"
        else:
            val = "no"
        self.root.find("TLE").set("autoupdate", val)

    def get_tle_update_interval(self):
        return self.get_config("TLE", "updt_interval")

    def set_tle_update_interval(self, interval):
        self.set_config("TLE", "updt_interval", str(interval))

    def get_all_configuration(self):
        loc = list(self.root.find("location"))
        tcp = list(self.root.find("TCP"))
        data = []
        for loc_item in loc:
            data.append(loc_item.text)
        for tcp_item in tcp:
            data.append(tcp_item.text)
        return data
