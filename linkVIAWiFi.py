#!/usr/bin/python

import subprocess
import shellscript

adbpath = '..\platform-tools\\adb.exe'
serial = ""


def adbshell(commands):
    # args = [adbpath]
    # # subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
    # # args=[]
    # if serial is not None:
    #     # args.append('-s')
    #     # args.append(serial)
        

    #     # args.append('shell')
    #     for com in commands:
    #         args.append(com)
    print(commands)
    return subprocess.Popen(commands, shell=True, stdout=subprocess.PIPE).stdout.read()

def adbdevices():
    # create a tuple with the arguments for the command
    args = [adbpath]
    args.append('devices')
    # run command to shell (This is not hazardos while shell=True because
    # the args input is not dependant in user input)
    child = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
    # split the bytes string where I can get the serial of the device
    print(args)
    bSerial = child.stdout.read().split(b'\n')[1].split(b'\t')[0]
    # decode the bytes into string
    return bSerial.decode()


serial = adbdevices()
print("serial found:" +  serial)
# adbshell([" shell ","ifconfig"])

# adbshell([" shell"])
# adbshell([adbpath + ' "tcpip 5555"'])
print(adbshell([adbpath + ' tcpip 5555']))
# ipFound = adbshell([' shell ',' ifconfig ', '| grep -A 1 wlan0 ','| tail -n 1','| cut -f2 -d: ','| cut -f1 -d' '"'])
# print("IP device found: " + ipFound)
# adbshell([" connect ",ipFound,":5555"])


# .\platform-tools\adb.exe tcpip 5555
# .\platform-tools\adb.exe shell "ifconfig | grep -A 1 wlan0 | tail -n 1 | cut -f2 -d: | cut -f1 -d' '"
# .\platform-tools\adb.exe connect 192.168.1.5:5555