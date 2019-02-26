#!/usr/bin/python

from __future__ import print_function
import sys
import binascii
import bluepy
import os

ble_conn = None
HRs = []

class MyDelegate(bluepy.btle.DefaultDelegate):

    def __init__(self, conn):
        bluepy.btle.DefaultDelegate.__init__(self)
        self.conn = conn

    def handleNotification(self, cHandle, data):
        data = binascii.b2a_hex(data)
        HR=int(data[-2:-1], 16)*16+int(data[-1:], 16)
        HRs.append(HR)
        print("Notification:", str(cHandle), " data ", data)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            pass
        elif isNewData:
            print("\\nDiscovery:", "MAC:", dev.addr, " Rssi ", str(dev.rssi))


def ble_connect(devAddr):

    global ble_conn
    if not devAddr is None and ble_conn is None:
        ble_conn = bluepy.btle.Peripheral(devAddr, bluepy.btle.ADDR_TYPE_RANDOM)
        ble_conn.setDelegate(MyDelegate(ble_conn))
        print("connected")


def ble_disconnect():

    global ble_conn
    ble_conn = None
    print("disconnected")


if __name__ == '__main__':

    ble_mac = "FF:C1:28:73:E3:5C"

    # scan
    # scanner = bluepy.btle.Scanner().withDelegate(MyDelegate(None))
    # timeout = 30.0
    # devices = scanner.scan(timeout)
    # for dev in devices:
    #     if dev.addr == ble_mac:
    #         print("\\nDiscovery:", "MAC:", dev.addr, " Rssi ", str(dev.rssi))
    #         for (adtype, desc, value) in dev.getScanData():
    #             print(" %s(0x%x) = %s" % (desc, int(adtype), value))
    #         break



    # connect
    ble_connect(ble_mac)
    # print(ble_conn)
    # print(bluepy.btle.Peripheral.getCharacteristics(ble_conn, startHnd=1, endHnd=0xFFFF, uuid=None))

    # write , set listen

    snd_content_str = b'\x01\x00'
    handle = 0x0014
    ble_conn.writeCharacteristic(handle, snd_content_str, withResponse=True)

    # wait notification
    while True:
        if ble_conn.waitForNotifications(1.0):
            continue
        print(HRs[-10:])
        print("Waiting...")

    # disconnect
    ble_disconnect()