#-*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import Queue
import threading
import time
import logging

import serial
import urllib2
#import pyowm
import MySQLdb
import CairoPlot
import cairo
import math
import subprocess
from decimal import *

from DBHelper import DBHelper
from SerialThread import SerialThread
from DeviceManagerThread import DeviceManagerThread
from HCProtocol import *
from MessageBox import *
from Utilities import *
from Configurations import Configurations
from DeviceInfo import *
from SensorInfo import *
from MacroInfo import *
from NotiInfo import *


# Telegram python interface
import telebot
from telebot import types



############################################
# Global variables
############################################

# Load configurations
config = Configurations()

# Telegram bot interface
CHAT_ID = 0
tmpid = config.get_chat_id()
if tmpid.isdigit():
    CHAT_ID = int(tmpid)
API_TOKEN = config.get_bot_token()
API_TOKEN.strip()
bot = telebot.TeleBot(API_TOKEN)

MYSQL_USER = config.get_mysql_user()
MYSQL_DB = config.get_mysql_db()
MYSQL_PASS = config.get_mysql_pass()

CCTV_URL = config.get_cctv_url()
CCTV_URL.strip()
CCTV_PORT = config.get_cctv_port()
CCTV_PORT.strip()
CCTV_START_CMD = config.get_cctv_start_cmd()
CCTV_STOP_CMD = config.get_cctv_stop_cmd()

PHOTO_CMD = config.get_photo_cmd()
PICTURE_DIR = config.get_picture_dir()
PICTURE_DIR.strip()
GRAPH_DIR = config.get_graph_dir()
GRAPH_DIR.strip()

# Camera
is_cctv_active = False
# Queue
recv_queue = Queue.Queue()
send_queue = Queue.Queue()
# Keypad
keypad_target_dev = -1

# Logging
logging.basicConfig(filename='homepy.log',level=logging.WARNING)



############################################
# Telegram message handler
############################################

# Example of telegram message handler
#@bot.message_handler(commands=['record', 'rec'])
#def cctv_off(message):
#    send_chat(message, 'Sorry, not implemented yet...')

# Slash commands and markup command handler
# : Only slash commands are allowed in group chat.
# : check if string starts with '/'
# : or filtering '[xxxxx]' string
@bot.message_handler(regexp="[^/{1}[^/]|^\[[[:alnum:]]+\]$]")
def bot_slash_cmd(message):
    global CHAT_ID

    # Markup command handler
    # Music
    if message.text == '[prev]':
        results = subprocess.check_output('mpc prev', shell=True)
        send_chat(message, 'Music: play previous song.\n' + results)
        return
    elif message.text == '[play]':
        results = subprocess.check_output('mpc toggle', shell=True)
        send_chat(message, 'Music: toggle play/pause\n' + results)
        return
    elif message.text == '[next]':
        results = subprocess.check_output('mpc next', shell=True)
        send_chat(message, 'Music: play next song.\n' + results)
        return
    elif message.text == '[pause]':
        results = subprocess.check_output('mpc toggle', shell=True)
        send_chat(message, 'Music: toggle play/pause\n' + results)
        return
    elif message.text == '[stop]':
        results = subprocess.check_output('mpc stop', shell=True)
        send_chat(message, 'Music: stop playing\n' + results)
        return
    elif message.text == '[exit]':
        markup = types.ReplyKeyboardHide(selective=False)
        bot.send_message(message.chat.id, "Music controller closed.", reply_markup=markup)
        return
    elif message.text == '[random]':
        results = subprocess.check_output('mpc random', shell=True)
        send_chat(message, 'Music: toggle random mode\n' + results)
        return
    elif message.text == '[repeat]':
        results = subprocess.check_output('mpc repeat', shell=True)
        send_chat(message, 'Music: toggle repeat mode\n' + results)
        return
    elif message.text == '[consume]':
        results = subprocess.check_output('mpc consume', shell=True)
        send_chat(message, 'Music: toggle consume mode\n' + results)
        return
    # Keypad
    elif message.text == '[Enter]':
        send_keycode(message, 10)
        return
    elif message.text == '[/]':
        send_keycode(message, 47)
        return
    elif message.text == '[*]':
        send_keycode(message, 42)
        return
    elif message.text == '[-]':
        send_keycode(message, 45)
        return
    elif message.text == '[7]':
        send_keycode(message, 55)
        return
    elif message.text == '[8]':
        send_keycode(message, 56)
        return
    elif message.text == '[9]':
        send_keycode(message, 57)
        return
    elif message.text == '[+]':
        send_keycode(message, 43)
        return
    elif message.text == '[4]':
        send_keycode(message, 52)
        return
    elif message.text == '[5]':
        send_keycode(message, 53)
        return
    elif message.text == '[6]':
        send_keycode(message, 54)
        return
    elif message.text == '[.]':
        send_keycode(message, 46)
        return
    elif message.text == '[1]':
        send_keycode(message, 49)
        return
    elif message.text == '[2]':
        send_keycode(message, 50)
        return
    elif message.text == '[3]':
        send_keycode(message, 51)
        return
    elif message.text == '[0]':
        send_keycode(message, 48)
        return

    # update chat id
    if CHAT_ID < 1:
        config.set_chat_id(message.chat.id)
    CHAT_ID = message.chat.id
    escaped = message.text.replace('/', '')
    parse_command(message, escaped)


# Nomal text handler
# : for 1:1 chat with bot
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    global is_cctv_active
    global CHAT_ID
    global CCTV_URL

    # update chat id
    if CHAT_ID < 1:
       config.set_chat_id(message.chat.id)
    CHAT_ID = message.chat.id
    parse_command(message, message.text)
    pass

# Parse command
def parse_command(message, str_cmd):
    global keypad_target_dev
    global is_cctv_active
    global CHAT_ID
    global CCTV_URL

    # split message
    cmd = str_cmd.strip().split(' ')
    
    # Bot check command
    if cmd[0] == 'hello' or cmd[0] == 'hi' or cmd[0] == '하이' or cmd[0] == '안녕':
        send_chat(message, msg_welcome())
        return

    # Send chat message
    if cmd[0] == 'chat' or cmd[0] == '챗':
        if len(cmd) > 1:
            str_msg = 'Bot msg: '
            for index in range(1, len(cmd)):
                str_msg += cmd[index] + ' '
            str_msg.strip()
            send_chat(message, str_msg)

    # Ping test
    elif cmd[0] == 'help' or cmd[0] == '도움말':
        send_chat(message, msg_help_text())
        return

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
        if device is None:
            send_chat(message, msg_device_not_found() + ' ' + str(devnum))
            return
        t_ser.send(device.cat1, device.cat2, device.devid, 0x01, 0, 0, 0, 0)
        return

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
        return

    # Control MPD (need MPC)
    elif cmd[0] == 'mpc' or cmd[0] == 'music' or cmd[0] == '음악' or cmd[0] == '뮤직':
        # show queued songs
        if len(cmd) < 2:
            results = subprocess.check_output('mpc playlist', shell=True)
            a_res = results.split('\n')
            disp_str = ''
            index = 1
            for item in a_res:
                if item != '':
                    disp_str += str(index) + '. ' + item + '\n'
                    index += 1
            send_chat(message, '[] '+msg_current_queue()+': \n' + disp_str)
            return

        # play
        elif cmd[1] == 'play' or cmd[1] == '재생' or cmd[1] == '플레이':
            # play
            if len(cmd) < 3:
                results = subprocess.check_output('mpc play', shell=True)
                send_chat(message, results)
                return
            # check parameter: playlist number
            if cmd[2].isdigit() == False:
                send_chat(message, msg_invalid_playlist())
                return
            # push playlist into current queue
            tmpcheck = subprocess.check_output('mpc play '+cmd[2], shell=True)
            send_chat(message, tmpcheck)
            return

        # stop
        elif cmd[1] == 'stop' or cmd[1] == '정지':
            tmpcheck = subprocess.check_output('mpc stop', shell=True)
            send_chat(message, tmpcheck)
            return

        # playlist handler
        elif cmd[1] == 'playlist' or cmd[1] == '재생목록':
            # show playlists
            if len(cmd) < 3:
                results = subprocess.check_output('mpc lsplaylists', shell=True)
                a_res = results.split('\n')
                disp_str = ''
                index = 1
                for item in a_res:
                    if item != '':
                        disp_str += str(index) + '. ' + item + '\n'
                        index += 1
                send_chat(message, '[*] Playlists: \n' + disp_str)
                return
            # check parameter: playlist number
            if cmd[2].isdigit() == False:
                send_chat(message, msg_invalid_playlist())
                return
            # push playlist into current queue
            playlist_num = int(cmd[2])
            results = subprocess.check_output('mpc lsplaylists', shell=True)
            a_res = results.split('\n')
            disp_str = ''
            index = 1
            selected = 0
            for item in a_res:
                if item != '':
                    if playlist_num == index:
                        disp_str = item
                        selected = index
                    index += 1
            if selected > 0:
                tmpcheck = subprocess.check_output('mpc current', shell=True)
                if tmpcheck == '' or tmpcheck is None or len(tmpcheck) < 3:
                    # current status: stopped - clear all
                    subprocess.check_output('mpc clear', shell=True)
                else:
                    # current status: stopped - clear except current playing
                    subprocess.check_output('mpc crop', shell=True)
                results = subprocess.check_output('mpc load '+disp_str, shell=True)
                send_chat(message, 'Playlist '+msg_changed_to()+' \n' + disp_str)
            else:
                send_chat(message, msg_invalid_playlist())
            return

        # control panel
        if cmd[1] == 'ctrl' or cmd[1] == 'control' or cmd[1] == '리모콘' or cmd[1] == '컨트롤':
            if len(cmd) > 2 and (cmd[2] == 'off' or cmd[2] == '닫기' or cmd[2]=='오프'):
                markup = types.ReplyKeyboardHide(selective=False)
                bot.send_message(CHAT_ID, 'Music '+msg_control_panel_closed(), reply_markup=markup)
            else:
                markup = types.ReplyKeyboardMarkup(row_width=3)
                markup.add('[prev]', '[play]', '[next]', '[pause]', '[stop]', '[exit]', '[random]', '[repeat]', '[consume]')
                bot.send_message(CHAT_ID, 'Music '+msg_control_panel()+': ', reply_markup=markup)
            return

    # Keypad: control panel
    if cmd[0] == 'keypad' or cmd[0] == 'control' or cmd[0] == '키패드' or cmd[0] == '컨트롤':
        # close keypad
        if len(cmd) > 1 and (cmd[1] == 'off' or cmd[1] == 'close' or cmd[1] == '닫기' or cmd[1]=='오프'):
            markup = types.ReplyKeyboardHide(selective=False)
            bot.send_message(CHAT_ID, msg_keypad()+' '+msg_control_panel_closed(), reply_markup=markup)
        # show current target device
        elif len(cmd) == 2 and (cmd[1] == 'dev' or cmd[1] == 'set' or cmd[1] == '장치' or cmd[1]=='설정'):
            send_chat(message, msg_k+' = '+str(keypad_target_dev))
        # set target device
        elif len(cmd) > 2 and (cmd[1] == 'dev' or cmd[1] == 'set' or cmd[1] == '장치' or cmd[1]=='설정'):
            if cmd[2].isdigit():
                devnum = -1
                devnum = int(cmd[2])
                device = t_dev.get_device_at(devnum)
                if device is None:
                    send_chat(message, msg_wrong_device())
                    return;
                keypad_target_dev = devnum
                send_chat(message, msg_keypad_set_dev()+' : '+str(keypad_target_dev))
            else:
                send_chat(message, msg_wrong_device())
            return
        # open keypad
        else:
            markup = types.ReplyKeyboardMarkup(row_width=4)
            markup.add('[/]', '[*]', '[+]', '[-]', '[7]', '[8]', '[9]', '[Enter]', '[4]', '[5]', '[6]', '[.]', '[1]', '[2]', '[3]', '[0]')
            bot.send_message(CHAT_ID, msg_keypad()+': ', reply_markup=markup)
        return

    # cctv command
    elif cmd[0] == 'cctv' or cmd[0] == 'cam' or cmd[0] == '캠':
        if len(cmd) < 2:
            send_chat(message, msg_invalid_param())
            return
        if cmd[1] == 'on' or cmd[1] == '온':
            if is_cctv_active:
                send_chat(message, msg_cctv_already_on() + ' ' + CCTV_URL)
                return
            else:
                #if CCTV_URL == '':
                #    CCTV_URL = 'http://'
                #    CCTV_URL += subprocess.check_output('wget -q http://ip.kiduk.kr && more index.html', shell=True)
                #    CCTV_URL += ':' + CCTV_PORT
                os.system(CCTV_START_CMD)
                send_chat(message, msg_cctv_on() + ' ' + CCTV_URL)
                is_cctv_active = True
        elif cmd[1] == 'off' or cmd[1] == '오프':
            os.system(CCTV_STOP_CMD)
            send_chat(message, msg_cctv_off())
            is_cctv_active = False
        return

    # take a picture
    elif cmd[0] == 'pic' or cmd[0] == 'picture' or cmd[0] == '사진':
        # remove pictures in picture directory
        if len(cmd) > 1 and (cmd[1] == 'remove' or cmd[1] == 'del' or cmd[1] == 'delete' or cmd[1] == '삭제' or cmd[1] == '제거'):
            os.system('rm -f '+PICTURE_DIR+'image_*.jpg')
            send_chat(message, msg_remove_pictures())
            return

        # Stop cctv first
        if is_cctv_active:
            send_chat(message, msg_turnoff_cctv())
        os.system(CCTV_STOP_CMD)
        is_cctv_active = False
        time.sleep(1)  # Sleep for a while to avoid camera access error

        # Take a still shot
        now = time.localtime()
        pic_file_name = "image_%04d-%02d-%02d_%02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
        pic_file_name += '.jpg'
        os.system(PHOTO_CMD + ' ' + PICTURE_DIR + pic_file_name)

        # Send picture
        try:
            pic_file = open(PICTURE_DIR + pic_file_name, 'rb')
            ret_msg = send_photo(message, pic_file)  # message.chat.id
        except:
            send_chat(message, 'Cannot take a picture!!')
        return

    # Device command
    elif cmd[0] == 'dev' or cmd[0] == 'device' or cmd[0] == '장치':
        # Device - Show device list
        if len(cmd) < 2:
            count = 0
            msg = ''
            devices = t_dev.get_device_list()
            for device in devices:
                msg += str(count+1) + ". "
                msg += device.name
                msg += ", " + msg_location() + "="
                msg += device.loc
                msg += "\n" + msg_category() +"1=" + str(device.cat1)
                msg += ", " + msg_category() +"2=" + str(device.cat2)
                msg += ", ID=" + str(device.devid)
                msg += "\n\n"
                count = count + 1
            if count < 1:
                msg += msg_device_not_found()
            else:
                msg += msg_devdesc_command()
            send_chat(message, msg)
            return
        # Device - Show device details
        elif cmd[1] == 'desc' or cmd[1] == 'detail' or cmd[1] == '상세':
            if len(cmd) >= 3:
                msg = ''
                devnum = -1
                if cmd[2].isdigit():
                    devnum = int(cmd[2])
                device = t_dev.get_device_at(devnum)
                if device is not None:
                    msg += msg_device_number() + " = " + str(devnum) + "\n"
                    msg += device.name
                    msg += ", " + msg_location() + "="
                    msg += device.loc
                    msg += "\n" + msg_category() + "1=" + str(device.cat1)
                    msg += ", " + msg_category() + "2=" + str(device.cat2)
                    msg += ", ID=" + str(device.devid)
                    msg += "\n" + msg_update_time() + "=" + time.asctime(time.localtime(device.time))
                    msg += "\n\n"
                    msg += msg_control_signal() + "1="
                    msg += get_cmd_name(device.cmd1)
                    msg += ", " + msg_data_type() + "1="
                    msg += get_cmd_type_name(device.cmd1dtype)
                    msg += "\n"
                    msg += msg_control_signal() + "2="
                    msg += get_cmd_name(device.cmd2)
                    msg += ", " + msg_data_type() + "2="
                    msg += get_cmd_type_name(device.cmd2dtype)
                    msg += "\n"
                    msg += msg_control_signal() + "3="
                    msg += get_cmd_name(device.cmd3)
                    msg += ", " + msg_data_type() + "3="
                    msg += get_cmd_type_name(device.cmd3dtype)
                    msg += "\n"
                    msg += msg_control_signal() + "4="
                    msg += get_cmd_name(device.cmd4)
                    msg += ", " + msg_data_type() + "4="
                    msg += get_cmd_type_name(device.cmd4dtype)
                    msg += "\n\n" + msg_ctrlsignal_desc()
                else:
                    msg += msg_device_not_found()
                send_chat(message, msg)
            return

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
            return

        # Device - Remove all devices
        elif cmd[1] == 'removeall' or cmd[1] == 'delall' or cmd[1] == 'deleteall' or cmd[1] == '모두삭제' or cmd[1] == '모두제거':
            if t_dev.delete_devices_all():
                send_chat(message, msg_every_device_removed())
            else:
                send_chat(message, msg_every_device_remove_error())
            return

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
            return

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
            if devnum < 0:
                send_chat(message, msg_wrong_device())
                return
            infos = t_dev.get_sensor_val(devnum, count)
            if infos is None or len(infos) < 1:
                send_chat(message, msg_no_matching_result())
                return
            msg = ''
            i = 0
            for info in infos:
                itime = time.localtime(info.time)
                msg += "%d-%d %d:%d" % (itime.tm_mon, itime.tm_mday, itime.tm_hour, itime.tm_min)
                msg += " = %d, %d, %d, %d" % (info.data1, info.data2, info.data3, info.data4)
                msg += "\n"
                i = i + 1
            if i > 0:
                send_chat(message, msg)
            else:
                send_chat(message, msg_no_matching_result())
        return

    # Get sensor value and return with graph
    elif cmd[0] == 'graph' or cmd[0] == '그래프':
        if len(cmd) == 2 and (cmd[1] == 'remove' or cmd[1] == 'del' or cmd[1] == 'delete' or cmd[1] == '삭제' or cmd[1] == '제거'):
            os.system('rm -f '+GRAPH_DIR+'graph_*.png')
            send_chat(message, msg_remove_pictures())
            return

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
        if devnum < 0:
            send_chat(message, msg_wrong_device())
            return
        infos = t_dev.get_sensor_val(devnum, count)
        if infos is None or len(infos) < 1:
            send_chat(message, msg_no_matching_result())
            return
        # making data list
        i = 0
        datas = [[], [], [], []]
        h_labels = []
        prev_d, prev_h, prev_m = 0, 0, 0
        for info in infos:
            itime = time.localtime(info.time)
            if prev_d != itime.tm_mday or prev_h != itime.tm_hour or prev_m != itime.tm_min:
                timestr = "%d-%d %d:%d" % (itime.tm_mon, itime.tm_mday, itime.tm_hour, itime.tm_min)
            else:
                timestr = "%d:%d" % (itime.tm_hour, itime.tm_min)
            prev_d, prev_h, prev_m = itime.tm_mday, itime.tm_hour, itime.tm_min
            datas[0].append(info.data1)
            datas[1].append(info.data2)
            datas[2].append(info.data3)
            datas[3].append(info.data4)
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
            CairoPlot.dot_line_plot(GRAPH_DIR + fname,
                    datas, width, height,
                    h_labels = h_labels, v_labels = [],
                    axis = True, grid = True, dots = True)
            try:
                # Send graph
                pic_file = open(GRAPH_DIR + fname, 'rb')
                ret_msg = send_photo(message, pic_file)
            except:
                send_chat(message, msg_cannot_open_graph())
        else:
            send_chat(message, msg_no_matching_result())
        return

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
        if device is None:
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
        t_ser.send_control_signal(device.cat1, device.cat2, device.devid, data1, data2, data3, data4)
        send_chat(message, msg_sent_signal() % devnum)
        return

    # Make notification setting
    elif cmd[0] == 'noti' or cmd[0] == 'notification' or cmd[0] == '알림':
        # Show current notifications
        if len(cmd) < 2:
            strmsg = ''
            notis = t_dev.get_noti_list()
            count = 0
            for noti in notis:
                strmsg += msg_noti() + ' ID = ' + str(noti.id) + '\n'
                #strmsg += noti[13] + '\n'
                strmsg += msg_category() + "1=" + str(noti.cat1)
                strmsg += ", " + msg_category() + "2=" + str(noti.cat2)
                strmsg += ", ID=" + str(noti.devid) + "\n" + "if "
                tmpcount = 0
                if noti.comp1 > 0:
                    strmsg += "Data1 "
                    strmsg += get_comp_operator(noti.comp1) + " "
                    strmsg += str(noti.data1) + "\n"
                    tmpcount += 1
                if noti.comp2 > 0:
                    if tmpcount > 0:
                        strmsg += "and "
                    strmsg += "Data2 "
                    strmsg += get_comp_operator(noti.comp2) + " "
                    strmsg += str(noti.data2) + "\n"
                    tmpcount += 1
                if noti.comp3 > 0:
                    if tmpcount > 0:
                        strmsg += "and "
                    strmsg += "Data3 "
                    strmsg += get_comp_operator(noti.comp3) + " "
                    strmsg += str(noti.data3) + "\n"
                    tmpcount += 1
                if noti.comp4 > 0:
                    if tmpcount > 0:
                        strmsg += "and "
                    strmsg += "Data4 "
                    strmsg += get_comp_operator(noti.comp4) + " "
                    strmsg += str(noti.data4) + "\n"
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
            noti = NotiInfo()
            noti.cat1 = cat1
            noti.cat2 = cat2
            noti.devid = devid
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
            noti.comp1 = compcode1
            noti.comp2 = compcode2
            noti.comp3 = compcode3
            noti.comp4 = compcode4
            noti.data1 = targetnum1
            noti.data2 = targetnum2
            noti.data3 = targetnum3
            noti.data4 = targetnum4
            noti.time = int(time.time())
            cur = time.localtime()
            noti.name = 'Noti' + str(cur.tm_mon) + str(cur.tm_mday) + str(cur.tm_hour) + str(cur.tm_min) + str(cur.tm_sec)
            # push to DB and cached list
            if t_dev.add_noti(noti):
                send_chat(message, msg_add_noti_success())
            else:
                send_chat(message, msg_add_noti_failed())
        # Invalid notification command
        else:
            send_chat(message, msg_invalid_noti_cmd())
        return

    # Make macro
    elif cmd[0] == 'macro' or cmd[0] == '매크로':
        # Show macro list
        if len(cmd) < 2:
            strmsg = ''
            macros = t_dev.get_macro_list()
            count = 0
            for macro in macros:
                if macro.interval > 0 or macro.nid < 0:  # filtering macro
                    continue
                strmsg += msg_macro() + ' ID = ' + str(macro.id) + '\n'
                strmsg += '-> If ' + msg_noti() + 'ID == ' + str(macro.nid) + ', Do : '
                strmsg += macro.cmd + '\n'
                count += 1
            if count > 0:
                send_chat(message, strmsg)
            else:
                strmsg += '\n'
                send_chat(message, msg_no_macro())
            # End of 'macro' command
            return

        # Delete macro
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

        # Add macro (noti-triggered)
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
            if noti is None:
                send_chat(message, msg_invalid_noti_id())
                return
            cat1 = noti.cat1
            cat2 = noti.cat2
            devid = noti.devid
            if cat1 < 0 or cat2 < 0 or devid < 0:
                send_chat(message, msg_wrong_device())
                return
            str_cmd = ""
            for index in range(3, len(cmd)):
                str_cmd += cmd[index] + ' '
            str_cmd.strip()
            o_macro = MacroInfo()
            o_macro.nid = noti_num  # noti id
            o_macro.cat1 = cat1     # cat1
            o_macro.cat2 = cat2     # cat2
            o_macro.devid = devid   # device ID
            o_macro.time = int(time.time())  # updated
            o_macro.cmd = str_cmd   # command
            o_macro.interval = 0    # interval (for timer)
            if t_dev.add_macro(o_macro):
                send_chat(message, msg_add_macro_success())
            else:
                send_chat(message, msg_add_macro_fail())
            return

    # Make timer
    elif cmd[0] == 'timer' or cmd[0] == '타이머':
        # Show timer list
        if len(cmd) < 2:
            strmsg = ''
            macros = t_dev.get_macro_list()
            count = 0
            for macro in macros:
                if macro.nid > -1:  # filter out noti-triggered macro
                    continue
                strmsg += msg_timer() + ' ID = ' + str(macro.id) + '\n'
                if macro.interval < 1:  # time based timer
                    strmsg += '-> At ' + str(macro.hour) + ':' + str(macro.minute) + ', Do : '
                else:    # interval based timer
                    strmsg += '-> Every ' + str(macro.interval) + ' min, Do : '
                strmsg += macro.cmd + '\n'
                count += 1
            if count > 0:
                send_chat(message, strmsg)
            else:
                strmsg += '\n'
                send_chat(message, msg_no_timer())
            # End of 'timer' command
            return

        # Delete timer
        elif cmd[1] == 'delete' or cmd[1] == 'del' or cmd[1] == '삭제' or cmd[1] == '제거':
            if len(cmd) < 3:
                send_chat(message, msg_type_timer_del_param())
                return
            else:
                if len(cmd) == 3 and cmd[2].isdigit():
                    # delete with timer-ID
                    timer_id = int(cmd[2])
                    if t_dev.delete_macro_with_id(timer_id):
                        send_chat(message, msg_timer_del_success())
                    else:
                        send_chat(message, msg_timer_del_fail())
                    return
                else:
                    # cannot delete timer
                    send_chat(message, msg_timer_del_fail())
                    return

        # Add timer
        elif cmd[1] == 'add' or cmd[1] == '추가':
            if len(cmd) < 4:
                send_chat(message, msg_add_timer_param())
                return
            interval = -1
            ihour = 0
            imin = 0
            # time interval timer
            if cmd[2].isdigit():
                interval = int(cmd[2])
            # reserved time
            else:
                if cmd[2].find(':') < 0:
                    send_chat(message, msg_add_timer_param())
                    return
                else:
                    tmpstr = cmd[2].split(':')
                    if len(tmpstr) != 2:
                        send_chat(message, msg_add_timer_param())
                        return
                    if tmpstr[0].isdigit() and tmpstr[1].isdigit():
                        ihour = int(tmpstr[0])
                        imin = int(tmpstr[1])
                    else:
                        send_chat(message, msg_add_timer_param())
                        return
            str_cmd = ""
            for index in range(3, len(cmd)):
                str_cmd += cmd[index] + ' '
            str_cmd.strip()
            o_macro = MacroInfo()
            o_macro.time = int(time.time())  # updated
            o_macro.cmd = str_cmd        # command
            o_macro.interval = interval  # interval (for timer)
            o_macro.hour = ihour         # reserved time - hour
            o_macro.minute = imin        # reserved time - min
            if t_dev.add_macro(o_macro):
                send_chat(message, msg_add_timer_success())
            else:
                send_chat(message, msg_add_timer_fail())
            return

    # End of echo_all(message)
    pass



############################################
# Callback functions
############################################

def incoming_cmd_callback(recv):
    if recv is None:
        print '    serial thread callback: Critical error!!! recv is not an object!!!'
        return
    # Process received information
    if recv.objtype == 1:    # received packet
        if recv.cmd == 17:  # 0x11 : Register device
            print ''
        elif recv.cmd == 81: # 0x51 : Update sensor data
            print ''
        elif recv.cmd == 1: # 0x01 : Ping response
            # get matching device
            device = t_dev.get_device(recv.cat1, recv.cat2, recv.devid)
            if device is None:
                print '    home.py dev callback: error!! There is no matching device!!'
                return
            msg = ''
            msg += device.name
            msg += ", "+msg_location()+"="
            msg += device.loc
            msg += "\n"+msg_category()+"1=" + str(device.cat1)
            msg += ", "+msg_category()+"2=" + str(device.cat2)
            msg += ", ID=" + str(device.devid)
            msg += "\n\n" + msg_recv_ping_response()
            send_chat(None, msg)
        elif recv.cmd == 129: # 0x81 : Control signal response
            # get matching device
            device = t_dev.get_device(recv.cat1, recv.cat2, recv.devid)
            if device is None:
                print '    home.py dev callback: error!! There is no matching device!!'
                return
            msg = ''
            msg += device.name
            msg += ", "+msg_location()+"="
            msg += device.loc
            msg += "\n"+msg_category()+"1=" + str(device.cat1)
            msg += ", "+msg_category()+"2=" + str(device.cat2)
            msg += ", ID=" + str(device.devid)
            msg += "\n\n" + msg_ctrlsignal_response() + "\n"
            msg += get_cmd_name(device.cmd1)
            msg += "="
            msg += str(recv.data1)
            msg += "\n"
            msg += get_cmd_name(device.cmd2)
            msg += "="
            msg += str(recv.data2)
            msg += "\n"
            msg += get_cmd_name(device.cmd3)
            msg += "="
            msg += str(recv.data3)
            msg += "\n"
            msg += get_cmd_name(device.cmd4)
            msg += "="
            msg += str(recv.data4)
            send_chat(None, msg)
    # End of incoming_cmd_callback()
    return


CALLBACK_TYPE_NOTI = 1
CALLBACK_TYPE_MACRO = 2

def device_thread_callback(type, recv, command):
    if type == CALLBACK_TYPE_NOTI:
        if recv is None:
            logging.warning('    dev thread callback: Critical error!!! recv is not an object!!!')
            print '    dev thread callback: Critical error!!! recv is not an object!!!'
            return
        msg = ''
        msg += recv.name
        msg += ", " + msg_location() + "="
        msg += recv.loc
        msg += "\n" + msg_category() +"1=" + str(recv.cat1)
        msg += ", " + msg_category() +"2=" + str(recv.cat2)
        msg += ", ID=" + str(recv.devid)
        msg += "\n\n" + msg_noti_received()
        send_chat(None, msg)
        logging.warning('Noti callback launched!! device = ' + recv.name)
    elif type == CALLBACK_TYPE_MACRO:
        parse_command(None, command)
        logging.warning('Macro run with command: ' + command)
    # End of device_thread_callback()
    return



############################################
# Private functions
############################################

def send_chat(message, str_msg):
    if message is None:
        bot.send_message(CHAT_ID, str_msg)
    else:
        bot.reply_to(message, str_msg)
    return

# Send key code to selected device
def send_keycode(message, keycode):
    if keypad_target_dev < 0:
        send_chat(message, msg_wrong_device())
        return
    device = t_dev.get_device_at(keypad_target_dev)
    if device is None:
        send_chat(message, msg_wrong_device())
        return;
    # send device control signal to remote
    t_ser.send_control_signal(device.cat1, device.cat2, device.devid, keycode, 0, 0, 0)
    send_chat(message, msg_sent_signal() % keypad_target_dev)
    return

def send_photo(message, file):
    if message is None:
        ret_msg = bot.send_photo(CHAT_ID, file)
    else:
        ret_msg = bot.send_photo(message.chat.id, file)

def finalize():
    print '\nCleaning up the resources...'
    config.set_chat_id(str(CHAT_ID))
    dbhelper.close()
    t_ser.close()
    t_dev.close()
    recv_queue.join()    # block until all tasks are done
    send_queue.join()
    print "Elapsed Time: %s" % (time.time() - start)
    print "Bye~\n\n"



############################################
# Python starts here
############################################

start = time.time()
print start

# Apply configurations
env_lang = config.get_language()
print '    current language setting = ' + env_lang
set_proto_lang(env_lang)
set_msg_lang(env_lang)

# Get network IP addr
if CCTV_URL == '':
    CCTV_URL = 'http://'
    tempstr = subprocess.check_output('dig +short myip.opendns.com @resolver1.opendns.com', shell=True)
    tempstr.replace('\r', '')
    tempstr.replace('\n', '')
    CCTV_URL += tempstr.strip()
    CCTV_URL += ':' + CCTV_PORT
print 'Found external IP = ' + CCTV_URL
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
        print '==================================================\n'
        bot.polling()

        # Telegram polling() function stops the main procedure
        # If you wish to do something while running
        # do the job in WorkerThread or SerialThread
        print 'HomePy terminated !!'

    except KeyboardInterrupt:
        # Quit gracefully
        print '\n\nKeyboard interrupt !!!!!'
        finalize()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

# Quit gracefully
finalize()
