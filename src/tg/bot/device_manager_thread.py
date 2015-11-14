#-*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import Queue
import threading
import time
from hc_protocol import *


############################################
# Device Manager thread
############################################

CALLBACK_TYPE_NOTI = 1

class DeviceManagerThread(threading.Thread):
    quit = False
    prev_db_clean_time = 0
    CLEANING_INTERVAL = 60*10    # do DB cleaning every 10 min
    DEL_SENSOR_TIME = 3*24*60*60    # delete records older than 3 days

    def __init__(self, db, recv_queue, send_queue, callback):
        threading.Thread.__init__(self)
        self.devices = list()
        self.noti = list()
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

                # Process received information
                if recv[0] == 1:    # received packet
                    if recv[4] == 17:  # 0x11 : Register device
                        # find name with category1 and category2
                        recv[13] = get_device_name(recv[1], recv[2])
                        # set location name
                        recv[14] = get_location_name(recv[3])
                        # update device list
                        found = self.update_device(recv)
                        # push to DB
                        self.db.add_device(recv, found)

                    elif recv[4] == 81: # 0x51 : Update sensor data
                        # push to DB
                        self.db.add_monitoring_data(recv)
                        # check if notification is enabled
                        if self.check_noti(recv):
                            self.callback(CALLBACK_TYPE_NOTI, recv)

                    elif recv[4] == 1: # 0x01 : Ping response
                        print ' '

                    elif recv[4] == 129: # 0x81 : Control signal response
                        print ' '

                # Send complete signal to queue
                self.recv_queue.task_done()

            if self.prev_db_clean_time + self.CLEANING_INTERVAL < int(time.time()):
                print '    Cleaning old data...'
                self.prev_db_clean_time = int(time.time())
                self.delete_sensor_all(self.DEL_SENSOR_TIME)

            if self.quit == True:
                break;

            # Do scheduled jobs here
            #
            time.sleep(0.1)

    # Load device informations from DB
    def load_devices(self):
        results = self.db.select_all_device()
        for row in results:
            device_info = []
            device_info.append(1)    # queue item type
            device_info.append(int(row[1]))  # cat1
            device_info.append(int(row[2]))  # cat2
            device_info.append(int(row[3]))  # device ID
            device_info.append(0x11)  # command
            device_info.append(int(row[7]))  # available cmd 1
            device_info.append(int(row[11]))  # available cmd 1 - data type
            device_info.append(int(row[8]))
            device_info.append(int(row[12]))
            device_info.append(int(row[9]))
            device_info.append(int(row[13]))
            device_info.append(int(row[10]))  # available cmd 4
            device_info.append(int(row[14]))  # available cmd 4 - data type
            device_info.append(row[4])  # name
            device_info.append(row[5])  # location
            device_info.append(row[6])  # timestamp
            self.add_device_to_list(device_info)

    # Get specified device info
    # num is ordering number, not an array index
    def get_device_at(self, num):
        if len(self.devices) >= num and num > 0:
            return self.devices[num-1]
        return []

    # Get specified device info
    def get_device(self, cat1, cat2, did):
        for dev in self.devices:
            if (dev[1] == cat1
                    and dev[2] == cat2
                    and dev[3] == did):
                return dev
        return []

    # Get specified device info
    # devnum is ordering number, not an array index
    def get_ids_at(self, devnum):
        if devnum > 0 and len(self.devices) >= devnum:
            cat1 = self.devices[devnum-1][1]
            cat2 = self.devices[devnum-1][2]
            devid = self.devices[devnum-1][3]
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
            if (dev[1] == device[1]
                    and dev[2] == device[2] 
                    and dev[3] == device[3]):
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
            info = []
            if int(row[4]) != 0:
                is_found[0] == True
            info.append(row[4])  # 0: int 1
            if int(row[5]) != 0:
                is_found[1] == True
            info.append(int(row[5]))  # 1: int 2
            if int(row[6]) != 0:
                is_found[2] == True
            info.append(int(row[6]))  # 2: int 3
            if int(row[7]) != 0:
                is_found[3] == True
            info.append(int(row[7]))  # 3: int 4
            if int(row[8]) != 0:
                is_found[4] == True
            info.append(int(row[8]))  # 4: float 1
            if int(row[9]) != 0:
                is_found[5] == True
            info.append(int(row[9]))  # 5: float 2
            info.append(int(row[10])) # 6: timestamp
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
        return is_avail, infos

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
        for row in results:
            noti = []
            noti.append(int(row[0]))    # id
            noti.append(int(row[1]))    # cat1
            noti.append(int(row[2]))    # cat2
            noti.append(int(row[3]))    # device ID
            noti.append(int(row[4]))    # comp 1
            noti.append(int(row[5]))    # comp 2
            noti.append(int(row[6]))    # comp 3
            noti.append(int(row[7]))    # comp 4
            noti.append(int(row[10]))   # data 1
            noti.append(int(row[11]))   # data 2
            noti.append(int(row[12]))   # data 3
            noti.append(int(row[13]))   # data 4
            noti.append(int(row[16]))   # updated time
            noti.append(row[17])        # name
            self.add_noti_to_list(noti)

    # Get all notifications
    def get_noti_list(self):
        return self.noti

    # Get noti with id
    def get_noti_with_id(self, nid):
        for item in self.noti:
            if item[0] == nid:
                return item
        return []

    # Get noti(s) with device parameters
    def get_noti_with_param(self, cat1, cat2, devid):
        notis = []
        for item in self.noti:
            if item[1] == cat1 and item[2] == cat2 and item[3] == devid:
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
            self.refresh_noti_list()
            return True
        return False

    # Delete noti with device parameters
    def delete_noti_with_param(self, cat1, cat2, devid):
        if self.db.delete_noti_with_param(cat1, cat2, devid):
            self.refresh_noti_list()
            return True
        return False

    # Delete noti with name
    def delete_noti_with_name(self, name):
        if self.db.delete_noti_with_name(name):
            self.refresh_noti_list()
            return True
        return False

    # Check if notification is available or not
    def check_noti(self, recv):
        is_ok = False
        for row in self.noti:
            if recv[1] == row[1] and recv[2] == row[2] and recv[3] == row[3]:
                noti_on = False
                # check data1
                if row[4] == 1:
                    if recv[5] > row[8]:
                        noti_on = True
                    else:
                        continue
                elif row[4] == 2:
                    if recv[5] >= row[8]:
                        noti_on = True
                    else:
                        continue
                elif row[4] == 3:
                    if recv[5] == row[8]:
                        noti_on = True
                    else:
                        continue
                elif row[4] == 4:
                    if recv[5] <= row[8]:
                        noti_on = True
                    else:
                        continue
                elif row[4] == 5:
                    if recv[5] < row[8]:
                        noti_on = True
                    else:
                        continue
                elif row[4] == 6:
                    if recv[5] != row[8]:
                        noti_on = True
                    else:
                        continue
                # check data2
                if row[5] == 1:
                    if recv[6] > row[9]:
                        noti_on = True
                    else:
                        continue
                elif row[5] == 2:
                    if recv[6] >= row[9]:
                        noti_on = True
                    else:
                        continue
                elif row[5] == 3:
                    if recv[6] == row[9]:
                        noti_on = True
                    else:
                        continue
                elif row[5] == 4:
                    if recv[6] <= row[9]:
                        noti_on = True
                    else:
                        continue
                elif row[5] == 5:
                    if recv[6] < row[9]:
                        noti_on = True
                    else:
                        continue
                elif row[5] == 6:
                    if recv[6] != row[9]:
                        noti_on = True
                    else:
                        continue
                # check data3
                if row[6] == 1:
                    if recv[7] > row[10]:
                        noti_on = True
                    else:
                        continue
                elif row[6] == 2:
                    if recv[7] >= row[10]:
                        noti_on = True
                    else:
                        continue
                elif row[6] == 3:
                    if recv[7] == row[10]:
                        noti_on = True
                    else:
                        continue
                elif row[6] == 4:
                    if recv[7] <= row[10]:
                        noti_on = True
                    else:
                        continue
                elif row[6] == 5:
                    if recv[7] < row[10]:
                        noti_on = True
                    else:
                        continue
                elif row[6] == 6:
                    if recv[7] != row[10]:
                        noti_on = True
                    else:
                        continue
                # check data4
                if row[7] == 1:
                    if recv[8] > row[11]:
                        noti_on = True
                    else:
                        continue
                elif row[7] == 2:
                    if recv[8] >= row[11]:
                        noti_on = True
                    else:
                        continue
                elif row[7] == 3:
                    if recv[8] == row[11]:
                        noti_on = True
                    else:
                        continue
                elif row[7] == 4:
                    if recv[8] <= row[11]:
                        noti_on = True
                    else:
                        continue
                elif row[7] == 5:
                    if recv[8] < row[11]:
                        noti_on = True
                    else:
                        continue
                elif row[7] == 6:
                    if recv[8] != row[11]:
                        noti_on = True
                    else:
                        continue
            if noti_on:
                is_ok = True

        return is_ok


    # Exit thread
    def close(self):
        self.quit = True

    # End of class DeviceManagerThread
    pass

