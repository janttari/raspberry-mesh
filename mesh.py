#!/usr/bin/env python3
import sys, os, time, subprocess
DEBUG=True
KANAVA=40 #36

def lokita (*args):
    if DEBUG:
        print("["+time.strftime("%H:%M:%S")+"]", end=" ")
        for a in args:
            print(a, end=" ")
        print()

def usage():
    print("Usage:")
    print(sys.argv[0]+" {gateway|client} {up|down}")
    quit()

def getserial_mac():
    with open('/proc/cpuinfo') as f:
        lines=f.readlines()
    for line in lines:
        if line.startswith("Serial"):
            line=line.split(":")[1][-9:]
            ser="00:00:"+line[0:2]+":"+line[2:4]+":"+line[4:6]+":"+line[6:8]
    return ser

def run_cmd(command): #run shell command and wait it's done
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if len(err)>0:
        lokita("*ERR", err)


def check_cmd_bool(command): #returns command output as True or False
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if len(err)>0:
        lokita("*ERR", err)

    #lokita(out[0])
    #lokita(len(out[0]))
    if len(out) == 0:
        outbool=False
    else:
        outbool=True
    return outbool

#def get_phy():
#    process = subprocess.Popen('iw list|head -n 1|cut -d " " -f 2', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#    out, err = process.communicate()
#    if len(err)>0:
#        lokita("*ERR", err)
#    return out[:-1].decode()

def wait_for(command, tf=True): #wait until output command returns True or False
    while True:
        #lokita("wait...")
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if len(err)>0:
            lokita("*ERR", err)
        if len(out) == 0:
            outbool=False
        else:
            outbool=True
        if outbool == tf:
            break
        time.sleep(0.1)

def mesh_up():
    lokita("mesh up")
    if check_cmd_bool('iwconfig 2>/dev/null |grep mesh0'):
        lokita("mesh0 löytyy jo. aja alas ensin!")
        quit()
    if not check_cmd_bool('lsusb | grep "0e8d:7612"'):
        lokita("7612 ei ole!")
        run_cmd('sudo usb_modeswitch -K -W -v 0e8d -p 2870 -Q')
        wait_for('lsusb | grep "0e8d:7612"')
        lokita("7612 löytyi")
    lokita('batman V')
    run_cmd('sudo modprobe batman-adv && sudo batctl ra BATMAN_V')
    lokita("odottaa laitetta wlan1")
    wait_for('iwconfig 2>/dev/null|grep wlan1', True)
    lokita("wlan1 löytyi")
    time.sleep(1)
    ser=getserial_mac()
    run_cmd('sudo iw dev wlan1 interface add mesh0 type mp addr '+ser+' mesh_id MYMESHID')
    lokita("Odotetaan mesh0 ilmestymistä")
    wait_for('iwconfig 2>/dev/null | grep mesh0', True)
    lokita("mesh0 ilmestynyt")
    lokita("odotetaan mesh0 tilaa")
    wait_for('cat /sys/class/net/mesh0/operstate |grep dormant', True)
    lokita("mesh0 tila ok")
    time.sleep(2)
    lokita("ajetaan alas")
    run_cmd('sudo ifconfig wlan1 down')
    lokita("mesh0 alas")
    run_cmd('sudo ifconfig mesh0 down')
    #wait_for('cat /sys/class/net/mesh0/operstate |grep down', False)
    #time.sleep(1)
    lokita("vaihda kanava wlan1")
    run_cmd('sudo iwconfig wlan1 channel '+str(KANAVA))
    #time.sleep(1)
    lokita("vaihda kanava mesh0")
    run_cmd('sudo iwconfig mesh0 channel '+str(KANAVA))
    run_cmd('sudo ip link set mtu 1532 dev mesh0')
    #time.sleep(1)
    lokita("aja ylös")
    run_cmd('sudo ifconfig mesh0 up')
    lokita("odottaa laitetta mesh0")
    wait_for('iwconfig 2>/dev/null | grep mesh0', True)
    lokita('laite mesh0 löytyi')
    time.sleep(0.5)
    lokita('ajetaan batctl')
    run_cmd('sudo batctl if add mesh0')
    if sys.argv[1] == "gateway":
        run_cmd('sudo batctl gw_mode server')
    elif sys.argv[1] == "client":
        run_cmd('sudo batctl gw_mode server')
    run_cmd('sudo ip link add name mesh-bridge type bridge')
    #sudo ip link set dev eth0 master mesh-bridge
    #time.sleep(1)
    lokita("lisätään mesh-bridge")
    run_cmd('sudo ip link set dev bat0 master mesh-bridge')
    #time.sleep(1)
    lokita("mesh-bridge up")
    run_cmd('sudo ifconfig mesh-bridge up')
    lokita("odotetaan laitetta mesh-bridge")
    wait_for('cat /sys/class/net/mesh-bridge/operstate 2>/dev/null|grep up', True)
    time.sleep(2)
    lokita("ajetaan alfred")
    os.system('sudo alfred -i mesh-bridge -m >/dev/null 2>/dev/null &')
    time.sleep(1)
    alf=check_cmd_bool("pgrep alfred")
    lokita("Alfredin ajo onnistui", alf)
    lokita("b.a.t.m.a.n", sys.argv[1], "running...")



def mesh_down():
    lokita("mesh down")
    if not check_cmd_bool('iwconfig 2>/dev/null |grep mesh0'):
        lokita("mesh0 ei ole käynnissä, ei voi ajaa alas")
        quit()
    run_cmd('sudo iw dev mesh0 del')
    run_cmd('sudo batctl if del bat0')
    run_cmd('sudo ip link del mesh-bridge')
    run_cmd('sudo rmmod batman_adv')
    run_cmd('sudo killall -9 alfred 2>/dev/null') #!TODO voisko tehdä nätimmin kenties?
    lokita("b.a.t.m.a.n", sys.argv[1], "stopped...")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()
    if sys.argv[1] not in ["gateway", "client"]:
        print("unknown mode", sys.argv[1])
        usage()
    if sys.argv[2] == "up":
        mesh_up()
    elif sys.argv[2] == "down":
        mesh_down()
    else:
        usage()

