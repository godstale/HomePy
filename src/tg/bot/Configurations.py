#-*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os.path

import ConfigParser



SECTION_GLOBAL = 'GlobalParam'
OPTION_LANG = 'language'
SECTION_PRIVATE = 'PrivateParam'
OPTION_BOT_TOKEN = 'api_token'
OPTION_MYSQL_USER = 'mysql_user'
OPTION_MYSQL_DB = 'mysql_db'
OPTION_MYSQL_PASS = 'mysql_pass'
SECTION_SYSTEM = 'SystemParam'
OPTION_CCTV_URL = 'cctv_url'
OPTION_CCTV_PORT = 'cctv_port'
OPTION_CCTV_START_CMD = 'cctv_start_cmd'
OPTION_CCTV_STOP_CMD = 'cctv_stop_cmd'
OPTION_PHOTO_CMD = 'photo_cmd'
OPTION_PICTURE_DIR = 'picture_dir'
OPTION_GRAPH_DIR = 'graph_dir'

class Configurations:
    PATH = './HomePy.ini'

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        if os.path.isfile(self.PATH):
            print 'Found configurations...'
        else:
            print 'Serious error!!! Cannot find configuration file!!!!!!!'
            # Make config file
            #self.config.add_section(SECTION_GLOBAL)
            #self.config.set(SECTION_GLOBAL, OPTION_LANG, 'en')
            #self.config.add_section(SECTION_PRIVATE)
            #self.config.set(SECTION_PRIVATE, OPTION_BOT_TOKEN, 'write your telegram bot token')
            # Write configurations to 'HomePy.cfg'
            #with open(self.PATH, 'wb') as configfile:
            #    self.config.write(configfile)

        print 'Read configurations...'
        self.config.read(self.PATH)

    # language setting
    def get_language(self):
        if self.config.has_section(SECTION_GLOBAL) and self.config.has_option(SECTION_GLOBAL, OPTION_LANG):
            return self.config.get(SECTION_GLOBAL, OPTION_LANG)
        else:
            self.set_language('en')
            return 'en'

    def set_language(self, code):
        self.config.set(SECTION_GLOBAL, OPTION_LANG, code)
        # Write configurations to 'HomePy.cfg'
        with open(self.PATH, 'wb') as configfile:
            self.config.write(configfile)

    # telegram bot token
    def get_bot_token(self):
        if self.config.has_section(SECTION_PRIVATE) and self.config.has_option(SECTION_PRIVATE, OPTION_BOT_TOKEN):
            return self.config.get(SECTION_PRIVATE, OPTION_BOT_TOKEN)
        else:
            print '    Cannot find telegram bot token!!'
            return ''

    # mysql parameters
    def get_mysql_user(self):
        if self.config.has_section(SECTION_PRIVATE) and self.config.has_option(SECTION_PRIVATE, OPTION_MYSQL_USER):
            return self.config.get(SECTION_PRIVATE, OPTION_MYSQL_USER)
        else:
            print '    Cannot find MySQL user name!!'
            return ''

    def get_mysql_db(self):
        if self.config.has_section(SECTION_PRIVATE) and self.config.has_option(SECTION_PRIVATE, OPTION_MYSQL_DB):
            return self.config.get(SECTION_PRIVATE, OPTION_MYSQL_DB)
        else:
            print '    Cannot find MySQL DB name!!'
            return ''

    def get_mysql_pass(self):
        if self.config.has_section(SECTION_PRIVATE) and self.config.has_option(SECTION_PRIVATE, OPTION_MYSQL_PASS):
            return self.config.get(SECTION_PRIVATE, OPTION_MYSQL_PASS)
        else:
            print '    Cannot find MySQL password!!'
            return ''

    # CCTV parameters
    def get_cctv_url(self):
        if self.config.has_section(SECTION_SYSTEM) and self.config.has_option(SECTION_SYSTEM, OPTION_CCTV_URL):
            return self.config.get(SECTION_SYSTEM, OPTION_CCTV_URL)
        else:
            print '    Cannot find CCTV URL!!'
            return ''

    def get_cctv_port(self):
        if self.config.has_section(SECTION_SYSTEM) and self.config.has_option(SECTION_SYSTEM, OPTION_CCTV_PORT):
            return self.config.get(SECTION_SYSTEM, OPTION_CCTV_PORT)
        else:
            print '    Cannot find CCTV PORT!!'
            return '8891'

    def get_cctv_start_cmd(self):
        if self.config.has_section(SECTION_SYSTEM) and self.config.has_option(SECTION_SYSTEM, OPTION_CCTV_START_CMD):
            return self.config.get(SECTION_SYSTEM, OPTION_CCTV_START_CMD)
        else:
            print '    Cannot find CCTV start command!!'
            return '/home/pi/tg/bot/start_mjpg.sh'

    def get_cctv_stop_cmd(self):
        if self.config.has_section(SECTION_SYSTEM) and self.config.has_option(SECTION_SYSTEM, OPTION_CCTV_STOP_CMD):
            return self.config.get(SECTION_SYSTEM, OPTION_CCTV_STOP_CMD)
        else:
            print '    Cannot find CCTV stop command!!'
            return '/home/pi/tg/bot/stop_mjpg.sh'

    # Photo command
    def get_photo_cmd(self):
        if self.config.has_section(SECTION_SYSTEM) and self.config.has_option(SECTION_SYSTEM, OPTION_PHOTO_CMD):
            return self.config.get(SECTION_SYSTEM, OPTION_PHOTO_CMD)
        else:
            print '    Cannot find photo command!!'
            return 'sudo /usr/bin/raspistill -w 640 -h 480 -o'

    # path information
    def get_picture_dir(self):
        if self.config.has_section(SECTION_SYSTEM) and self.config.has_option(SECTION_SYSTEM, OPTION_PICTURE_DIR):
            return self.config.get(SECTION_SYSTEM, OPTION_PICTURE_DIR)
        else:
            print '    Cannot find picture directory!!'
            return '/home/pi/tg/bot/picture/'

    def get_graph_dir(self):
        if self.config.has_section(SECTION_SYSTEM) and self.config.has_option(SECTION_SYSTEM, OPTION_GRAPH_DIR):
            return self.config.get(SECTION_SYSTEM, OPTION_GRAPH_DIR)
        else:
            print '    Cannot find graph directory!!'
            return '/home/pi/tg/bot/graph/'
