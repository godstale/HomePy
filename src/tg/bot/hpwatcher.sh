#!/bin/bash
 
HPPATH="/home/pi/tg/bot"
HPBIN_PATH="/home/pi/tg/bot"
HPBIN_NAME="python hpwatcher.py"
HPBIN_CHECK="python"
HPBIN_CHECK2="hpwatcher.py"
 
function ProcChk()
{
    local ProcFile="$1"
    local ProcFile2="$2"
    local ProcName="$3"
    PID=`/bin/ps aux | /bin/grep -w $ProcFile | /bin/grep -w $ProcFile2 | /usr/bin/awk '{print $2}'`
    if [ "$PID" ] ;  then
        printf "%16s : Running\n" "$ProcName";
    else
        printf "%16s : Stopped\n" "$ProcName";
    fi;
}
 
case "$1" in
start)
    echo "Starting HomePy process watcher..."
    cd $HPPATH
    PID=`/bin/ps aux | /bin/grep -w $HPBIN_CHECK | /bin/grep -w $HPBIN_CHECK2 | /usr/bin/awk '{print $2}'`
 
    if [ $PID ]; then
        echo "HomePy process watcher is already running"
        # exit 1
    else
        export PYTHONPATH="$HOME/lib/python2.7/site-packages/:$PYTHONPATH"
        $HPBIN_NAME &
        ProcChk "$HPBIN_CHECK" "$HPBIN_CHECK2" "HomePy Daemon"
    fi
    ;;
stop)
    echo "HomePy process watcher safe stop Trying"
    `echo "safe_quit" | nc localhost 4500`
 
    PID=`/bin/ps aux | /bin/grep -w $HPBIN_CHECK | /bin/grep -w $HPBIN_CHECK2 | /usr/bin/awk '{print $2}'`
 
    if [ -z $PID ]; then
        echo "HomePy process watcher is already stopped"
        # exit 1
    else
        kill -9 $PID
    fi
 
    sleep 1
    ProcChk "$HPBIN_CHECK" "$HPBIN_CHECK2" "HomePy process watcher"
    ;;
chk)
    ProcChk "$HPBIN_CHECK" "$HPBIN_CHECK2" "HomePy process watcher"
    ;;
*)
    echo "Usage : `basename $0` [ start | stop | chk ]"
    ;;
esac
