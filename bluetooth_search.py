#!/usr/bin/env python
# --*--coding=utf-8--*--
# P191
# sudo pip install pybluez

import time
from bluetooth import *

alreadyFound = []


def findDevs():
    foundDevs = discover_devices(lookup_names=True)
    for (addr, name) in foundDevs:
        if addr not in alreadyFound:
            print
            "[*] Found Bluetooth Device :  " + str(name)
            print
            "[+] MAC address :  " + str(addr)
            alreadyFound.append(addr)


while True:
    findDevs()
    time.sleep(5)