#!/usr/bin/python

import subprocess
import shellscript

adbpath = '..\\platform-tools\\.\\adb'
serial = ""


def adbshell(commands):
    args = [adbpath]
    if serial is not None:
        args.append('-s')
        args.append(serial)
    # args.append('shell')
    for com in commands:
        args.append(com)
    print(args)
    return subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)

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

adbdevices()

adbshell([" tcpip", " 5555"])
adbshell([" shell"," \"ifconfig | grep -A 1 wlan0 | tail -n 1 | cut -f2 -d: | cut -f1 -d\' \'\""])
adbshell([" connect"," 192.168.1.5:5555"])