#!/usr/bin/env python3
import pyalfred
import time, threading, signal,sys

CHANNELS=[64,128] #channels [data types] to listen

#try in another pi: 'echo -n "test test test"|sudo alfred -s 128'

def signal_handler(sig, frame):
    print('\nCTRL+c. Stopping threads...')
    RUN=False
    alf.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


class PyAlfMsg: #----------------------------------------------------------------------------------
    def __init__(self, msg_callback):
        self.msg_callback = msg_callback
        self.run=True
        self.th_alfReceiver=(threading.Thread(target=self.__alfReceiver))
        self.th_alfReceiver.start()
    
    def __alfReceiver(self):
        self.lastdata={}
        self.ac = pyalfred.AlfredConnection()
        self.msgdict={}
        while self.run:
            for ch in CHANNELS:
                data = self.ac.fetch(ch)
                for mac in data:
                    msg=data[mac]
                    key = mac + "_" + str(ch) #key 22:54:99:cc:14:05_253 address_channel
                    if self.msgdict.get(key) is None or self.msgdict.get(key) !=(ch,msg):
                        self.msgdict[key]=(ch,msg)
                        msg=data[mac]
                        if self.msg_callback:
                            self.msg_callback(ch, mac, msg)
            for i in range(0,10):
                time.sleep(0.1)
                if not self.run:
                    break

    def send(self, channel, message):
        self.ac.send(channel, message)

    def stop(self):
        self.run=False
#--------------------------------------------------------------------------------------------------

def on_message(ch, mac, message): #callback when new alfred message
    print("*", ch, mac, message)

k=0
alf=PyAlfMsg(on_message)
while True:
    k+=1
    if k == 5:
        alf.send(64,"test"+str(time.time()))
    if k == 9:
        alf.send(128,"128BBB"+str(time.time()))
    time.sleep(1)

