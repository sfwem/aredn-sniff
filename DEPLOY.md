# Deploy notes
RPI should have a mountpoint, preferrably a vfat partition, mounted at /aredndata with pi:pi permissions  
/etc/fstab line:
```
LABEL=AREDNDATA /aredndata vfat uid=pi,gid=pi 0 0
```
tcpdump-mini package must be installed.  
either install via ssh
```
opkg install tcpdump-mini
```
or via the package: http://downloads.arednmesh.org/releases/3/18/3.18.9.0/packages/mips_24kc/base/tcpdump-mini_4.9.2-1_mips_24kc.ipk
```
opkg install tcpdump-mini_4.9.2-1_mips_24kc.ipk
```

startup via user systemd:
```
mkdir -p ~/.config/systemd/user
ln -s ~/aredn-sniff/aredn-sniff.service ~/.config/systemd/user/aredn-sniff.service
sudo loginctl enable-linger pi
systemctl --user enable aredn-sniff
``` 

wifi AP for access: 
https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md