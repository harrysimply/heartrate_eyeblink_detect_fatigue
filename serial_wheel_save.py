#!usr/bin/python
#coding=gbk

#https://www.cnblogs.com/dongxiaodong/p/9992083.html

import serial
import sys
import os
import time
import re
from time import sleep

import os, struct, array
from fcntl import ioctl

# Iterate over the joystick devices.
print('Available devices:')

for fn in os.listdir('/dev/input'):
    if fn.startswith('js'):
        print('  /dev/input/%s' % (fn))
#这句显示手柄在硬件中的端口位置： /dev/input/js0
# We'll store the states here.
axis_states = {}
button_states = {}


#先前校验时，方向盘是x,左侧踏板是z,右侧踏板是rz。


# These constants were borrowed from linux/input.h
axis_names = {
    0x00 : 'x',
    0x02 : 'z',
    0x05 : 'rz',

}



axis_map = []

# Open the joystick device.
fn = '/dev/input/js0'
print('Opening %s...' % fn)
jsdev = open(fn, 'rb')

# # Get the device name.
buf = array.array('u', ['\0']*5)
ioctl(jsdev, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
js_name = buf.tostring()
print('Device name: %s' % js_name)

# Get number of axes and buttons.
buf = array.array('B', [0])
ioctl(jsdev, 0x80016a11, buf) # JSIOCGAXES
num_axes = buf[0]

# Get the axis map.
buf = array.array('B', [0] * 0x40)
ioctl(jsdev, 0x80406a32, buf) # JSIOCGAXMAP
#
for axis in buf[:num_axes]:
    axis_name = axis_names.get(axis, 'unknown(0x%02x)' % axis)
    axis_map.append(axis_name)
    axis_states[axis_name] = 0.0
try:
    #portx="COM3"
    portx = "/dev/ttyUSB0"
    bps=115200
    timex=5
    ser =serial.Serial(portx,bps,timeout=timex)

    # Main event loop
    while True:
        evbuf = jsdev.read(8)

        if evbuf:
            time, value, type, number = struct.unpack('IhBB', evbuf)

            if type & 0x02:
                axis = axis_map[number]
                if axis:
                    #print("{}".format(axis))
                    if axis=="x":

                        fvalue = value / 32767

                        res=int(((fvalue+1)/2)*8)
                        res=res

                        #print ("%s: %d" % (axis, res))

                    # if axis == "z":
                    #     #print(value)
                    #
                    #
                    #     fvalue = value / 32767
                    #
                    #     res=int(((fvalue+1)/2)*8)   #改成 32   2^5
                    #     res=res+8
                    #
                    #     #print ("%s: %d" % (axis, res))
                    #
                    #
                    #
                    # if axis == "rz":
                    #     #print(value)
                    #
                    #     fvalue = value / 32767
                    #
                    #     res = int(((fvalue+1)/2)*8)
                    #     res=res+16
                    #
                    #     #print ("%s: %d" % (axis, res))



                    #res=bin(res).replace('0b','')

                    #res=bytes(res)
                    sleep(0.5)
                    #res=bytearray(3)
                    #print(res)


                    #res=1
                    #result =ser.write('\x01'.encode())
                    result = ser.write(res)
                    print('s_write:',result)

                    # buffer =b''
                    # while True:
                    #     buffer=ser.read_all()
                    #     if buffer == '':
                    #         continue
                    #     else:
                    #         break

                    #print("写的内容：", result)
                    buffer = ser.read_all()

                    print("receive:",buffer)
                    # ret=int.from_bytes(buffer,byteorder = 'big')
                    #ret=struct.unpack('i',buffer)
                    #print(a)
                    #ret=struct.unpack("f",buffer)
                    #ret=gzip.decompress(buffer).decode("utf-8")
                    # print("读的内容：", ret)



except Exception as e:
    print("--异常--：",e)

#python对串口蓝牙模块的操作https://www.jianshu.com/p/7d35eb953eb9
#Ubuntu下cutecom图像界面串口调试工具使用详细https://blog.csdn.net/zhaoqi2617/article/details/72238546
#python对串口蓝牙模块的操作https://www.jianshu.com/p/7d35eb953eb9
#https://pyserial.readthedocs.io/en/latest/pyserial.html#overview

