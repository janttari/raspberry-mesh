# Raspberry 7612 Mesh 802.11s  
![](https://raw.githubusercontent.com/janttari/raspberry-mesh/master/doc/kaavio.png)    
wlan1: mediatek 7612 mesh0  
wlan0: raspberry internal wifi hostapd  
  
### MESH    
usage:  
./mesh.py gateway up  
./mesh.py gateway down  

./mesh.py client up  
./mesh.py client down  

### ALFRED  
./alfredmsg.py #start in receiver mode  
./alfredmsg.py 255 test test test #send message to channel (data type) 255  
  
-----
### Todo

- [ ] Bridge hostapd
- [ ] alfred python class with events and callbacks
- [ ] package(s) create script
- [ ] installer
- [ ] mesh.py alfred primary/ secondary gateway/ client?
- [ ] systemd scripts
- [ ] conf files (wifi channel mesh/ ap, ap name...)
