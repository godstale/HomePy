#-*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class NotiInfo:
    def __init__(self):
        self.id = -1   # notification ID
        self.cat1 = -1     # category 1
        self.cat2 = -1     # category 2
        self.devid = -1    # device ID
        self.data1 = 0     # int data1
        self.data2 = 0     # int data2
        self.data3 = 0     # int data3
        self.data4 = 0     # int data4
        self.comp1 = 0     # comparison operator 1
        self.comp2 = 0     # comp op 2
        self.comp3 = 0     # 
        self.comp4 = 0     # 
        self.name = ""     # noti name
        self.time = 0      # timestamp

