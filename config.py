__all__ = ["GPSConfig", "SnifferConfig", "systemlog", "logfmt"]

systemlog = '/aredndata/system.log'
logfmt = "%(asctime)s %(levelname)8s %(name)20s %(message)s"

class GPSConfig:
    port = "/dev/ttyACM0"
    logfile = "/aredndata/nmea.log"
    maxage = 10.0  # Maximum age of GPS position

class SnifferConfig:
    host = "localnode"
    port = 2222
    username = "root"
    password = "XXX"
    capturelog = '/aredndata/capture.log'

    # These commands will be executed, blindly, in an interactive shell to configure monitoring parameters
    setup = [
            "/etc/init.d/olsrd stop",
            "ifconfig wlan0 down",
            "iw reg set HX",
            "iw wlan0 set monitor control",
            "ifconfig wlan0 up",
            "iw wlan0 set channel 179 10MHz",
        ]

    # tcpdump command. Parsing code is stdout dependent
    tcpdump = "tcpdump -e -n -i wlan0 type mgt subtype beacon"
