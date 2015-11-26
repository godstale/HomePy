#-*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import Queue
import threading
import time

import serial
import urllib2
#import pyowm
import MySQLdb
import CairoPlot
import cairo
import math
import subprocess
from decimal import *

from db_helper import DBHelper
from serial_thread import SerialThread
from device_manager_thread import DeviceManagerThread
from hc_protocol import *
from message_box import *
from utilities import *
from config import Configurations

# Telegram python interface
import telebot



###########################################
# Important!!!
# Configurations: adjust as necessary
###########################################

# Write your own TOKEN (get from BotFather)
API_TOKEN = "your_token"
CHAT_ID = ""    # leave it blank if you dont know

# Type your MySQL settings
MYSQL_USER = 'your_user_name'
MYSQL_DB = 'your_db_name'
MYSQL_PASS = 'your_user_pass'

# Weather report (Deprecated!!! do not use this)
# Get API key from
# http://openweathermap.org/register 
# weather_api_key = 'your_api_key'
# weather_location = 'Seoul,kr'

# Camera
cctv_url = ''    # leave it blank if you dont know your IP (not internal IP)
cctv_port = '8891'  # external port of cctv streaming (you have to set port forwarding)
cctv_start_cmd = '/home/pi/tg/bot/start_motion'
cctv_stop_cmd = '/home/pi/tg/bot/stop_motion'
picture_dir = '/home/pi/tg/bot/picture/'
graph_dir = '/home/pi/tg/bot/graph/'
take_a_picture_cmd = 'sudo /usr/bin/raspistill -w 640 -h 480 -o '  # adjust as necessary



############################################
# Global variables
############################################

# Telegram bot interface
bot = telebot.TeleBot(API_TOKEN)
# Camera
is_cctv_active = False
# Queue
recv_queue = Queue.Queue()
send_queue = Queue.Queue()





############################################
# Telegram message handler
############################################

# Not implemented yet!!
#@bot.message_handler(commands=['record', 'rec'])
#def cctv_off(message):
#    send_chat(message, 'Sorry, not implemented yet...')


# Nomal text handler
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    global is_cctv_active
    global CHAT_ID
    global cctv_url

    # update chat id
    if CHAT_ID == '':
        CHAT_ID = message.chat.id

    parseCommand(message, message.text)
    pass

# Parse command
def parseCommand(message, str_cmd):
    global is_cctv_active
    global CHAT_ID
    global cctv_url

    # split message
    cmd = str_cmd.strip().split(' ')
    
    # Bot check command
    if cmd[0] == 'hello' or cmd[0] == 'hi' or cmd[0] == '하이' or cmd[0] == '안녕':
        send_chat(message, msg_welcome())
    # Ping test
    elif cmd[0] == 'help' or cmd[0] == '도움말':
        send_chat(message, msg_help_text())

    # Ping test
    elif cmd[0] == 'ping' or cmd[0] == '핑':
        # extract parameter
        # send a data1 data2 data3 data4 : a=device number, data1 ~ data4: data to send to remote
        if len(cmd) < 2:
            send_chat(message, msg_devnum_error())
            return
        devnum = -1
        if cmd[1].isdigit():
            devnum = int(cmd[1])
        else:
            send_chat(message, msg_devnum_error())
            return
        device = t_dev.get_device_at(devnum)
        if len(device) < 1:
            send_chat(message, msg_device_not_found() + ' ' + str(devnum))
            return
        t_ser.send(device[1], device[2], device[3], 0x01, 0, 0, 0, 0)        

    # Set language
    elif cmd[0] == 'lang' or cmd[0] == 'language' or cmd[0] == '언어':
        if len(cmd) < 2:
            send_chat(message, msg_current_lang() +': '+config.get_language())
            return
        if cmd[1] == 'en' or cmd[1] == 'english' or cmd[1] == '영어':
            config.set_language('en')
            set_proto_lang('en')
            set_msg_lang('en')
            send_chat(message, msg_lang_changed())
            return
        elif cmd[1] == 'kr' or cmd[1] == 'korean' or cmd[1] == '한글' or cmd[1] == '한국어':
            config.set_language('kr')
            set_proto_lang('kr')
            set_msg_lang('kr')
            send_chat(message, msg_lang_changed())
            return
        send_chat(message, msg_invalid_param())

    # Deprecated!!! Do not use this
    # weather command
#    elif cmd[0] == 'weather' or cmd[0] == '날씨':
#        owm = pyowm.OWM(weather_api_key)
#        obs = owm.weather_at_place(weather_location)
#        w = obs.get_weather()
#        report_str = weather_location
#        report_str += "\n"
#        report_str += w.get_detailed_status()
#        report_str += ", "
#        report_str += str(w.get_temperature(unit='celsius')['temp'])
#        report_str += "'C, "
#        report_str += str(w.get_humidity())
#        report_str += "%"
#        send_chat(message, report_str)

    # cctv command
    elif cmd[0] == 'cctv' or cmd[0] == 'cam' or cmd[0] == '캠':
        if len(cmd) < 2:
            send_chat(message, msg_invalid_param())
            return
        if cmd[1] == 'on' or cmd[1] == '온':
            if is_cctv_active:
                send_chat(message, msg_cctv_already_on() + ' ' + cctv_url)
                return
            else:
                #if cctv_url == '':
                #    cctv_url = 'http://'
                #    cctv_url += subprocess.check_output('wget -q http://ip.kiduk.kr && more index.html', shell=True)
                #    cctv_url += ':' + cctv_port
                os.system(cctv_start_cmd)
                send_chat(message, msg_cctv_on() + ' ' + cctv_url)
                is_cctv_active = True
        elif cmd[1] == 'off' or cmd[1] == '오프':
            os.system(cctv_stop_cmd)
            send_chat(message, msg_cctv_off())
            is_cctv_active = False

    # take a picture
    elif cmd[0] == 'pic' or cmd[0] == 'picture' or cmd[0] == '사진':
        # Stop cctv first
        if is_cctv_active:
            send_chat(message, msg_turnoff_cctv())
        os.system(cctv_stop_cmd)
        is_cctv_active = False
        time.sleep(1)  # Sleep for a while to avoid camera access error

        # Take a still shot
        now = time.localtime()
        pic_file_name = "image_%04d-%02d-%02d_%02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
        pic_file_name += '.jpg'
        os.system(take_a_picture_cmd + picture_dir + pic_file_name)

        # Send picture
        try:
            pic_file = open(picture_dir + pic_file_name, 'rb')
            ret_msg = send_photo(message, pic_file)  # message.chat.id
        except:
            send_chat(message, 'Cannot take a picture!!')

    # Device command
    elif cmd[0] == 'dev' or cmd[0] == 'device' or cmd[0] == '장치':
        # Device - Show device list
        if len(cmd) < 2:
            count = 0
            msg = ''
            devices = t_dev.get_device_list()
            for device in devices:
                msg += str(count+1) + ". "
                msg += device[13]
                msg += ", " + msg_location() + "="
                msg += device[14]
                msg += "\n" + msg_category() +"1=" + str(device[1])
                msg += ", " + msg_category() +"2=" + str(device[2])
                msg += ", ID=" + str(device[3])
                msg += "\n\n"
                count = count + 1
            if count < 1:
                msg += msg_device_not_found()
            else:
                msg += msg_devdesc_command()
            send_chat(message, msg)
        # Device - Show device details
        elif cmd[1] == 'desc' or cmd[1] == 'detail' or cmd[1] == '상세':
            if len(cmd) >= 3:
                msg = ''
                devnum = -1
                if cmd[2].isdigit():
                    devnum = int(cmd[2])
                device = t_dev.get_device_at(devnum)
                if len(device) > 0:
                    msg += msg_device_number() + " = " + str(devnum) + "\n"
                    msg += device[13]
                    msg += ", " + msg_location() + "="
                    msg += device[14]
                    msg += "\n" + msg_category() + "1=" + str(device[1])
                    msg += ", " + msg_category() + "2=" + str(device[2])
                    msg += ", ID=" + str(device[3])
                    msg += "\n" + msg_update_time() + "=" + time.asctime(time.localtime(device[15]))
                    msg += "\n\n"
                    msg += msg_control_signal() + "1="
                    msg += get_cmd_name(device[5])
                    msg += ", " + msg_data_type() + "1="
                    msg += get_cmd_type_name(device[6])
                    msg += "\n"
                    msg += msg_control_signal() + "2="
                    msg += get_cmd_name(device[7])
                    msg += ", " + msg_data_type() + "2="
                    msg += get_cmd_type_name(device[8])
                    msg += "\n"
                    msg += msg_control_signal() + "3="
                    msg += get_cmd_name(device[9])
                    msg += ", " + msg_data_type() + "3="
                    msg += get_cmd_type_name(device[10])
                    msg += "\n"
                    msg += msg_control_signal() + "4="
                    msg += get_cmd_name(device[11])
                    msg += ", " + msg_data_type() + "4="
                    msg += get_cmd_type_name(device[12])
                    msg += "\n\n" + msg_ctrlsignal_desc()
                else:
                    msg += msg_device_not_found()
                send_chat(message, msg)

        # Device - Remove device
        elif cmd[1] == 'remove' or cmd[1] == 'del' or cmd[1] == 'delete' or cmd[1] == '삭제' or cmd[1] == '제거':
            if len(cmd) >= 3:
                msg = ''
                devnum = 0
                if cmd[2].isdigit():
                    devnum = int(cmd[2])
                else:
                    send_chat(message, msg_devnum_error())
                    return
                if t_dev.delete_device_at(devnum):
                    send_chat(message, msg_device_removed() % devnum)
                else:
                    send_chat(message, msg_device_remove_error() % devnum)

        # Device - Remove all devices
        elif cmd[1] == 'removeall' or cmd[1] == 'delall' or cmd[1] == 'deleteall' or cmd[1] == '모두삭제' or cmd[1] == '모두제거':
            if t_dev.delete_devices_all():
                send_chat(message, msg_every_device_removed())
            else:
                send_chat(message, msg_every_device_remove_error())

    # Get sensor value
    elif cmd[0] == 'sensor' or cmd[0] == 'data' or cmd[0] == 'print' or cmd[0] == '센서' or cmd[0] == '데이터' or cmd[0] == '출력':
        if len(cmd) < 2:
            return
        # Delete sensor records
        if cmd[1] == 'remove' or cmd[1] == 'del' or cmd[1] == 'delete' or cmd[1] == '삭제' or cmd[1] == '제거':
            # Delete specified device's records
            if len(cmd) == 3:
                devnum = 0
                if cmd[2].isdigit():
                    devnum = int(cmd[2])
                else:
                    send_chat(message, msg_devnum_error())
                    return
                # delete from DB
                if t_dev.delete_sensor_val(devnum, -1):
                    send_chat(message, msg_sensordata_removed() % devnum)
                else:
                    send_chat(message, msg_sensordata_remove_error() % devnum)

            # Delete records older than user specified time (specified device)
            # time must be hour unit: delete all older than x hours
            elif len(cmd) >= 4:
                # Get device number, time string
                devnum = -1
                if cmd[2].isdigit():
                    devnum = int(cmd[2])
                newtime = -1
                if cmd[3].isdigit():
                    tparam = int(cmd[3])
                    newtime = int(time.time() - tparam*60*60)
                # delete from DB
                if t_dev.delete_sensor_val(devnum, newtime):
                    send_chat(message, msg_sensordata_removed() % devnum)
                else:
                    send_chat(message, msg_sensordata_remove_error() % devnum)
            else:
                send_chat(message, msg_need_devnum())

        # Delete sensor records all
        elif cmd[1] == 'removeall' or cmd[1] == 'delall' or cmd[1] == 'deleteall' or cmd[1] == '모두삭제' or cmd[1] == '모두제거':
            # Delete specified device's records
            newtime = -1
            if len(cmd) >= 3:
                # Delete records older than user specified time (specified device)
                # time must be hour unit: delete all older than x hours
                newtime = -1
                if cmd[2].isdigit():
                    tparam = int(cmd[2])
                    newtime = int(time.time() - tparam*60*60*1000)
            # delete from DB
            if t_dev.delete_sensor_all(newtime):
                send_chat(message, msg_every_sensordata_removed())
            else:
                send_chat(message, msg_every_sensordata_remove_error())

        # Show sensor records
        else:
            # extract parameter
            # sensor a b : a=device number, b=count
            count = 1
            if len(cmd) > 2:
                if cmd[2].isdigit():
                    count = int(cmd[2])
                if count > 100 or count < 1:
                    count = 100
            devnum = -1
            if cmd[1].isdigit():
                devnum = int(cmd[1])
            is_avail, infos = t_dev.get_sensor_val(devnum, count)
            msg = ''
            i = 0
            for info in infos:
                itime = time.localtime(info[6])
                msg += "%d-%d %d:%d" % (itime.tm_mon, itime.tm_mday, itime.tm_hour, itime.tm_min)
                msg += " = %d, %d, %d, %d" % (info[0], info[1], info[2], info[3])
                msg += "\n"
                i = i + 1
            if i > 0:
                send_chat(message, msg)
            else:
                send_chat(message, msg_no_matching_result())

    # Get sensor value and return with graph
    elif cmd[0] == 'graph' or cmd[0] == '그래프':
        # extract parameter
        # graph a b : a=device number, b=count
        if len(cmd) < 2:
            return
        count = 10
        if len(cmd) > 2:
            if cmd[2].isdigit():
                count = int(cmd[2])
            if count > 100 or count < 1:
                count = 100
        devnum = -1
        if cmd[1].isdigit():
            devnum = int(cmd[1])
        is_avail, infos = t_dev.get_sensor_val(devnum, count)
        # making data list
        i = 0
        datas = [[], [], [], []]
        h_labels = []
        prev_d, prev_h, prev_m = 0, 0, 0
        for info in infos:
            itime = time.localtime(info[6])
            if prev_d != itime.tm_mday or prev_h != itime.tm_hour or prev_m != itime.tm_min:
                timestr = "%d-%d %d:%d" % (itime.tm_mon, itime.tm_mday, itime.tm_hour, itime.tm_min)
            else:
                timestr = "%d:%d" % (itime.tm_hour, itime.tm_min)
            prev_d, prev_h, prev_m = itime.tm_mday, itime.tm_hour, itime.tm_min
            datas[0].append(info[0])
            datas[1].append(info[1])
            datas[2].append(info[2])
            datas[3].append(info[3])
            h_labels.append(timestr)
            i = i + 1
        # ready to burn graph
        if i > 0:
            # adjust image size
            width = 500
            height = 375
            if i > 25 and i <= 50:
                width = 1000
                height = 750
            elif i > 50:
                width = 1600
                height = 1200
            # burn graph
            cat1, cat2, devid = t_dev.get_ids_at(devnum)
            fname = 'graph_'+str(cat1)+'_'+str(cat2)+'_'+str(devid)+'.png'
            CairoPlot.dot_line_plot(graph_dir + fname,
                    datas, width, height,
                    h_labels = h_labels, v_labels = [],
                    axis = True, grid = True, dots = True)
            try:
                # Send graph
                pic_file = open(graph_dir + fname, 'rb')
                ret_msg = send_photo(message, pic_file)
            except:
                send_chat(message, msg_cannot_open_graph())
        else:
            send_chat(message, msg_no_matching_result())

    # Sends data to remote
    elif cmd[0] == 'ctrl' or cmd[0] == 'control' or cmd[0] == 'send' or cmd[0] == '제어' or cmd[0] == '전송':
        # extract parameter
        # send a data1 data2 data3 data4 : a=device number, data1 ~ data4: data to send to remote
        if len(cmd) < 3:
            return
        devnum = -1
        if cmd[1].isdigit():
            devnum = int(cmd[1])
        else:
            send_chat(message, msg_wrong_device())
            return;
        # get device info
        device = t_dev.get_device_at(devnum)
        if len(device) < 1:
            send_chat(message, msg_wrong_device())
            return;
        data1 = 0
        # we have to catch the exception: negative value
        if cmd[2][0] == '-' and cmd[2][1:].isdigit():
            data1 = int(Decimal(cmd[2]))
        elif cmd[2].isdigit():
            data1 = int(cmd[2])
        else:
            send_chat(message, msg_wrong_param1())
            return;
        data2 = 0
        if len(cmd) > 3 and cmd[3][0] == '-' and cmd[3][1:].isdigit():
            data2 = int(Decimal(cmd[3]))
        elif len(cmd) > 3 and cmd[3].isdigit():
            data2 = int(cmd[3])
        else:
            data2 = 0
        data3 = 0
        if len(cmd) > 4 and cmd[4][0] == '-' and cmd[4][1:].isdigit():
            data3 = int(Decimal(cmd[4]))
        elif len(cmd) > 4 and cmd[4].isdigit():
            data3 = int(cmd[4])
        else:
            data3 = 0
        data4 = 0
        if len(cmd) > 5 and cmd[5][0] == '-' and cmd[5][1:].isdigit():
            data4 = int(Decimal(cmd[5]))
        elif len(cmd) > 5 and cmd[5].isdigit():
            data4 = int(cmd[5])
        else:
            data4 = 0
        # send device control signal to remote
        t_ser.send_control_signal(device[1], device[2], device[3], data1, data2, data3, data4)
        send_chat(message, msg_sent_signal() % devnum)

    # Make notification setting
    elif cmd[0] == 'noti' or cmd[0] == 'notification' or cmd[0] == '알림':
        # Show current notifications
        if len(cmd) < 2:
            strmsg = ''
            notis = t_dev.get_noti_list()
            count = 0
            for noti in notis:
                strmsg += msg_noti() + ' ID = ' + str(noti[0]) + '\n'
                #strmsg += noti[13] + '\n'
                strmsg += msg_category() + "1=" + str(noti[1])
                strmsg += ", " + msg_category() + "2=" + str(noti[2])
                strmsg += ", ID=" + str(noti[3]) + "\n" + "if "
                tmpcount = 0
                if noti[4] > 0:
                    strmsg += "Data1 "
                    strmsg += get_comp_operator(noti[4]) + " "
                    strmsg += str(noti[8]) + "\n"
                    tmpcount += 1
                if noti[5] > 0:
                    if tmpcount > 0:
                        strmsg += "and "
                    strmsg += "Data2 "
                    strmsg += get_comp_operator(noti[5]) + " "
                    strmsg += str(noti[9]) + "\n"
                    tmpcount += 1
                if noti[6] > 0:
                    if tmpcount > 0:
                        strmsg += "and "
                    strmsg += "Data3 "
                    strmsg += get_comp_operator(noti[6]) + " "
                    strmsg += str(noti[10]) + "\n"
                    tmpcount += 1
                if noti[7] > 0:
                    if tmpcount > 0:
                        strmsg += "and "
                    strmsg += "Data4 "
                    strmsg += get_comp_operator(noti[7]) + " "
                    strmsg += str(noti[11]) + "\n"
                    tmpcount += 1
                count += 1
                strmsg += '\n'
            if count > 0:
                send_chat(message, strmsg)
            else:
                send_chat(message, msg_no_noti())
            # End of 'noti' command
            return

        # Delete notification
        elif cmd[1] == 'delete' or cmd[1] == 'del' or cmd[1] == '삭제' or cmd[1] == '제거':
            if len(cmd) < 3:
                send_chat(message, msg_type_noti_del_param())
                return
            else:
                if len(cmd) == 3 and cmd[2].isdigit():
                    # delete with noti-ID
                    noti_id = int(cmd[2])
                    if t_dev.delete_noti_with_id(noti_id):
                        send_chat(message, msg_noti_del_success())
                    else:
                        send_chat(message, msg_noti_del_fail())
                    return
                elif len(cmd) == 5 and cmd[2].isdigit() and cmd[3].isdigit() and cmd[4].isdigit():
                    # delete with device parameters
                    cat1 = int(cmd[2])
                    cat2 = int(cmd[3])
                    devid = int(cmd[4])
                    if t_dev.delete_noti_with_param(cat1, cat2, devid):
                        send_chat(message, msg_noti_del_success())
                    else:
                        send_chat(message, msg_noti_del_fail())
                    return
                else:
                    # delete with name
                    noti_name = ''
                    for index in range(2, len(cmd)):
                        noti_name += cmd[index]
                    if t_dev.delete_noti_with_name(noti_name):
                        send_chat(message, msg_noti_del_success())
                    else:
                        send_chat(message, msg_noti_del_fail())
                    return

        # Add notification
        elif cmd[1] == 'add' or cmd[1] == '추가':
            if len(cmd) < 4:
                send_chat(message, msg_add_noti_param())
                return
            devnum = -1
            if cmd[2].isdigit():
                devnum = int(cmd[2])
            else:
                send_chat(message, msg_add_noti_param())
                return
            # search device info
            cat1, cat2, devid = t_dev.get_ids_at(devnum)
            if cat1 < 0 or cat2 < 0 or devid < 0:
                send_chat(message, msg_wrong_device())
                return
            noti = []
            noti.append(-1)
            noti.append(cat1)
            noti.append(cat2)
            noti.append(devid)

            datanum1, datanum2, datanum3, datanum4 = 0,0,0,0
            compcode1, compcode2, compcode3, compcode4 = 0,0,0,0
            targetnum1, targetnum2, targetnum3, targetnum4 = 0,0,0,0
            pcount = 0
            # parse data1
            datanum, compcode, targetnum = parse_comp_str(cmd[3])
            if datanum < 1 or compcode < 1:
                # send_chat(message, msg_add_noti_param()+' (data1 error)')
                pass
            elif datanum == 1:
                compcode1 = compcode
                targetnum1 = targetnum
                pcount += 1
            elif datanum == 2:
                compcode2 = compcode
                targetnum2 = targetnum
                pcount += 1
            elif datanum == 3:
                compcode3 = compcode
                targetnum3 = targetnum
                pcount += 1
            elif datanum == 4:
                compcode4 = compcode
                targetnum4 = targetnum
                pcount += 1
            # parse data2
            if len(cmd) > 4:
                datanum, compcode, targetnum = parse_comp_str(cmd[4])
                if datanum < 1 or compcode < 1:
                    # send_chat(message, msg_add_noti_param()+' (data2 error)')
                    pass
                elif datanum == 1:
                    compcode1 = compcode
                    targetnum1 = targetnum
                    pcount += 1
                elif datanum == 2:
                    compcode2 = compcode
                    targetnum2 = targetnum
                    pcount += 1
                elif datanum == 3:
                    compcode3 = compcode
                    targetnum3 = targetnum
                    pcount += 1
                elif datanum == 4:
                    compcode4 = compcode
                    targetnum4 = targetnum
                    pcount += 1
            # parse data3
            if len(cmd) > 5:
                datanum, compcode, targetnum = parse_comp_str(cmd[5])
                if datanum < 1 or compcode < 1:
                    # send_chat(message, msg_add_noti_param()+' (data4 error)')
                    pass
                elif datanum == 1:
                    compcode1 = compcode
                    targetnum1 = targetnum
                    pcount += 1
                elif datanum == 2:
                    compcode2 = compcode
                    targetnum2 = targetnum
                    pcount += 1
                elif datanum == 3:
                    compcode3 = compcode
                    targetnum3 = targetnum
                    pcount += 1
                elif datanum == 4:
                    compcode4 = compcode
                    targetnum4 = targetnum
                    pcount += 1
            # parse data4
            if len(cmd) > 6:
                datanum, compcode, targetnum = parse_comp_str(cmd[6])
                if datanum < 1 or compcode < 1:
                    # send_chat(message, msg_add_noti_param()+' (data4 error)')
                    pass
                if datanum == 1:
                    compcode1 = compcode
                    targetnum1 = targetnum
                    pcount += 1
                elif datanum == 2:
                    compcode2 = compcode
                    targetnum2 = targetnum
                    pcount += 1
                elif datanum == 3:
                    compcode3 = compcode
                    targetnum3 = targetnum
                    pcount += 1
                elif datanum == 4:
                    compcode4 = compcode
                    targetnum4 = targetnum
                    pcount += 1
            if pcount < 1:
                send_chat(message, msg_invalid_noti_cmd())
                return
            # assign parsed parameters
            noti.append(compcode1)
            noti.append(compcode2)
            noti.append(compcode3)
            noti.append(compcode4)
            noti.append(targetnum1)
            noti.append(targetnum2)
            noti.append(targetnum3)
            noti.append(targetnum4)
            noti.append(int(time.time()))
            cur = time.localtime()
            noti.append('Noti' + str(cur.tm_mon) + str(cur.tm_mday) + str(cur.tm_hour) + str(cur.tm_min) + str(cur.tm_sec))
            # push to DB and cached list
            if t_dev.add_noti(noti):
                send_chat(message, msg_add_noti_success())
            else:
                send_chat(message, msg_add_noti_failed())
        # Invalid notification command
        else:
            send_chat(message, msg_invalid_noti_cmd())

    # Make macro
    elif cmd[0] == 'macro' or cmd[0] == '매크로':
        # Show macro list
        if len(cmd) < 2:
            strmsg = ''
            macros = t_dev.get_macro_list()
            count = 0
            for macro in macros:
                strmsg += msg_macro() + ' ID = ' + str(macro[0]) + '\n'
                strmsg += '-> If ' + msg_noti() + ' ID = ' + str(macro[1]) + ', Do : '
                strmsg += macro[6] + '\n'
                count += 1
            if count > 0:
                send_chat(message, strmsg)
            else:
                strmsg += '\n'
                send_chat(message, msg_no_macro())
            # End of 'macro' command
            return

        # Delete notification
        elif cmd[1] == 'delete' or cmd[1] == 'del' or cmd[1] == '삭제' or cmd[1] == '제거':
            if len(cmd) < 3:
                send_chat(message, msg_type_macro_del_param())
                return
            else:
                if len(cmd) == 3 and cmd[2].isdigit():
                    # delete with macro-ID
                    macro_id = int(cmd[2])
                    if t_dev.delete_macro_with_id(macro_id):
                        send_chat(message, msg_macro_del_success())
                    else:
                        send_chat(message, msg_macro_del_fail())
                    return
                elif len(cmd) == 5 and cmd[2].isdigit() and cmd[3].isdigit() and cmd[4].isdigit():
                    # delete with device parameters
                    cat1 = int(cmd[2])
                    cat2 = int(cmd[3])
                    devid = int(cmd[4])
                    if t_dev.delete_macro_with_param(cat1, cat2, devid):
                        send_chat(message, msg_macro_del_success())
                    else:
                        send_chat(message, msg_macro_del_fail())
                    return
                else:
                    # cannot delete macro
                    send_chat(message, msg_macro_del_fail())
                    return

        # Add notification
        elif cmd[1] == 'add' or cmd[1] == '추가':
            if len(cmd) < 4:
                send_chat(message, msg_add_macro_param())
                return
            noti_num = -1
            if cmd[2].isdigit():
                noti_num = int(cmd[2])
            else:
                send_chat(message, msg_add_macro_param())
                return
            # search device info
            noti = t_dev.get_noti_with_id(noti_num)
            if len(noti) < 1:
                send_chat(message, msg_invalid_noti_id())
                return
            cat1 = noti[1]
            cat2 = noti[2]
            devid = noti[3]
            if cat1 < 0 or cat2 < 0 or devid < 0:
                send_chat(message, msg_wrong_device())
                return
            str_cmd = ""
            for index in range(3, len(cmd)):
                str_cmd += cmd[index] + ' '
            str_cmd.strip()
            a_macro = []
            a_macro.append(-1)      # id
            a_macro.append(noti_num)# noti id
            a_macro.append(cat1)    # cat1
            a_macro.append(cat2)    # cat2
            a_macro.append(devid)  # device ID
            a_macro.append(time.time())  # updated
            a_macro.append(str_cmd) # command
            if t_dev.add_macro(a_macro):
                send_chat(message, msg_add_macro_success())
            else:
                send_chat(message, msg_add_macro_fail())

    # End of echo_all(message)
    pass



############################################
# Callback functions
############################################

def incoming_cmd_callback(recv):
    # Process received information
    if recv[0] == 1:    # received packet
        if recv[4] == 17:  # 0x11 : Register device
            print ''
        elif recv[4] == 81: # 0x51 : Update sensor data
            print ''
        elif recv[4] == 1: # 0x01 : Ping response
            # get matching device
            device = t_dev.get_device(recv[1], recv[2], recv[3])
            if len(device) < 1:
                return
            msg = ''
            msg += device[13]
            msg += ", "+msg_location()+"="
            msg += device[14]
            msg += "\n"+msg_category()+"1=" + str(device[1])
            msg += ", "+msg_category()+"2=" + str(device[2])
            msg += ", ID=" + str(device[3])
            msg += "\n\n" + msg_recv_ping_response()
            send_chat(None, msg)
        elif recv[4] == 129: # 0x81 : Control signal response
            # get matching device
            device = t_dev.get_device(recv[1], recv[2], recv[3])
            if len(device) < 1:
                return
            msg = ''
            msg += device[13]
            msg += ", "+msg_location()+"="
            msg += device[14]
            msg += "\n"+msg_category()+"1=" + str(device[1])
            msg += ", "+msg_category()+"2=" + str(device[2])
            msg += ", ID=" + str(device[3])
            msg += "\n\n" + msg_ctrlsignal_response() + "\n"
            msg += get_cmd_name(device[5])
            msg += "="
            msg += str(recv[5])
            msg += "\n"
            msg += get_cmd_name(device[7])
            msg += "="
            msg += str(recv[6])
            msg += "\n"
            msg += get_cmd_name(device[9])
            msg += "="
            msg += str(recv[7])
            msg += "\n"
            msg += get_cmd_name(device[11])
            msg += "="
            msg += str(recv[8])
            send_chat(None, msg)
    # End of incoming_cmd_callback()
    return


CALLBACK_TYPE_NOTI = 1
CALLBACK_TYPE_MACRO = 2

def device_thread_callback(type, recv, command):
    if type == CALLBACK_TYPE_NOTI:
        msg = ''
        msg += recv[13]
        msg += ", " + msg_location() + "="
        msg += recv[14]
        msg += "\n" + msg_category() +"1=" + str(recv[1])
        msg += ", " + msg_category() +"2=" + str(recv[2])
        msg += ", ID=" + str(recv[3])
        msg += "\n\n" + msg_noti_received()
        send_chat(None, msg)
    elif type == CALLBACK_TYPE_MACRO:
        parseCommand(None, command)
        print '    macro command = ' + command
    # End of device_thread_callback()
    return

def send_chat(message, str_msg):
    if message is None:
        bot.send_message(CHAT_ID, str_msg)
    else:
        bot.reply_to(message, str_msg)
    return

def send_photo(message, file):
    if message is None:
        ret_msg = bot.send_photo(CHAT_ID, file)
    else:
        ret_msg = bot.send_photo(message.chat.id, file)



############################################
# Python starts here
############################################

start = time.time()
print start

# Load configurations
config = Configurations()
# Apply configurations
env_lang = config.get_language()
set_proto_lang(env_lang)
set_msg_lang(env_lang)
# Get network IP addr
if cctv_url == '':
    cctv_url = 'http://'
    tempstr = subprocess.check_output('dig +short myip.opendns.com @resolver1.opendns.com', shell=True)
    tempstr.replace('\r', '')
    tempstr.replace('\n', '')
    cctv_url += tempstr.strip()
    cctv_url += ':' + cctv_port
print 'Found external IP = ' + cctv_url
# Initialize DB
dbhelper = DBHelper(MYSQL_USER, MYSQL_PASS, MYSQL_DB)
dbhelper.connect()
dbhelper.checktables()
# Connect serial
t_ser = SerialThread(recv_queue, send_queue, incoming_cmd_callback)
t_ser.connect()
# Make worker thread
t_dev = DeviceManagerThread(dbhelper, recv_queue, send_queue, device_thread_callback)

# Start main loop
if __name__ == '__main__':
    try:
        # Start worker thread
        t_dev.load_devices()
        t_dev.load_noti()
        t_dev.load_macro()
        t_dev.setDaemon(True)
        t_dev.start()
        # Start serial monitor thread
        t_ser.setDaemon(True)
        t_ser.start()
        # Delete unused devices
        #
        # Instantiate telegram interface
        print 'Start polling from telegram...'
        print ' '
        print ' '
        bot.polling()

        # Telegram polling() function stops the main procedure
        # If you wish to do something while running
        # do the job in WorkerThread or SerialThread
        print 'HomePy terminated !!'

    except KeyboardInterrupt:
        # Quit gracefully
        print ' '
        print 'Keyboard interrupt'
        print 'Cleaning up the resources...'
        dbhelper.close()
        t_ser.close()
        t_dev.close()
        recv_queue.join()    # block until all tasks are done
        send_queue.join()
        print "Elapsed Time: %s" % (time.time() - start)
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

# Quit gracefully
print ' '
print 'Cleaning up the resources...'
dbhelper.close()
t_ser.close()
t_dev.close()
recv_queue.join()    # block until all tasks are done
send_queue.join()

print "Elapsed Time: %s" % (time.time() - start)

