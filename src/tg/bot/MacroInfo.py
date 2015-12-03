#-*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class MacroInfo:
    def __init__(self):
        self.id = -1    # ID
        self.nid = -1   # notification ID (target ID)
        self.cat1 = -1     # category 1
        self.cat2 = -1     # category 2
        self.devid = -1    # device ID
        self.time = 0      # timestamp (for timer)
        self.cmd = ""      # command
        self.interval = 0  # time interval (minute, for timer)

