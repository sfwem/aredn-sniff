# aredn-sniff readme

This is wardriving rig for aredn networks. It is intended to run on an a Raspberry Pi but could run anywhere.
It will connect to a config specified aredn node, configure the wifi interface for sniffing, sniff with tcpdump, and log captured data. 
Stations are identified from their beacon packets + mac address.
Location is determined thourgh an GPS NEMA stream

See [deploy.md]() for deploy instructions

## Configuration
Edit config.py 

## Logs
logs are written to /aredndata
* system.log is the system log
* nmea.log is the raw GPS NMEA logs
* capture.log is the coalated packet + nmea data

## TODO
* Log GPS acquire/loss in system.log
