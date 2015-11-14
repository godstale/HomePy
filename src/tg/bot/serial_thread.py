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
        bytes = bytearray(stream)
        index = 0
        for i in range(len(bytes)):
            # check packet validity at this index
            if (bytes[i] == IN_START1 and bytes[i+1] == IN_START2 
                    and i+PACKET_LEN <= len(bytes) 
                    and bytes[i+PACKET_LEN-1] == IN_END):
                index = i
                # start parsing
                # index+2 : category1, index+3 : category2, index+4 : ID, index+5 : command
                # index+6~index+7 : Data1, index+8~index+9 : Data2, ..., index+12~index+13 : Data4
                # index+14 : End byte
                device_info = []
                device_info.append(1)    # 0: queue item type
                device_info.append(int(bytes[index+2]))  # 1: cat1
                device_info.append(int(bytes[index+3]))  # 2: cat2
                device_info.append(int(bytes[index+4]))  # 3: device ID
                command = int(bytes[index+5])
                device_info.append(command)  # 4: command

                # ping response
                if command == CMD_PING:
                    data1 = 0
                    data2 = 0
                    data3 = 0
                    data4 = 0
                    print '    Command : Ping response'
                    device_info.append(data1)  # int data 1
                    device_info.append(data2)  # int data 2
                    device_info.append(data3)  # int data 3
                    device_info.append(data4)  # int data 4
                    device_info.append(0)  # float data 1
                    device_info.append(0)  # float data 2
                    device_info.append(0)  # dummy
                    device_info.append(0)  # dummy
                    device_info.append('User device')  # name
                    device_info.append('NA')  # location
                    device_info.append(int(time.time()))  #timestamp
                    # pass to callback function
                    self.cmd_callback(device_info)

                # register device
                elif command == CMD_REGISTER:
                    print '    Command : Register device'
                    device_info.append(int(bytes[index+6]))  # 5: available cmd 1
                    device_info.append(int(bytes[index+7]))  # 6: available cmd 1 - data type
                    device_info.append(int(bytes[index+8]))  # 7: 
                    device_info.append(int(bytes[index+9]))  # 8: 
                    device_info.append(int(bytes[index+10])) # 9: 
                    device_info.append(int(bytes[index+11]))  # 10: 
                    device_info.append(int(bytes[index+12]))  # 11: available cmd 4
                    device_info.append(int(bytes[index+13]))  # 12: available cmd 4 - data type
                    device_info.append('User device')  # 13: name
                    device_info.append('NA')  # 14: location
                    device_info.append(int(time.time()))  # 15: timestamp
                    # put in queue
                    self.recv_queue.put(device_info)

                # update sensor value
                elif command == CMD_UPDATE:
                    data1 = (int(bytes[index+6]) << 8) | int(bytes[index+7])
                    data2 = (int(bytes[index+8]) << 8) | int(bytes[index+9])
                    data3 = (int(bytes[index+10]) << 8) | int(bytes[index+11])
                    data4 = (int(bytes[index+12]) << 8) | int(bytes[index+13])
                    print '    Command : Update sensor value (%d, %d, %d, %d)' % (data1, data2, data3, data4)
                    device_info.append(data1)  # 5: int data 1
                    device_info.append(data2)  # 6: int data 2
                    device_info.append(data3)  # 7: int data 3
                    device_info.append(data4)  # 8: int data 4
                    device_info.append(0)  # 9: float data 1
                    device_info.append(0)  # 10: float data 2
                    device_info.append(0)  # 11: dummy
                    device_info.append(0)  # 12: dummy
                    device_info.append('User device')  # 13: name
                    device_info.append('NA')  # 14: location
                    device_info.append(int(time.time()))  # 15: timestamp
                    # put in queue
                    self.recv_queue.put(device_info)

                # control signal response
                elif command == CMD_CONTROL:
                    data1 = (int(bytes[index+6]) << 8) | int(bytes[index+7])
                    data2 = (int(bytes[index+8]) << 8) | int(bytes[index+9])
                    data3 = (int(bytes[index+10]) << 8) | int(bytes[index+11])
                    data4 = (int(bytes[index+12]) << 8) | int(bytes[index+13])
                    print '    Command : result of control request (%d, %d, %d, %d)' % (data1, data2, data3, data4)
                    device_info.append(data1)  # int data 1
                    device_info.append(data2)  # int data 2
                    device_info.append(data3)  # int data 3
                    device_info.append(data4)  # int data 4
                    device_info.append(0)  # float data 1
                    device_info.append(0)  # float data 2
                    device_info.append(0)  # dummy
                    device_info.append(0)  # dummy
                    device_info.append('User device')  # name
                    device_info.append('NA')  # location
                    device_info.append(int(time.time()))  #timestamp
                    # pass to callback function
                    self.cmd_callback(device_info)

                else:
                    print '    Undefined command !!'
        # End of parse function
        return

    def run(self):
        while True:
            # Check serial input
            try:
                res = self.ser.readline()
                #print ':'.join("{:02x}".format(ord(c)) for c in res)
            except:
                print 'Oooops!!! Serial port is not available!!!'
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
        barray.append(data1 >> 8)
        barray.append(data1)
        barray.append(data2 >> 8)
        barray.append(data2)
        barray.append(data3 >> 8)
        barray.append(data3)
        barray.append(data4 >> 8)
        barray.append(data4)
        barray.append(OUT_END)
        #print array.array('B', barray).tostring()
        print ':'.join(format(x, '02x') for x in barray)
        self.ser.write(barray)
        return

    def send_control_signal(self, cat1, cat2, devid, data1, data2, data3, data4):
        barray = bytearray([OUT_START1, OUT_START2, cat1, cat2, devid, 0x81])
        barray.append(data1 >> 8)
        barray.append(data1)
        barray.append(data2 >> 8)
        barray.append(data2)
        barray.append(data3 >> 8)
        barray.append(data3)
        barray.append(data4 >> 8)
        barray.append(data4)
        barray.append(OUT_END)
        #print array.array('B', barray).tostring()
        print ':'.join(format(x, '02x') for x in barray)
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

