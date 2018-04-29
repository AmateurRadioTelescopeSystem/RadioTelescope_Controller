import logging

class logData(object):
    def __init__(self, loger_name):
        fileHandler = logging.FileHandler('RadioTelescope.log') #Create the necessary file
        #strmHandler = logging.StreamHandler() #Limited use, removed in the end product
        
        #Set the formatting for the logs
        #Include level:time_of_log:name_of_logger:log_message
        fileHandler.setFormatter(logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s'))
        self.logger = logging.getLogger(loger_name) #Initialize the logger
        self.logger.setLevel(logging.INFO) #Set the logging level for the current logger
        self.logger.addHandler(fileHandler) #Add the file handler to the logger
        #self.logger.addHandler(strmHandler) #Used when debugging
    
    def log(self, level, msg, fname = ""):
        if level == "DEBUG":
            self.logger.debug(fname + ":" + msg)
        elif level == "INFO":
            self.logger.info(fname + ":" + msg)
        elif level == "WARNING":
            self.logger.warning(fname + ":" + msg)
        elif level == "ERROR":
            self.logger.error(fname + ":" + msg)
        elif level == "CRITICAL":
            self.logger.critical(fname + ":" + msg)
        elif level == "EXCEPT":
            self.logger.error(fname + ":" + msg, exc_info = True)
    
    def logClose(self):
        logging.shutdown()