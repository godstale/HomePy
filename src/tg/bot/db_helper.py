#-*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import time
import MySQLdb

import traceback


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
            #dummy = list()
            return []

    def add_device(self, device, update):
        if update > 0:
            # update row
            sql_query = "UPDATE devices SET name='"
            sql_query += device[13]
            sql_query += "', location='"
            sql_query += device[14]
            sql_query += "', updated="
            sql_query += str(device[15])
            sql_query += ", cmd1="
            sql_query += str(device[5])
            sql_query += ", cmd2="
            sql_query += str(device[7])
            sql_query += ", cmd3="
            sql_query += str(device[9])
            sql_query += ", cmd4="
            sql_query += str(device[11])
            sql_query += ", type1="
            sql_query += str(device[6])
            sql_query += ", type2="
            sql_query += str(device[8])
            sql_query += ", type3="
            sql_query += str(device[10])
            sql_query += ", type4="
            sql_query += str(device[12])
            sql_query += " WHERE category1="
            sql_query += str(device[1])
            sql_query += " AND category2="
            sql_query += str(device[2])
            sql_query += " AND deviceid="
            sql_query += str(device[3])
            sql_query += ";"
        else:
            sql_query = """INSERT INTO devices (category1, category2, deviceid,
                            name, location, updated,
                            cmd1, cmd2, cmd3, cmd4,
                            type1, type2, type3, type4)
                            VALUES ("""
            sql_query += str(device[1])  # category 1
            sql_query += ','
            sql_query += str(device[2])  # category 2
            sql_query += ','
            sql_query += str(device[3])  # device ID
            sql_query += ",'"
            sql_query += device[13]   # name
            sql_query += "','"
            sql_query += device[14]   # location
            sql_query += "',"
            sql_query += str(device[15])  # updated time
            sql_query += ','
            sql_query += str(device[5])  # cmd1
            sql_query += ','
            sql_query += str(device[7])  # cmd2
            sql_query += ','
            sql_query += str(device[9])  # cmd3
            sql_query += ','
            sql_query += str(device[11])  # cmd4
            sql_query += ','
            sql_query += str(device[6])  # type1
            sql_query += ','
            sql_query += str(device[8])  # type2
            sql_query += ','
            sql_query += str(device[10])  # type3
            sql_query += ','
            sql_query += str(device[12])  # type4
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
        sql_query += str(device[1])  # category 1
        sql_query += ','
        sql_query += str(device[2])  # category 2
        sql_query += ','
        sql_query += str(device[3])  # device ID
        sql_query += ','
        sql_query += str(device[5])  # int 1
        sql_query += ','
        sql_query += str(device[6])  # int 2
        sql_query += ','
        sql_query += str(device[7])  # int 3
        sql_query += ','
        sql_query += str(device[8])  # int 4
        sql_query += ','
        sql_query += str(device[9])  # float 1
        sql_query += ','
        sql_query += str(device[10])  # float 2
        sql_query += ','
        sql_query += str(device[15])  # updated time
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
        sql_query += str(noti[1])  # category 1
        sql_query += ','
        sql_query += str(noti[2])  # category 2
        sql_query += ','
        sql_query += str(noti[3])  # device ID
        sql_query += ','
        sql_query += str(noti[4])  # comp 1
        sql_query += ','
        sql_query += str(noti[5])  # comp 2
        sql_query += ','
        sql_query += str(noti[6])  # comp 3
        sql_query += ','
        sql_query += str(noti[7])  # comp 4
        sql_query += ','
        sql_query += str(noti[8])  # int 1
        sql_query += ','
        sql_query += str(noti[9])  # int 2
        sql_query += ','
        sql_query += str(noti[10])  # int 3
        sql_query += ','
        sql_query += str(noti[11])  # int 4
        sql_query += ','
        sql_query += str(noti[12])  # updated time
        sql_query += ',"'
        sql_query += str(noti[13])  # name
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
            print sql_query2
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
            print sql_query2
            self.cursor.execute(sql_query2)
            self.db.commit()
        except:
            print '    Cannot execute device delete all query!!!'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.db.rollback()
            return False
        return True

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


    # disconnect from server
    def close(self):
        self.db.close()


    # End of class DBHelper
    pass

