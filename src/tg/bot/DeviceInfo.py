#-*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

########################################
# incoming packet
#
# packet length = 15
# (byte order: description)
# 1: 0x55  (fixed)
# 2: 0xfe  (fixed)
# 3: category 1
# 4: category 2
# 5: ID
# 6: command
# 7: Data1 (upper byte) / command 1 type
# 8: Data1 (lower byte) / command 1 data type
# 9: Data2 / command 2 type
# 10: Data2 / command 2 data type
# 11: Data3 / command 3 type
# 12: Data3 / command 3 data type
# 13: Data4 / command 4 type
# 14: Data4 / command 4 data type
# 15: 0xff  (fixed)

class DeviceInfo:
    def __init__(self):
        self.objtype = 1   # object type, 1: from received packet
        self.cat1 = -1     # category 1
        self.cat2 = -1     # category 2
        self.devid = -1    # device ID
        self.cmd = -1      # command
        self.data1 = 0     # int data1
        self.data2 = 0     # int data2
        self.data3 = 0     # int data3
        self.data4 = 0     # int data4
        self.fdata1 = 0    # float data1 (not available yet)
        self.fdata2 = 0    # float data2 (not available yet)
        self.dummy1 = 0    # dummy1
        self.dummy2 = 0    # dummy2
        self.name = ""     # device name
        self.loc = ""      # location
        self.time = 0      # timestamp
        self.cmd1 = 0      # acceptable command 1
        self.cmd1dtype = 0 # acceptable command 1 - data type
        self.cmd2 = 0      # acceptable command 2
        self.cmd2dtype = 0 # acceptable command 2 - data type
        self.cmd3 = 0      # acceptable command 3
        self.cmd3dtype = 0 # acceptable command 3 - data type
        self.cmd4 = 0      # acceptable command 4
        self.cmd4dtype = 0 # acceptable command 4 - data type

