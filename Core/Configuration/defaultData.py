# Strings of the default file settings are included here

log_config_str = """Logging:
  version: 1
  disable_existing_loggers: True

  formatters:
    debugging:
      format: "%(asctime)s  [%(thread)12d] %(levelname)-8s - %(name)35s.%(funcName)-20s - %(message)s"
    mainFile:
      format: "%(asctime)s  [%(name)35s.%(funcName)-20s]  %(levelname)-8s -  %(message)s"
    brief:
      format: "%(levelname)-8s [%(thread)d] - %(name)35s.%(funcName)-20s - %(message)s"

  handlers:
    console:
      class: logging.StreamHandler
      formatter: brief
      level: DEBUG
      stream: ext://sys.stderr
    debugFile:
      class: Handlers.CLogFileHandler.CustomLogRotationHandler
      formatter: debugging
      level: DEBUG
      filename: logs/debugging_info.log
      max_bytes: 1048576  # Set change size to 1MB
      backup_count: 7  # Keep 7 days old files and delete older
      enc: 'utf-8'  # Set the file encoding to utf-8
    radioTelescopeThread:
      class: Handlers.CLogFileHandler.CustomLogTimedRotationHandler
      formatter: mainFile
      level: INFO
      filename: logs/RadioTelescope_Logger.log
      when: 'midnight'  # Rotate the file creation every midnight
      backup_count: 7  # Keep 7 days old files and delete older
      enc: 'utf-8'  # Set the file encoding to utf-8
      utc: True  # Set the time of file creation to be UTC

  loggers:
    debugging_logger:
      level: DEBUG
      handlers: [debugFile]

  # Configure the root logger
  root:
    level: INFO
    handlers: [console, radioTelescopeThread]

"""

settings_xml_str = """<settings>
    <location gmaps="no">
        <altitude>50</altitude>
        <latitude>40.6306</latitude>
        <longitude>22.9589</longitude>
    </location>
    <TCP autoconnect="yes" remote="no">
        <host>127.0.0.1</host>
        <port>10001</port>
    </TCP>
    <TCPStell autoconnect="yes" remote="no">
        <host>127.0.0.1</host>
        <port>10002</port>
    </TCPStell>
    <TCPRPiServ remote="no">
        <host>127.0.0.1</host>
        <port>10003</port>
    </TCPRPiServ>
    <TLE autoupdate="yes">
        <updt_interval>7</updt_interval>
        <url>https://www.celestrak.com/NORAD/elements/geo.txt</url>
    </TLE>
    <object stationary="yes">
        <name>Crab Nebula</name>
        <RA>83.63308333</RA>
        <DEC>22.0145</DEC>
    </object>
    <Steps dec_to_home="0" ra_to_home="0" />
</settings>
"""