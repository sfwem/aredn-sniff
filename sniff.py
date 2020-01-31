"""
Thread for performing remote AREDN host sniffing
"""

import gps
import ssh
import pynmea2
import threading
import sys
import logging
import queue

from config import *

__all__ = ['AREDNSniffer', 'AREDNBeacon']

class AREDNBeacon:
    """
    Represent a beacon packet and its coorelated GPS position
    """
    def __init__(self):
        self.time: str = None
        self.MHz: int = None
        self.rssi: int = None
        self.MAC: str = None
        self.IBSS: str = None
        self.GPS: pynmea2.GGA = None
        return

    @classmethod
    def from_bytes(cls, s: bytes):
        """
        Create AREDNBeacon from a tcpdump output line
        :param s:
        :return:
        """
        ret = cls()
        d = s.decode().strip().split()
        ret.time = d[0]
        ret.MHz = int(d[5])
        ret.rssi = int(d[8][:-3])
        ret.MAC = d[16][3:]
        ret.IBSS = d[18][1:-1]
        return ret

    def __repr__(self):
        if self.GPS:
            gps = "GPSTime: %s Lat: %.6f Lon: %.6f Alt: %.1f" % (self.GPS.timestamp, self.GPS.latitude,
                                                                 self.GPS.longitude, self.GPS.altitude)
        else:
            gps = "No GPS"

        return "BeaconPkt: [%s] %s %d MHz %d dBm %s %s" % (gps, self.time, self.MHz, self.rssi, self.MAC, self.IBSS)

class AREDNSniffer(threading.Thread):
    """
    Connect to a AREDN-firmware Ubiquiti Bullet M5 (may work with any device, on wlan0?
    Must have tcpdump package installed on device
    Will disable olsrd on the device
    A device reboot should revert all changes

    Executes commands as dictated in configration object to setup sniffing mode
    Executes tcpdump and parses stdout for actual data
    Creates GPS thread to get location stamps for incoming packets
    Logs all of this to the configured capture log
    """
    def __init__(self, gc: GPSConfig, sc: SnifferConfig):
        super().__init__(name=self.__class__.__name__, daemon=True)
        self.gpsconfig = gc
        self.snifferconfig = sc
        self.gps_thread: gps.GPSMon = None
        self.ssh_thread: ssh.SSHThread = None
        return

    def start(self):
        self.gps_thread = gps.GPSMon(self.gpsconfig.port, self.gpsconfig.logfile)
        self.ssh_thread = ssh.SSHThread(self.snifferconfig)

        self.gps_thread.start()
        self.ssh_thread.start()

        with open(self.snifferconfig.capturelog, 'a') as capture:
            while 1:
                if not self.ssh_thread.is_alive():
                    raise RuntimeError("SSH Thread died")
                try:
                    pkt = AREDNBeacon.from_bytes(self.ssh_thread.get(1))
                    pkt.GPS = self.gps_thread.position(self.gpsconfig.maxage)
                    pktstr = str(pkt)
                    sys.stderr.write(pktstr+'\n')
                    sys.stderr.flush()
                    capture.write(pktstr+'\n')
                    capture.flush()
                except queue.Empty:
                    continue
                except Exception as e:
                    logging.exception(e)
                    pass

        return
