#!/usr/bin/env python3
import threading, time, subprocess, os, sys, signal

CHANNELS={255,253} #listen these channels (data types)

#
# https://downloads.open-mesh.org/batman/manpages/alfred.8.html
# ----------------------------------------------------------------------------------------------
MSGDICT={}
RUN=True

def signal_handler(sig, frame):
    print('CTRL+c. Stopping threads...')
    RUN=False
    al.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ----------------------------------------------------------------------------------------------
def getMac(device: str): #print(getMac("mesh-bridge"))
    cmd='ifconfig |grep "'+device+'" -A 5|grep -o "ether.*" |cut -d " " -f 2'
    p=subprocess.check_output(cmd, shell=True)
    return p.decode().rstrip("\n")

def getIp4(device: str): #print(getIp4("bat0"))
    cmd='ifconfig |grep "'+device+'" -A 5|grep -o "inet .*"|cut -d " " -f 2'
    p=subprocess.check_output(cmd, shell=True)
    return p.decode().rstrip("\n")

def getIp6(device: str): #print(getIp4("bat0")) #print(getIp6("bat0")[0])
    cmd='ifconfig |grep "'+device+'" -A 5|grep -o "inet6 .*"|cut -d " " -f 2'
    p=subprocess.check_output(cmd, shell=True)
    addrs=p.decode().split("\n")[:-1]
    if len(addrs)>0:
        return addrs #return type is list
    else:
        return ["0"] #no ipv4 addrs to return!
# ----------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------
class AlfredReceiver:
    def __init__(self, callback):
        try:
            p=subprocess.check_output(["pgrep","alfred"])
        except:
            print("alfred not running! Please run mesh.py first.")
            quit()
        self.callback=callback
        self.run=True
        t=threading.Thread(target=self.__receiver)
        t.start()

    def __receiver(self):
        while self.run:
            for ch in CHANNELS:
                cmd='sudo alfred -r '+str(ch)
                p=subprocess.check_output(cmd.split(' ')) # p <- { "22:54:99:cc:14:05", "pia Testi 255" },
                if len(p)>0:
                    lines=p.decode().split("\n")
                    for line in lines:
                        if len(line)>0:
                            #print("LINE",line)
                            data=line.split(",")[:2]
                            sender = data[0].split('"')[1]
                            msg = data[1].split('"')[1]
                            key = sender + "_" + str(ch) #key 22:54:99:cc:14:05_253 address_channel
                            if MSGDICT.get(key) is None or MSGDICT.get(key) !=(ch,msg):
                                MSGDICT[key]=(ch,msg)
                                #print(MSGDICT)
                                if self.callback is not None:
                                    self.callback(sender, ch, msg)
            for i in range(0,5):
                if not self.run:
                    break
                time.sleep(1)

    def send(self, channel, message):
        cmd='echo -n "'+message+'" | sudo alfred -s '+str(channel)
        os.system(cmd)

    def stop(self):
        self.run=False
# ----------------------------------------------------------------------------------------------


def cback(sender,channel, msg): #callback when new data (changed) in alfdred
    print("MSG:", sender, channel, msg)

# ----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    k=0
    if len(sys.argv)>=2: #./alfredmsg.py 255 test message
        al=AlfredReceiver(None)
        ch=sys.argv[1]
        msg=" ".join(sys.argv[2:])
        al.send(ch, msg)
        #time.sleep(1)
        al.stop()
        quit()

    else: #./alfredmsg.py
        al=AlfredReceiver(cback)
    while RUN:
        k+=1
        #print("main", RUN)
        time.sleep(1)
        # if k==5:
        #     al.send(255, "Tama on testi")
        # if k==2:
        #     print(getMac("mesh-bridge"))
        #     print(getIp4("bat0"))
        #     print(getIp6("bat0")[0])

