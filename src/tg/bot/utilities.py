#-*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def parse_comp_str(strcomp):
    if strcomp.strip() == '':
        return 0, 0, 0

    # find field name
    datanum = 0
    if strcomp.find('data1') > -1:
        datanum = 1
    elif strcomp.find('data2') > -1:
        datanum = 2
    elif strcomp.find('data3') > -1:
        datanum = 3
    elif strcomp.find('data4') > -1:
        datanum = 4
    if datanum < 1:
        # at lease one data field is needed
        return 0, 0, 0
    print 'parsed data number'
    # find comparison operator
    compcode = 0
    targetnum = 0
    if strcomp.find('>=') > -1:
        compcode = 2
        param = strcomp[strcomp.find('>=') + 2:]
        if not param.isdigit():
            return 0, 0, 0
        targetnum = int(param)
    elif strcomp.find('==') > -1:
        compcode = 3
        param = strcomp[strcomp.find('==') + 2:]
        print 'splitted = ' + param
        if not param.isdigit():
            return 0, 0, 0
        targetnum = int(param)
    elif strcomp.find('<=') > -1:
        compcode = 4
        param = strcomp[strcomp.find('<=') + 2:]
        if not param.isdigit():
            return 0, 0, 0
        targetnum = int(param)
    elif strcomp.find('!=') > -1:
        compcode = 6
        param = strcomp[strcomp.find('!=') + 2:]
        if not param.isdigit():
            return 0, 0, 0
        targetnum = int(param)
    elif strcomp.find('>') > -1:
        compcode = 1
        param = strcomp[strcomp.find('>') + 1:]
        if not param.isdigit():
            return 0, 0, 0
        targetnum = int(param)
    elif strcomp.find('<') > -1:
        compcode = 5
        param = strcomp[strcomp.find('<') + 1:]
        if not param.isdigit():
            return 0, 0, 0
        targetnum = int(param)
        #strcomp.replace('<', ' ')
        #param = strcomp.split()
        #print 'comp oper split into %d' % len(param)
        #print param[0]
        #if len(param) < 2:
        #    return 0, 0, 0
        #print param[1]
        #if not param[1].isdigit():
        #    return 0, 0, 0
        #targetnum = int(param[1])

    #print 'parsed result: %d, %d, %d' % (datanum, compcode, targetnum)

    if compcode < 1:
        return 0, 0, 0

    return datanum, compcode, targetnum


def get_comp_operator(type):
    if type == 1:
        return '>'
    elif type == 2:
        return '>='
    elif type == 3:
        return '=='
    elif type == 4:
        return '<='
    elif type == 5:
        return '<'
    elif type == 6:
        return '!='



