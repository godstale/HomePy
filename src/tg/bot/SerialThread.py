#-*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import Queue
import threading
import serial
import time
import array
import logging

from DeviceInfo import *


############################################
# Global variables
############################################

# Parsing
PACKET_LEN = 15
IN_START1 = 0x55
IN_START2 = 0xfe
IN_END = 0xff
OUT_START1 = 0x78
OUT_START2 = 0xfe
OUT_END = 0xff
CMD_PING = 0x01
CMD_REGISTER = 0x11
CMD_UPDATE = 0x51
CMD_CONTROL = 0x81


############################################
# Serial monitoring thread
############################################

class SerialThread(threading.Thread):
    quit = False

    def __init__(self, recv_queue, send_queue, callback):
        threading.Thread.__init__(self)
        self.recv_queue = recv_queue
        self.send_queue = send_queue
        self.cmd_callback = callback
        self.bytes = list()

    def connect(self):
        # Connect serial
        print 'Serial thread: started !!!'
        print 'Connect to serial...'
        try:
            self.ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
            #ser = serial.Serial(0)
            self.ser.open()
            print '\tPort ttyAMA0 is opened'
        except serial.SerialException as ex:
            print '\tPort ttyAMA0 is unavailable:'

        print 'OK'

    # Parse input stream and make information list
    # device information list will be put into queue (recv_queue)
    def parse(self, stream):
        self.stream = stream
        in_bytes = bytearray(stream)
        index = 0
        # append packet to buffer
        for idx in range(len(in_bytes)):
            self.bytes.append(in_bytes[idx])
            if len(self.bytes) < PACKET_LEN:
                continue
            # check packet validity at this index
            if (index+PACKET_LEN <= len(self.bytes)
                    and self.bytes[index] == IN_START1 
                    and self.bytes[index+1] == IN_START2 
                    and self.bytes[index+PACKET_LEN-1] == IN_END):
                # start parsing
                # index+2 : category1, index+3 : category2, index+4 : ID, index+5 : command
                # index+6~index+7 : Data1, index+8~index+9 : Data2, ..., index+12~index+13 : Data4
                # index+14 : End byte
                device_info = DeviceInfo()
                device_info.itemtype = 1    # 0: queue item type
                device_info.cat1 = int(self.bytes[index+2])  # 1: cat1
                device_info.cat2 = int(self.bytes[index+3])  # 2: cat2
                device_info.devid = int(self.bytes[index+4])   # 3: device ID
                device_info.cmd = int(self.bytes[index+5]) # 4: command

                # ping response
                if device_info.cmd == CMD_PING:
                    #print '    Command : Ping response'
                    logging.warning('Command received : Ping response')
                    device_info.name = 'User device'  # name
                    device_info.loc = 'NA'    # location
                    device_info.time = int(time.time())  # timestamp
                    # pass to callback function
                    self.cmd_callback(device_info)
                    # empty buffer
                    self.bytes = list()
                # register device
                elif device_info.cmd == CMD_REGISTER:
                    #print '    Command : Register device'
                    logging.warning('Command received : Register device')
                    device_info.cmd1 = int(self.bytes[index+6])  # 5: available cmd 1
                    device_info.cmd1dtype = int(self.bytes[index+7])  # 6: available cmd 1 - data type
                    device_info.cmd2 = int(self.bytes[index+8])  # 7: 
                    device_info.cmd2dtype = int(self.bytes[index+9])  # 8: 
                    device_info.cmd3 = int(self.bytes[index+10]) # 9: 
                    device_info.cmd3dtype = int(self.bytes[index+11])  # 10: 
                    device_info.cmd4 = int(self.bytes[index+12])  # 11: available cmd 4
                    device_info.cmd4dtype = int(self.bytes[index+13])  # 12: available cmd 4 - data type
                    device_info.name = 'User device'  # 13: name
                    device_info.loc = 'NA'  # 14: location
                    device_info.time = int(time.time())  # 15: timestamp
                    # put in queue
                    self.recv_queue.put(device_info)
                    # empty buffer
                    self.bytes = list()
                # update sensor value
                elif device_info.cmd == CMD_UPDATE:
                    data1, data2, data3, data4 = 0x0000,0x0000,0x0000,0x0000
                    # you have to check negative value
                    if self.bytes[index+6] & 0x80 == 0x80:
                        data1 = int(self.bytes[index+6] ^ 0xff) << 8 | int(self.bytes[index+7] ^ 0xff)
                        data1 *= -1
                    else:
                        data1 = (int(self.bytes[index+6]) << 8) | int(self.bytes[index+7])
                    if self.bytes[index+8] & 0x80 == 0x80:
                        data2 = int(self.bytes[index+8] ^ 0xff) << 8 | int(self.bytes[index+9] ^ 0xff)
                        data2 *= -1
                    else:
                        data2 = (int(self.bytes[index+8]) << 8) | int(self.bytes[index+9])
                    if self.bytes[index+10] & 0x80 == 0x80:
                        data3 = int(self.bytes[index+10] ^ 0xff) << 8 | int(self.bytes[index+11] ^ 0xff)
                        data3 *= -1
                    else:
                        data3 = (int(self.bytes[index+10]) << 8) | int(self.bytes[index+11])
                    if self.bytes[index+12] & 0x80 == 0x80:
                        data4 = int(self.bytes[index+12] ^ 0xff) << 8 | int(self.bytes[index+13] ^ 0xff)
                        data4 *= -1
                    else:
                        data4 = (int(self.bytes[index+12]) << 8) | int(self.bytes[index+13])
                    #print '    Command : Update sensor value (%d, %d, %d, %d)' % (data1, data2, data3, data4)
                    logging.warning('Command received : Update sensor value (%d, %d, %d, %d)' % (data1, data2, data3, data4))
                    device_info.data1 = data1  # 5: int data 1
                    device_info.data2 = data2  # 6: int data 2
                    device_info.data3 = data3  # 7: int data 3
                    device_info.data4 = data4  # 8: int data 4
                    device_info.name = 'User device'  # 13: name
                    device_info.loc = 'NA'  # 14: location
                    device_info.time = int(time.time())  # 15: timestamp
                    # put in queue
                    self.recv_queue.put(device_info)
                    # empty buffer
                    self.bytes = list()
                # control signal response
                elif device_info.cmd == CMD_CONTROL:
                    data1, data2, data3, data4 = 0x0000,0x0000,0x0000,0x0000
                    # you have to check negative value
                    if self.bytes[index+6] & 0x80 == 0x80:
                        data1 = int(self.bytes[index+6] ^ 0xff) << 8 | int(self.bytes[index+7] ^ 0xff)
                        data1 *= -1
                    else:
                        data1 = (int(self.bytes[index+6]) << 8) | int(self.bytes[index+7])
                    if self.bytes[index+8] & 0x80 == 0x80:
                        data2 = int(self.bytes[index+8] ^ 0xff) << 8 | int(self.bytes[index+9] ^ 0xff)
                        data2 *= -1
                    else:
                        data2 = (int(self.bytes[index+8]) << 8) | int(self.bytes[index+9])
                    if self.bytes[index+10] & 0x80 == 0x80:
                        data3 = int(self.bytes[index+10] ^ 0xff) << 8 | int(self.bytes[index+11] ^ 0xff)
                        data3 *= -1
                    else:
                        data3 = (int(self.bytes[index+10]) << 8) | int(self.bytes[index+11])
                    if self.bytes[index+12] & 0x80 == 0x80:
                        data4 = int(self.bytes[index+12] ^ 0xff) << 8 | int(self.bytes[index+13] ^ 0xff)
                        data4 *= -1
                    else:
                        data4 = (int(self.bytes[index+12]) << 8) | int(self.bytes[index+13])
                    print '    Command : result of control request (%d, %d, %d, %d)' % (data1, data2, data3, data4)
                    logging.warning('Command received : control result (%d, %d, %d, %d)' % (data1, data2, data3, data4))
                    device_info.data1 = data1  # int data 1
                    device_info.data2 = data2  # int data 2
                    device_info.data3 = data3  # int data 3
                    device_info.data4 = data4  # int data 4
                    device_info.name = 'User device'  # name
                    device_info.loc = 'NA'  # location
                    device_info.time = int(time.time())  #timestamp
                    # pass to callback function
                    self.cmd_callback(device_info)
                    # empty buffer
                    self.bytes = list()
                else:
                    #print '    Undefined command !!'
                    logging.warning('Undefined command found!!')
            # resize buffer
            if len(self.bytes) > 0:
                del self.bytes[0]
        # End of parse function
        return

    def run(self):
        while True:
            # Check serial input
            try:
                res = self.ser.readline()
                #print ':'.join("{:02x}".format(ord(c)) for c in res)
            except:
                #print 'Oooops!!! Serial port is not available!!!'
                logging.warning('Oooops!!! Serial port is not available!!!')
                break;
            # Parse
            self.parse(res)
            
            # Set asynchronous job in worker queue
            # recv_queue.put()
            if self.quit == True:
                break
            time.sleep(0.1)
        return

    def send(self, cat1, cat2, devid, command, data1, data2, data3, data4):
        barray = bytearray([OUT_START1, OUT_START2, cat1, cat2, devid, command])
        if data1 < 0:
            positive = ~(data1*-1) | 0x8000
            barray.append((positive >> 8) & 0xff)
            barray.append(positive & 0xff)
        else:
            barray.append((data1 >> 8) & 0xff)
            barray.append(data1 & 0xff)
        if data2 < 0:
            positive = ~(data2*-1) | 0x8000
            barray.append((positive >> 8) & 0xff)
            barray.append(positive & 0xff)
        else:
            barray.append((data2 >> 8) & 0xff)
            barray.append(data2 & 0xff)
        if data3 < 0:
            positive = ~(data3*-1) | 0x8000
            barray.append((positive >> 8) & 0xff)
            barray.append(positive & 0xff)
        else:
            barray.append((data3 >> 8) & 0xff)
            barray.append(data3 & 0xff)
        if data4 < 0:
            positive = ~(data4*-1) | 0x8000
            barray.append((positive >> 8) & 0xff)
            barray.append(positive & 0xff)
        else:
            barray.append((data4 >> 8) & 0xff)
            barray.append(data4 & 0xff)
        barray.append(OUT_END)
        #print array.array('B', barray).tostring()
        #print ':'.join(format(x, '02x') for x in barray)
        self.ser.write(barray)
        return

    def send_control_signal(self, cat1, cat2, devid, data1, data2, data3, data4):
        barray = bytearray([OUT_START1, OUT_START2, cat1, cat2, devid, 0x81])
        if data1 < 0:
            positive = ~(data1*-1) | 0x8000
            barray.append((positive >> 8) & 0xff)
            barray.append(positive & 0xff)
        else:
            barray.append((data1 >> 8) & 0xff)
            barray.append(data1 & 0xff)
        if data2 < 0:
            positive = ~(data2*-1) | 0x8000
            barray.append((positive >> 8) & 0xff)
            barray.append(positive & 0xff)
        else:
            barray.append((data2 >> 8) & 0xff)
            barray.append(data2 & 0xff)
        if data3 < 0:
            positive = ~(data3*-1) | 0x8000
            barray.append((positive >> 8) & 0xff)
            barray.append(positive & 0xff)
        else:
            barray.append((data3 >> 8) & 0xff)
            barray.append(data3 & 0xff)
        if data4 < 0:
            positive = ~(data4*-1) | 0x8000
            barray.append((positive >> 8) & 0xff)
            barray.append(positive & 0xff)
        else:
            barray.append((data4 >> 8) & 0xff)
            barray.append(data4 & 0xff)
        barray.append(OUT_END)
        #print array.array('B', barray).tostring()
        #print ':'.join(format(x, '02x') for x in barray)
        self.ser.write(barray)
        return

    def array2bin(arr):
        """ Array of integer byte values --> binary string
        """
        return ''.join(chr(b) for b in arr)


    def close(self):
        self.quit = True
        self.ser.close()

    # End of class SerialThread
    pass

