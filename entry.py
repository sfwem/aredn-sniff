"""
Entry point script for aredn-sniff
Configures logging, brings up AREDNSniffer instance
"""

import logging
from config import *
from sniff import *

if __name__ == '__main__':
    fmt = logging.Formatter(logfmt)

    rootlog = logging.getLogger()
    rootlog.setLevel(logging.NOTSET)

    stdlog = logging.StreamHandler()
    stdlog.setLevel(logging.INFO)
    stdlog.setFormatter(fmt)
    rootlog.addHandler(stdlog)

    fh = logging.FileHandler(filename=systemlog)
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    rootlog.addHandler(fh)

    logging.info("Sniffer started")

    try:
        sniffer = AREDNSniffer(GPSConfig(), SnifferConfig())
        sniffer.start()
        sniffer.join()
    except Exception as e:
        logging.exception(e)
        pass

    logging.info("Software exited")

