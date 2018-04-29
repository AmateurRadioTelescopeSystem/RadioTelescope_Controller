import xml.etree.ElementTree as etree
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
import os

class confData(object):
    #Class constructor
    def __init__(self, filename):
        self.filename = filename #Create a variable with the given filename
        self.parse() #Parse the XML file
    
    def parse(self):
        #Add a handling code for the case parsing fails
        self.tree = etree.parse(self.filename)
        self.root = self.tree.getroot()
        
    def getConfig(self, child, subchild):
        #self.parse()
        children = list(self.root.find(child))
        for item in children:
            if item.tag == subchild:
                return item.text
            else:
                continue
    
    def setConfig(self, element, child, value):
        elm = self.root.find(element) #Get the required element from the tree
        children = list(elm) #List the children of the element
        for item in children:
            if item.tag == child:
                item.text = value
                if (element == "TCP") or (element == "location"):
                    elm.set("updated", "yes")
                self.tree.write(self.filename)
                break
            else:
                continue
    
    def getUpdateStatus(self, element):
        return self.root.find(element).get("updated")
    
    def setUpdateStatus(self, element, status):
        self.root.find(element).set("updated", status)
        self.tree.write(self.filename)
    
    def getLatLon(self):
        lat = self.getConfig("location", "latitude")
        lon = self.getConfig("location", "longitude")
        return [lat, lon]
        
    def setLatLon(self, location):
        self.setConfig("location", "latitude", str(location[0]))
        self.setConfig("location", "longitude", str(location[1]))
    
    def getAltitude(self):
        return self.getConfig("location", "altitude")
    
    def setAltitude(self, altitude):
        self.setConfig("location", "altitude", str(altitude))
    
    def getHost(self):
        return self.getConfig("TCP", "host")
        
    def setHost(self, host):
        self.setConfig("TCP", "host", host)
    
    def getPort(self):
        return self.getConfig("TCP", "port")
        
    def setPort(self, port):
        self.setConfig("TCP", "port", str(port))
    
    def getTCPAutoConnStatus(self):
        return self.root.find("TCP").get("autoconnect")
        
    def TCPAutoConnEnable(self):
        self.root.find("TCP").set("autoconnect", "yes")
        self.tree.write(self.filename)
        
    def TCPAutoConnDisable(self):
        self.root.find("TCP").set("autoconnect", "no")
        self.tree.write(self.filename)
    
    def getObject(self):
        stat_obj = self.root.find("object").get("stationary")
        if stat_obj == "no":
            return [self.getConfig("object", "name"), -1]
        else:
            name = self.getConfig("object", "name")
            ra = self.getConfig("object", "RA")
            dec = self.getConfig("object", "DEC")
            return [name, ra, dec]
    
    def setObject(self, name, ra = -1, dec = -1):
        if (ra == -1) or (dec == -1):
            self.root.find("object").set("stationary", "no")
            self.setConfig("object", "name", name)
            self.setConfig("object", "RA", str(-1))
            self.setConfig("object", "DEC", str(-1))
        else:
            self.root.find("object").set("stationary", "yes")
            self.setConfig("object", "name", name)
            self.setConfig("object", "RA", str(ra))
            self.setConfig("object", "DEC", str(dec))
    
    def getAllConfiguration(self):
        loc = list(self.root.find("location"))
        tcp = list(self.root.find("TCP"))
        data = []
        for loc_item in loc:
            data.append(loc_item.text)
        for tcp_item in tcp:
            data.append(tcp_item.text)
        return data