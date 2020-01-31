"""
Thread for tracking GPS position
Monitors NMEA stream for GGA positions
Caches last GGA position for retrieval via GPSMon.position()
"""

import pynmea2
import serial
import threading
import logging
import time
from typing import Optional

log = logging.getLogger('GPS')

__all__ = ['GPSMon']

class GPSMon(threading.Thread):
    """
    Continuously monitor gps position
    """
    def __init__(self, port, logfilename: str=None):
        super().__init__(name=self.__class__.name, daemon=True)
        self.port = port
        self.ser = serial.Serial(port, baudrate=9600, timeout=1.0)
        self.lastpos: pynmea2.GGA = None
        self.lastpostime = time.time()
        self.logfilename = logfilename
        self.logfile = None
        return

    def position(self, maxage: Optional[float] = None) -> Optional[pynmea2.GGA]:
        """
        Get the current position.
        Returns None if we don't have a valid position, or position is older than maxage
        :return:
        """
        if maxage:
            if time.time() - self.lastpostime > maxage:
                return None
        return self.lastpos

    def run(self):
        log.info("GPSMon started")
        self.reader = pynmea2.NMEAStreamReader(self.ser)
        if self.logfilename:
             self.logfile = open(self.logfilename, 'ba')

        while 1:
            line = self.ser.readline()
            try:
                for msg in self.reader.next(line.decode()):
                    log.debug(msg)
                    if msg.sentence_type == 'GGA':
                        if msg.gps_qual in (1,2):
                            self.lastpos = msg
                            self.lastpostime = time.time()
                        log.debug(msg.__repr__())
            except (UnicodeDecodeError, pynmea2.ParseError):
                log.warning("Bad line: %s", line)
                pass
            finally:
                if self.logfile:
                    self.logfile.write(line)
                    self.logfile.flush()

# Test harness
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    gps = GPSMon('/dev/ttyACM0')
    gps.start()
    gps.join()
