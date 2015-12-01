#-*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import time
import MySQLdb

import traceback
from hc_protocol import *
from DeviceInfo import *
from SensorInfo import *
from MacroInfo import *
from NotiInfo import *


############################################
# DB helper
############################################

class DBHelper:
    sql_device_table = """CREATE TABLE devices (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        category1 INT NOT NULL,
        category2 INT NOT NULL,
        deviceid INT NOT NULL,
        name VARCHAR(64),
        location VARCHAR(64),
        updated INT UNSIGNED,
        cmd1 INT,
        cmd2 INT,
        cmd3 INT,
        cmd4 INT,
        type1 INT,
        type2 INT,
        type3 INT,
        type4 INT,
        temp1 INT,
        temp2 INT,
        temp3 FLOAT,
        temp4 VARCHAR(256)
        )"""

    sql_monitoring_table = """CREATE TABLE monitoring (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        category1 INT NOT NULL,
        category2 INT NOT NULL,
        deviceid INT NOT NULL,
        data1 INT,
        data2 INT,
        data3 INT,
        data4 INT,
        data5 FLOAT,
        data6 FLOAT,
        updated INT UNSIGNED,
        temp1 INT,
        temp2 INT,
        temp3 INT,
        temp4 INT,
        temp5 FLOAT,
        temp6 FLOAT,
        temp7 VARCHAR(256)
        )"""

    sql_noti_table = """CREATE TABLE notifications (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        category1 INT NOT NULL,
        category2 INT NOT NULL,
        deviceid INT NOT NULL,
        comp1 INT,
        comp2 INT,
        comp3 INT,
        comp4 INT,
        comp5 INT,
        comp6 INT,
        data1 INT,
        data2 INT,
        data3 INT,
        data4 INT,
        data5 FLOAT,
        data6 FLOAT,
        updated INT UNSIGNED,
        name VARCHAR(256),
        temp1 INT,
        temp2 INT,
        temp3 VARCHAR(256)
        )"""

    sql_macro_table = """CREATE TABLE macro (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        noti_id INT NOT NULL,
        category1 INT,
        category2 INT,
        deviceid INT,
        updated INT UNSIGNED,
        command VARCHAR(256),
        timeinterval INT,
        temp1 INT,
        temp2 INT,
        temp3 INT,
        temp4 VARCHAR(256)
        )"""

    def __init__(self, username, password, dbname):
        self.username = username
        self.password = password
        self.dbname = dbname

    def connect(self):
        self.db = MySQLdb.connect("localhost",self.username,self.password,self.dbname)
        self.cursor = self.db.cursor()

    def checktables(self):
        print 'Check database'
        retval = 0
        try:
            retval = self.cursor.execute("SELECT 1 FROM information_schema.tables WHERE TABLE_NAME like 'devices'")
            if retval < 1:
                print '    Cannot find devices table!!'
                self.maketables(1)
            retval = self.cursor.execute("SELECT 1 FROM information_schema.tables WHERE TABLE_NAME like 'monitoring'")
            if retval < 1:
                print '    Cannot find monitoring table!!'
                self.maketables(2)
            retval = self.cursor.execute("SELECT 1 FROM information_schema.tables WHERE TABLE_NAME like 'notifications'")
            if retval < 1:
                print '    Cannot find notifications table!!'
                self.maketables(3)
            retval = self.cursor.execute("SELECT 1 FROM information_schema.tables WHERE TABLE_NAME like 'macro'")
            if retval < 1:
                print '    Cannot find macro table!!'
                self.maketables(4)
        except:
            print '    Error!! Cannot execute table check query!!'
        return retval

    def maketables(self, ttype):
        try:
            if ttype == 1:
                print '    Making devices table...'
                self.cursor.execute(self.sql_device_table)
            elif ttype == 2:
                print '    Making monitoring table...'
                self.cursor.execute(self.sql_monitoring_table)
            elif ttype == 3:
                print '    Making notifications table...'
                self.cursor.execute(self.sql_noti_table)
            elif ttype == 4:
                print '    Making macro table...'
                self.cursor.execute(self.sql_macro_table)
        except:
            print '    Error!! Cannot make tables!!'
            return False
        print '    OK'
        return True

    def select_all_device(self):
        sql_query = "SELECT * FROM devices"
        # execute query
        try:
            print sql_query
            self.cursor.execute(sql_query)
            results = self.cursor.fetchall()
            return results
        except:
            print '    Cannot execute device select query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            return []

    def select_sensor_val(self, cat1, cat2, devid, count):
        sql_query = "SELECT * FROM monitoring WHERE category1="
        sql_query += str(cat1)
        sql_query += " AND category2="
        sql_query += str(cat2)
        sql_query += " AND deviceid="
        sql_query += str(devid)
        sql_query += " ORDER BY id DESC LIMIT "
        sql_query += str(count)
        # execute query
        try:
            #print sql_query
            self.cursor.execute(sql_query)
            results = self.cursor.fetchall()
            return results
        except:
            print '    Cannot execute device select query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            #dummy = list()
            return []

    def select_all_noti(self):
        sql_query = "SELECT * FROM notifications"
        # execute query
        try:
            print sql_query
            self.cursor.execute(sql_query)
            results = self.cursor.fetchall()
            return results
        except:
            print '    Cannot execute notification select query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            return []

    def select_all_macro(self):
        sql_query = "SELECT * FROM macro"
        # execute query
        try:
            print sql_query
            self.cursor.execute(sql_query)
            results = self.cursor.fetchall()
            return results
        except:
            print '    Cannot execute macro select query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            return []

    def add_device(self, device, update):
        if update > 0:
            # update row
            sql_query = "UPDATE devices SET name='"
            sql_query += device.name
            sql_query += "', location='"
            sql_query += device.loc
            sql_query += "', updated="
            sql_query += str(device.time)
            sql_query += ", cmd1="
            sql_query += str(device.cmd1)
            sql_query += ", cmd2="
            sql_query += str(device.cmd2)
            sql_query += ", cmd3="
            sql_query += str(device.cmd3)
            sql_query += ", cmd4="
            sql_query += str(device.cmd4)
            sql_query += ", type1="
            sql_query += str(device.cmd1dtype)
            sql_query += ", type2="
            sql_query += str(device.cmd2dtype)
            sql_query += ", type3="
            sql_query += str(device.cmd3dtype)
            sql_query += ", type4="
            sql_query += str(device.cmd4dtype)
            sql_query += " WHERE category1="
            sql_query += str(device.cat1)
            sql_query += " AND category2="
            sql_query += str(device.cat2)
            sql_query += " AND deviceid="
            sql_query += str(device.devid)
            #sql_query += ";"
        else:
            sql_query = """INSERT INTO devices (category1, category2, deviceid,
                            name, location, updated,
                            cmd1, cmd2, cmd3, cmd4,
                            type1, type2, type3, type4)
                            VALUES ("""
            sql_query += str(device.cat1)  # category 1
            sql_query += ','
            sql_query += str(device.cat2)  # category 2
            sql_query += ','
            sql_query += str(device.devid)  # device ID
            sql_query += ",'"
            sql_query += device.name   # name
            sql_query += "','"
            sql_query += device.loc   # location
            sql_query += "',"
            sql_query += str(device.time)  # updated time
            sql_query += ','
            sql_query += str(device.cmd1)  # cmd1
            sql_query += ','
            sql_query += str(device.cmd2)  # cmd2
            sql_query += ','
            sql_query += str(device.cmd3)  # cmd3
            sql_query += ','
            sql_query += str(device.cmd4)  # cmd4
            sql_query += ','
            sql_query += str(device.cmd1dtype)  # type1
            sql_query += ','
            sql_query += str(device.cmd2dtype)  # type2
            sql_query += ','
            sql_query += str(device.cmd3dtype)  # type3
            sql_query += ','
            sql_query += str(device.cmd4dtype)  # type4
            sql_query += ')'

        # execute query
        try:
            #print sql_query
            self.cursor.execute(sql_query)
            self.db.commit()
        except:
            print '    Cannot execute device insert/update query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.db.rollback()
            return False
        return True

    def add_monitoring_data(self, device):
        sql_query = """INSERT INTO monitoring (category1, category2, deviceid,
                            data1, data2, data3, data4, 
                            data5, data6, updated) VALUES ("""
        sql_query += str(device.cat1)  # category 1
        sql_query += ','
        sql_query += str(device.cat2)  # category 2
        sql_query += ','
        sql_query += str(device.devid)  # device ID
        sql_query += ','
        sql_query += str(device.data1)  # int 1
        sql_query += ','
        sql_query += str(device.data2)  # int 2
        sql_query += ','
        sql_query += str(device.data3)  # int 3
        sql_query += ','
        sql_query += str(device.data4)  # int 4
        sql_query += ','
        sql_query += str(device.fdata1)  # float 1
        sql_query += ','
        sql_query += str(device.fdata2)  # float 2
        sql_query += ','
        sql_query += str(device.time)  # updated time
        sql_query += ')'

        # execute query
        try:
            #print sql_query
            self.cursor.execute(sql_query)
            self.db.commit()
        except:
            print '    Cannot execute device insert/update query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.db.rollback()
            return False
        return True

    def add_noti(self, noti):
        sql_query = """INSERT INTO notifications (category1, category2, deviceid,
                            comp1, comp2, comp3, comp4,
                            data1, data2, data3, data4,
                            updated, name) VALUES ("""
        sql_query += str(noti.cat1)  # category 1
        sql_query += ','
        sql_query += str(noti.cat2)  # category 2
        sql_query += ','
        sql_query += str(noti.devid)  # device ID
        sql_query += ','
        sql_query += str(noti.comp1)  # comp 1
        sql_query += ','
        sql_query += str(noti.comp2)  # comp 2
        sql_query += ','
        sql_query += str(noti.comp3)  # comp 3
        sql_query += ','
        sql_query += str(noti.comp4)  # comp 4
        sql_query += ','
        sql_query += str(noti.data1)  # int 1
        sql_query += ','
        sql_query += str(noti.data2)  # int 2
        sql_query += ','
        sql_query += str(noti.data3)  # int 3
        sql_query += ','
        sql_query += str(noti.data4)  # int 4
        sql_query += ','
        sql_query += str(noti.time)  # updated time
        sql_query += ',"'
        sql_query += str(noti.name)  # name
        sql_query += '")'

        # execute query
        try:
            #print sql_query
            self.cursor.execute(sql_query)
            self.db.commit()
        except:
            print '    Cannot execute notification insert query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.db.rollback()
            return False
        return True

    def add_macro(self, macro):
        sql_query = """INSERT INTO macro (noti_id, category1, category2, deviceid,
                            updated, command, timeinterval) VALUES ("""
        sql_query += str(macro.nid)  # notification id
        sql_query += ','
        sql_query += str(macro.cat1)  # category 1
        sql_query += ','
        sql_query += str(macro.cat2)  # category 2
        sql_query += ','
        sql_query += str(macro.devid)  # device ID
        sql_query += ','
        sql_query += str(macro.time)  # updated time
        sql_query += ',"'
        sql_query += str(macro.cmd)  # command
        sql_query += '",'
        sql_query += str(macro.interval)  # interval (for timer)
        sql_query += ')'

        # execute query
        try:
            #print sql_query
            self.cursor.execute(sql_query)
            self.db.commit()
        except:
            print '    Cannot execute macro(timer) insert query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.db.rollback()
            return False
        return True

    def update_macro_time(self, mid, utime):
        sql_query = "UPDATE macro SET updated="
        sql_query += str(utime)
        sql_query += " WHERE id="
        sql_query += str(mid)
        #sql_query += ";"
        # execute query
        try:
            #print sql_query
            self.cursor.execute(sql_query)
            self.db.commit()
        except:
            print '    Cannot execute timer update query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.db.rollback()
            return False
        return True

    def delete_device(self, cat1, cat2, devid):
        sql_query = "DELETE FROM devices WHERE category1="
        sql_query += str(cat1)
        sql_query += " AND category2="
        sql_query += str(cat2)
        sql_query += " AND deviceid="
        sql_query += str(devid)

        sql_query2 = "DELETE FROM monitoring WHERE category1="
        sql_query2 += str(cat1)
        sql_query2 += " AND category2="
        sql_query2 += str(cat2)
        sql_query2 += " AND deviceid="
        sql_query2 += str(devid)

        # execute query
        try:
            #print sql_query
            self.cursor.execute(sql_query)
            self.db.commit()
            #print sql_query2
            self.cursor.execute(sql_query2)
            self.db.commit()
        except:
            print '    Cannot execute device delete query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.db.rollback()
            return False
        return True

    def delete_devices_all(self):
        sql_query = "DELETE FROM devices"
        sql_query2 = "DELETE FROM monitoring"
        # execute query
        try:
            #print sql_query
            self.cursor.execute(sql_query)
            self.db.commit()
            #print sql_query2
            self.cursor.execute(sql_query2)
            self.db.commit()
        except:
            print '    Cannot execute device delete all query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.db.rollback()
            return False
        return True

    def delete_sensor_val(self, cat1, cat2, devid, timestamp):
        sql_query = "DELETE FROM monitoring WHERE category1="
        sql_query += str(cat1)
        sql_query += " AND category2="
        sql_query += str(cat2)
        sql_query += " AND deviceid="
        sql_query += str(devid)
        if timestamp > 0:
            sql_query += " AND updated < "
            sql_query += str(timestamp)
        # execute query
        try:
            #print sql_query
            self.cursor.execute(sql_query)
            self.db.commit()
        except:
            print '    Cannot execute sensor delete query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.db.rollback()
            return False
        return True

    def delete_sensor_all(self, timestamp):
        sql_query = "DELETE FROM monitoring"
        if timestamp > 0:
            sql_query += " WHERE updated < "
            sql_query += str(timestamp)
        # execute query
        try:
            #print sql_query
            self.cursor.execute(sql_query)
            self.db.commit()
        except:
            print '    Cannot execute sensor delete all query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.db.rollback()
            return False
        return True

    def delete_noti_with_id(self, id):
        sql_query = "DELETE FROM notifications WHERE id="
        sql_query += str(id)

        # execute query
        try:
            #print sql_query
            self.cursor.execute(sql_query)
            self.db.commit()
        except:
            print '    Cannot execute noti delete (id) query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.db.rollback()
            return False
        return True

    def delete_noti_with_param(self, cat1, cat2, devid):
        sql_query = "DELETE FROM notifications WHERE category1="
        sql_query += str(cat1)
        sql_query += " AND category2="
        sql_query += str(cat2)
        sql_query += " AND deviceid="
        sql_query += str(devid)

        # execute query
        try:
            #print sql_query
            self.cursor.execute(sql_query)
            self.db.commit()
        except:
            print '    Cannot execute noti delete (device) query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.db.rollback()
            return False
        return True

    def delete_noti_with_name(self, name):
        sql_query = "DELETE FROM notifications WHERE name LIKE '%"
        sql_query += name
        sql_query += "%'"

        # execute query
        try:
            #print sql_query
            self.cursor.execute(sql_query)
            self.db.commit()
        except:
            print '    Cannot execute noti delete (name) query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.db.rollback()
            return False
        return True

    def delete_macro_with_id(self, id):
        sql_query = "DELETE FROM macro WHERE id="
        sql_query += str(id)

        # execute query
        try:
            #print sql_query
            self.cursor.execute(sql_query)
            self.db.commit()
        except:
            print '    Cannot execute macro delete (id) query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.db.rollback()
            return False
        return True

    def delete_macro_with_nid(self, nid):
        sql_query = "DELETE FROM macro WHERE noti_id="
        sql_query += str(nid)

        # execute query
        try:
            #print sql_query
            self.cursor.execute(sql_query)
            self.db.commit()
        except:
            print '    Cannot execute macro delete (noti id) query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.db.rollback()
            return False
        return True

    def delete_macro_with_param(self, cat1, cat2, devid):
        sql_query = "DELETE FROM macro WHERE category1="
        sql_query += str(cat1)
        sql_query += " AND category2="
        sql_query += str(cat2)
        sql_query += " AND deviceid="
        sql_query += str(devid)

        # execute query
        try:
            #print sql_query
            self.cursor.execute(sql_query)
            self.db.commit()
        except:
            print '    Cannot execute macro delete (device) query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.db.rollback()
            return False
        return True


    # disconnect from server
    def close(self):
        self.db.close()


    # End of class DBHelper
    pass

