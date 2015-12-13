#-*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import time
import subprocess



############################################
# Python starts here
############################################

# Start main loop
if __name__ == '__main__':

    while True:
        tempstr = subprocess.check_output('./hp.sh start', shell=True)
        time.sleep(60)

print 'HomePy process watcher died... '
