#!/usr/bin/env python3
import re
import subprocess
import os

def usb_availiable():
    '''device_re = re.compile(b"Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w:\+)\s(?P<tag>.+)$", re.I)
    df=subprocess.check_output('lsusb')
    devices = []
    for i in df.split(b'\n'):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                devices.append(dinfo)
    print(devices)
    if devices:
        return True
    return False'''
    if os.path.exists('/dev/sda') and os.path.ismount('/mnt') == False:
        #os.system('sudo mount /dev/sda1 /mnt')
        return True
    
    else:
        return False

def main():
    bool = usb_availiable()
    print("function returned " + str(bool))
    return 0


if __name__ == '__main__':
    main()