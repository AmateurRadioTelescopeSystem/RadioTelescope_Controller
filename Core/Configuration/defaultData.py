# Strings of the default file settings are included here

log_config_str = """Logging:
  version: 1
  disable_existing_loggers: True

  formatters:
    debugging:
      format: "%(asctime)s  [%(thread)12d] %(levelname)-8s - %(name)30s.%(funcName)-20s - %(message)s"
    mainFile:
      format: "%(asctime)s  [%(name)30s.%(funcName)-18s]  %(levelname)-8s -  %(message)s"
    brief:
      format: "%(levelname)-8s [%(thread)d] - %(name)30s.%(funcName)-20s - %(message)s"

  handlers:
    console:
      class: logging.StreamHandler
      formatter: brief
      level: DEBUG
      stream: ext://sys.stderr
    debugFile:
      class: logging.FileHandler
      formatter: debugging
      level: DEBUG
      filename: logs/debugging_info.log
    radioTelescopeThread:
      class: CLogFileHandler.CustomLogHandler
      formatter: mainFile
      level: INFO
      filename: logs/RadioTelescope_Logger.log
      when: 'midnight'  # Rotate the file creation every midnight
      enc: 'utf-8'  # Set the file encoding to utf-8
      utc: True  # Set the time of file creation to be UTC

  # Configure the root logger
  root:
    level: INFO
    handlers: [console, debugFile, radioTelescopeThread]

"""

settings_xml_str = """<settings>
    <location gmaps="no">
        <altitude>50</altitude>
        <latitude>40.6306</latitude>
        <longitude>22.9589</longitude>
    </location>
    <TCP autoconnect="yes">
        <host>10.42.0.158</host>
        <port>10001</port>
    </TCP>
    <TCPStell autoconnect="yes" remote="no">
        <host>127.0.0.1</host>
        <port>10002</port>
    </TCPStell>
    <TCPRPiServ remote="yes">
        <host>10.42.0.1</host>
        <port>10003</port>
    </TCPRPiServ>
    <object stationary="yes">
        <name>Crab Nebula</name>
        <RA>83.63308333</RA>
        <DEC>22.0145</DEC>
    </object>
    <Steps dec_to_home="0" ra_to_home="0" />
</settings>
"""