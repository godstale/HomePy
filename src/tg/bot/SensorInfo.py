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
# 7: Data1 (upper byte)
# 8: Data1 (lower byte)
# 9: Data2
# 10: Data2
# 11: Data3
# 12: Data3
# 13: Data4
# 14: Data4
# 15: 0xff  (fixed)

class SensorInfo:
    def __init__(self):
        self.cat1 = -1     # category 1
        self.cat2 = -1     # category 2
        self.devid = -1    # device ID
        self.data1 = 0     # int data1
        self.data2 = 0     # int data2
        self.data3 = 0     # int data3
        self.data4 = 0     # int data4
        self.fdata1 = 0    # float data1 (not available yet)
        self.fdata2 = 0    # float data2 (not available yet)
        self.time = 0      # timestamp

