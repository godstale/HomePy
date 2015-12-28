#-*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import Queue
import threading
import time
import logging

from HCProtocol import *
from DeviceInfo import *
from SensorInfo import *
from MacroInfo import *
from NotiInfo import *

############################################
# Device Manager thread
############################################

CALLBACK_TYPE_NOTI = 1
CALLBACK_TYPE_MACRO = 2

class DeviceManagerThread(threading.Thread):
    quit = False
    prev_db_clean_time = 0
    prev_timer_proc = 0
    CLEANING_INTERVAL = 60*10    # do DB cleaning every 10 min
    TIMER_CHECK_INTERVAL = 60    # do timer check every 1 min
    DEL_SENSOR_TIME = 3*24*60*60    # delete records older than 3 days

    def __init__(self, db, recv_queue, send_queue, callback):
        threading.Thread.__init__(self)
        self.devices = list()
        self.noti = list()
        self.macro = list()
        self.db = db
        self.recv_queue = recv_queue
        self.send_queue = send_queue
        self.callback = callback

    def run(self):
        print 'Worker thread: started!!'
        while True:
            # Get object from queue
            if self.recv_queue.empty() == False:
                recv = self.recv_queue.get()
                if not isinstance(recv, DeviceInfo):
                    print 'Critical error!!! recv is not a DeviceInfo object!!!'
                    # Send complete signal to queue
                    self.recv_queue.task_done()
                    continue

                # Process received information
                if recv.objtype == 1:    # object type == from received packet
                    if recv.cmd == 17:  # 0x11 : Register device
                        # find name with category1 and category2
                        recv.name = get_device_name(recv.cat1, recv.cat2)
                        # set location name
                        recv.loc = get_location_name(recv.devid)
                        # update device list
                        found = self.update_device(recv)
                        # push to DB
                        self.db.add_device(recv, found)
                        logging.warning('Register device: name = '+recv.name)

                    elif recv.cmd == 81: # 0x51 : Update sensor data
                        # check if device is exist
                        temp = self.get_device(recv.cat1, recv.cat2, recv.devid)
                        if temp is not None:
                            # push to DB
                            self.db.add_monitoring_data(recv)
                            # check if notification is enabled
                            noti_ids = self.check_noti(recv)
                            if len(noti_ids) > 0:
                                count = self.check_macro(noti_ids)    # do macro
                                print '    Found %d macro...' % count
                                if count < 1:
                                    self.callback(CALLBACK_TYPE_NOTI, recv, "")  # send notification
                            logging.warning('Update sensor value: cat1 = %d, cat2 = %d, devid = %d' % (recv.cat1, recv.cat2, recv, devid))

                    elif recv.cmd == 1: # 0x01 : Ping response
                        print '    Received Ping response...'

                    elif recv.cmd == 129: # 0x81 : Control signal response
                        print '    Received Control-Signal response...'

                # Send complete signal to queue
                self.recv_queue.task_done()

            # Remove old data
            if self.prev_db_clean_time + self.CLEANING_INTERVAL < int(time.time()):
                print '    Cleaning old data...'
                self.prev_db_clean_time = int(time.time())
                self.delete_sensor_all(self.DEL_SENSOR_TIME)

            if self.prev_timer_proc + self.TIMER_CHECK_INTERVAL < int(time.time()):
                print '    Check timer...'
                self.prev_timer_proc = int(time.time())
                self.check_timer_macro()

            if self.quit == True:
                break;

            # Do scheduled jobs here
            #
            time.sleep(0.1)

    # Load device informations from DB
    def load_devices(self):
        results = self.db.select_all_device()
        logging.warning('Load device info from DB: count = '+str(len(results)))
        for row in results:
            device_info = DeviceInfo()
            device_info.objtype = 1    # queue item type
            device_info.cat1 = int(row[1])  # cat1
            device_info.cat2 = int(row[2])  # cat2
            device_info.devid = int(row[3]) # device ID
            device_info.cmd = 0x11  # command (set dummy value)
            device_info.cmd1 = int(row[7])  # available cmd 1
            device_info.cmd1dtype = int(row[11])  # available cmd 1 - data type
            device_info.cmd2 = int(row[8])
            device_info.cmd2dtype = int(row[12])
            device_info.cmd3 = int(row[9])
            device_info.cmd3dtype = int(row[13])
            device_info.cmd4 = int(row[10])  # available cmd 4
            device_info.cmd4dtype = int(row[14])  # available cmd 4 - data type
            device_info.name = row[4]  # name
            device_info.loc = row[5]  # location
            device_info.time = int(row[6])  # timestamp
            self.add_device_to_list(device_info)
        return

    # Get specified device info
    # num is ordering number, not an array index
    def get_device_at(self, num):
        if len(self.devices) >= num and num > 0:
            return self.devices[num-1]
        return None

    # Get specified device info
    def get_device(self, cat1, cat2, did):
        for dev in self.devices:
            if (dev.cat1 == cat1
                    and dev.cat2 == cat2
                    and dev.devid == did):
                return dev
        return None

    # Get specified device info
    # devnum is ordering number, not an array index
    def get_ids_at(self, devnum):
        if devnum > 0 and len(self.devices) >= devnum:
            cat1 = self.devices[devnum-1].cat1
            cat2 = self.devices[devnum-1].cat2
            devid = self.devices[devnum-1].devid
            return cat1, cat2, devid
        return -1,-1,-1

    # Get device list
    def get_device_list(self):
        return self.devices

    # Add device to list (check duplicate)
    def add_device(self, device):
        self.update_device(device)

    # Add device to list (just add a new device)
    def add_device_to_list(self, device):
        self.devices.append(device)

    # Add/Update device to list and DB
    def update_device(self, device):
        found = 0
        for dev in self.devices:
            if (dev.cat1 == device.cat1
                    and dev.cat2 == device.cat2
                    and dev.devid == device.devid):
                # replace previous dev info
                self.devices[self.devices.index(dev)] = device
                found = found + 1

        if found < 1:
            self.devices.append(device)

        return found

    # Delete all devices from list and DB
    def delete_devices_all(self):
        self.devices = []
        return self.db.delete_devices_all()

    # Delete device from list and DB
    # num is ordering number, not an array index
    def delete_device_at(self, num):
        cat1, cat2, devid = self.get_ids_at(num)
        if cat1 < 0 or cat2 < 0 or devid < 0:
            return False
        if not self.delete_device(num-1):
            return False
        return self.db.delete_device(cat1, cat2, devid)

    # Delete nth device from list
    def delete_device(self, index):
        if len(self.devices) > index:
            del self.devices[index]
            return True
        return False

    # Get sensor value
    # num is ordering number, not an array index
    def get_sensor_val(self, num, count):
        cat1, cat2, devid = self.get_ids_at(num)
        if cat1 < 0 or cat2 < 0 or devid < 0:
            return []
        # querying DB
        results = self.db.select_sensor_val(cat1, cat2, devid, count)
        is_avail = 1
        is_found = [False, False, False, False, False, False]
        infos = []
        # parse results
        for row in results:
            info = SensorInfo()
            if int(row[4]) != 0:
                is_found[0] == True
            info.data1 = row[4]  # 0: int 1
            if int(row[5]) != 0:
                is_found[1] == True
            info.data2 = int(row[5])  # 1: int 2
            if int(row[6]) != 0:
                is_found[2] == True
            info.data3 = int(row[6])  # 2: int 3
            if int(row[7]) != 0:
                is_found[3] == True
            info.data4 = int(row[7])  # 3: int 4
            if int(row[8]) != 0:
                is_found[4] == True
            info.fdata1 = int(row[8])  # 4: float 1
            if int(row[9]) != 0:
                is_found[5] == True
            info.fdata2 = int(row[9])  # 5: float 2
            info.time = int(row[10])   # 6: timestamp
            infos.append(info)
        if is_found[0]:
            is_avail *= 2
        if is_found[1]:
            is_avail *= 3
        if is_found[2]:
            is_avail *= 5
        if is_found[3]:
            is_avail *= 7
        if is_found[4]:
            is_avail *= 11
        if is_found[5]:
            is_avail *= 13
        # reverse list order (move recent item to last)
        infos.reverse()
        return infos

    # Delete sensor records of specified device
    # num is ordering number, not an array index
    def delete_sensor_val(self, num, timestamp):
        cat1, cat2, devid = self.get_ids_at(num)
        if cat1 < 0 or cat2 < 0 or devid < 0:
            return False
        return self.db.delete_sensor_val(cat1, cat2, devid, timestamp)

    # Delete all sensor records
    def delete_sensor_all(self, timestamp):
        return self.db.delete_sensor_all(timestamp)

    # Load notifications from DB
    def load_noti(self):
        results = self.db.select_all_noti()
        logging.warning('Load notifications from DB: count = '+str(len(results)))
        for row in results:
            noti = NotiInfo()
            noti.id = int(row[0])     # id
            noti.cat1 = int(row[1])   # cat1
            noti.cat2 = int(row[2])   # cat2
            noti.devid = int(row[3])  # device ID
            noti.comp1 = int(row[4])    # comp 1
            noti.comp2 = int(row[5])    # comp 2
            noti.comp3 = int(row[6])    # comp 3
            noti.comp4 = int(row[7])    # comp 4
            noti.data1 = int(row[10])   # data 1
            noti.data2 = int(row[11])   # data 2
            noti.data3 = int(row[12])   # data 3
            noti.data4 = int(row[13])   # data 4
            noti.time = int(row[16])   # updated time
            noti.name = row[17]        # name
            self.add_noti_to_list(noti)

    # Get all notifications
    def get_noti_list(self):
        return self.noti

    # Get noti with id
    def get_noti_with_id(self, nid):
        for item in self.noti:
            if item.id == nid:
                return item
        return None

    # Get noti(s) with device parameters
    def get_noti_with_param(self, cat1, cat2, devid):
        notis = []
        for item in self.noti:
            if item.cat1 == cat1 and item.cat2 == cat2 and item.devid == devid:
                notis.append(item)
        return notis

    # Refresh noti list
    def refresh_noti_list(self):
        self.noti = []
        self.load_noti()

    # Add notification to DB and list. And update list again
    def add_noti(self, a_noti):
        if self.insert_noti(a_noti):
            self.refresh_noti_list()
            return True
        return False

    # Add notification to list
    def add_noti_to_list(self, a_noti):
        self.noti.append(a_noti)

    # Add notification to DB
    def insert_noti(self, a_noti):
        return self.db.add_noti(a_noti)

    # Delete noti with id
    def delete_noti_with_id(self, id):
        if self.db.delete_noti_with_id(id):
            # delete macro
            self.delete_macro_with_nid(id)
            self.refresh_noti_list()
            return True
        return False

    # Delete noti with device parameters
    def delete_noti_with_param(self, cat1, cat2, devid):
        if self.db.delete_noti_with_param(cat1, cat2, devid):
            # delete macro
            self.delete_macro_with_param(cat1, cat2, devid)
            self.refresh_noti_list()
            return True
        return False

    # Check if notification is available or not
    def check_noti(self, recv):
        notis = list()
        for row in self.noti:
            # compare category1, category2, device id
            if recv.cat1 == row.cat1 and recv.cat2 == row.cat2 and recv.devid == row.devid:
                noti_on = False
                # check data1
                if row.comp1 == 1:
                    if recv.data1 > row.data1:
                        noti_on = True
                    else:
                        continue
                elif row.comp1 == 2:
                    if recv.data1 >= row.data1:
                        noti_on = True
                    else:
                        continue
                elif row.comp1 == 3:
                    if recv.data1 == row.data1:
                        noti_on = True
                    else:
                        continue
                elif row.comp1 == 4:
                    if recv.data1 <= row.data1:
                        noti_on = True
                    else:
                        continue
                elif row.comp1 == 5:
                    if recv.data1 < row.data1:
                        noti_on = True
                    else:
                        continue
                elif row.comp1 == 6:
                    if recv.data1 != row.data1:
                        noti_on = True
                    else:
                        continue
                # check data2
                if row.comp2 == 1:
                    if recv.data2 > row.data2:
                        noti_on = True
                    else:
                        continue
                elif row.comp2 == 2:
                    if recv.data2 >= row.data2:
                        noti_on = True
                    else:
                        continue
                elif row.comp2 == 3:
                    if recv.data2 == row.data2:
                        noti_on = True
                    else:
                        continue
                elif row.comp2 == 4:
                    if recv.data2 <= row.data2:
                        noti_on = True
                    else:
                        continue
                elif row.comp2 == 5:
                    if recv.data2 < row.data2:
                        noti_on = True
                    else:
                        continue
                elif row.comp2 == 6:
                    if recv.data2 != row.data2:
                        noti_on = True
                    else:
                        continue
                # check data3
                if row.comp3 == 1:
                    if recv.data3 > row.data3:
                        noti_on = True
                    else:
                        continue
                elif row.comp3 == 2:
                    if recv.data3 >= row.data3:
                        noti_on = True
                    else:
                        continue
                elif row.comp3 == 3:
                    if recv.data3 == row.data3:
                        noti_on = True
                    else:
                        continue
                elif row.comp3 == 4:
                    if recv.data3 <= row.data3:
                        noti_on = True
                    else:
                        continue
                elif row.comp3 == 5:
                    if recv.data3 < row.data3:
                        noti_on = True
                    else:
                        continue
                elif row.comp3 == 6:
                    if recv.data3 != row.data3:
                        noti_on = True
                    else:
                        continue
                # check data4
                if row.comp4 == 1:
                    if recv.data4 > row.data4:
                        noti_on = True
                    else:
                        continue
                elif row.comp4 == 2:
                    if recv.data4 >= row.data4:
                        noti_on = True
                    else:
                        continue
                elif row.comp4 == 3:
                    if recv.data4 == row.data4:
                        noti_on = True
                    else:
                        continue
                elif row.comp4 == 4:
                    if recv.data4 <= row.data4:
                        noti_on = True
                    else:
                        continue
                elif row.comp4 == 5:
                    if recv.data4 < row.data4:
                        noti_on = True
                    else:
                        continue
                elif row.comp4 == 6:
                    if recv.data4 != row.data4:
                        noti_on = True
                    else:
                        continue
            if noti_on:
                notis.append(row.id)    # Add noti id

        return notis

    # Check if macro is available or not (noti triggered)
    def check_macro(self, noti_ids):
        count = 0
        for noti_id in noti_ids:
            for row in self.macro:
                # compare notification id
                if noti_id == row.nid:
                    row.time = time.time()
                    self.db.update_macro_time(row.id, row.time)
                    self.callback(CALLBACK_TYPE_MACRO, None, row.cmd)  # process command
                    count += 1
        return count

    # Check if timer-macro is available or not (time triggered)
    def check_timer_macro(self):
        count = 0
        for row in self.macro:
            # check interval timer macro
            if row.interval > 0:
                if row.time + row.interval*60 < time.time():
                    row.time = time.time()
                    self.db.update_macro_time(row.id, row.time)
                    self.callback(CALLBACK_TYPE_MACRO, None, row.cmd)  # process command
                    count += 1
            # check reserved timer macro
            elif row.interval < 1 and row.nid < 0:
                now = time.localtime()
                if now.tm_hour == row.hour and now.tm_min == row.minute:
                    row.time = time.time()
                    self.db.update_macro_time(row.id, row.time)
                    self.callback(CALLBACK_TYPE_MACRO, None, row.cmd)  # process command
                    count += 1
        return count

    # Load macro from DB
    def load_macro(self):
        results = self.db.select_all_macro()
        logging.warning('Load macro info from DB: count = '+str(len(results)))
        for row in results:
            a_macro = MacroInfo()
            a_macro.id = int(row[0])    # id
            a_macro.nid = int(row[1])    # noti id
            a_macro.cat1 = int(row[2])    # cat1
            a_macro.cat2 = int(row[3])    # cat2
            a_macro.devid = int(row[4])    # device ID
            a_macro.time = int(row[5])    # updated
            a_macro.cmd = row[6]    # command
            a_macro.interval = int(row[7])    # interval (for timer)
            a_macro.hour = int(row[8])    # reserved time (hour, for timer)
            a_macro.minute = int(row[9])    # reserved time (min, for timer)
            self.add_macro_to_list(a_macro)

    # Get all macro
    def get_macro_list(self):
        return self.macro

    # Get macro with id
    def get_macro_with_id(self, mid):
        for item in self.macro:
            if item.id == mid:
                return item
        return None

    # Refresh macro list
    def refresh_macro_list(self):
        self.macro = []
        self.load_macro()

    # Add macro to DB and update list
    def add_macro(self, o_macro):
        if self.insert_macro(o_macro):
            self.refresh_macro_list()
            return True
        return False

    # Add macro to list
    def add_macro_to_list(self, o_macro):
        self.macro.append(o_macro)

    # Add macro to DB
    def insert_macro(self, o_macro):
        return self.db.add_macro(o_macro)

    # Delete macro with id
    def delete_macro_with_id(self, id):
        if self.db.delete_macro_with_id(id):
            self.refresh_macro_list()
            return True
        return False

    # Delete macro with noti id
    def delete_macro_with_nid(self, nid):
        if self.db.delete_macro_with_nid(nid):
            self.refresh_macro_list()
            return True
        return False

    # Delete noti with device parameters
    def delete_macro_with_param(self, cat1, cat2, devid):
        if self.db.delete_macro_with_param(cat1, cat2, devid):
            self.refresh_macro_list()
            return True
        return False


    # Exit thread
    def close(self):
        self.quit = True

    # End of class DeviceManagerThread
    pass

