#!/usr/bin/python


..\platform-tools\adb.exe tcpip 5555
..\platform-tools\adb.exe shell "ifconfig | grep -A 1 wlan0 | tail -n 1 | cut -f2 -d: | cut -f1 -d' '"
..\platform-tools\adb.exe connect 192.168.1.5:5555


def adbshell(command):
    args = [adbpath]
    if serial is not None:
        args.append('-s')
        args.append(serial)
    args.append('shell')
    args.append(command)
    # print(args)
    return subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
