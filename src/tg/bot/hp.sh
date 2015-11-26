#!/bin/bash
 
HPPATH="/home/pi/tg/bot"
HPBIN_PATH="/home/pi/tg/bot"
HPBIN_NAME="python home.py"
HPBIN_CHECK="python"
 
 
function ProcChk()
{
    local ProcFile="$1"
    local ProcName="$2"
    PID=`/bin/ps -e -u 0 | /bin/grep -w $ProcFile | /usr/bin/awk '{print $1}'`
    if [ "$PID" ] ;  then
        printf "%16s : Running\n" "$ProcName";
    else
        printf "%16s : Stopped\n" "$ProcName";
    fi;
}
 
case "$1" in
start)
    echo "Starting HomePy Daemon..."
    cd $HPPATH
    PID=`/bin/ps -e -u 0 | /bin/grep -w python | awk '{print $1}'`
 
    if [ $PID ]; then
        echo "HomePy Already Running"
        # exit 1
    else
        export PYTHONPATH="$HOME/lib/python2.7/site-packages/:$PYTHONPATH"
        $HPBIN_NAME &
        ProcChk "$HPBIN_CHECK" "HomePy Daemon"
    fi
    ;;
stop)
    echo "HomePy safe stop Trying"
    `echo "safe_quit" | nc localhost 4500`
 
    PID=`/bin/ps -e -u 0 | /bin/grep -w python | awk '{print $1}'`
 
    if [ -z $PID ]; then
        echo "HomePy Already Stop"
        # exit 1
    else
        kill -9 $PID
    fi
 
    sleep 1
    ProcChk "$HPBIN_CHECK" "HomePy Daemon"
    ;;
chk)
    ProcChk "$HPBIN_CHECK" "HomePy Daemon"
    ;;
*)
    echo "Usage : `basename $0` [ start | stop | chk ]"
    ;;
esac
