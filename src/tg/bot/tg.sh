#!/bin/bash

TGPATH="/home/pi/tg"
TGBIN_PATH="/home/pi/tg/bin"
TGBIN_NAME="telegram-cli"
TGBOT_PATH="/home/pi/tg/bot/basicbot.lua"
TGLOG_PATH="/var/log/telegram-cli.log"
TGLISTEN_PORT=8888


function ProcChk()
{
    local ProcFile="$1"
    local ProcName="$2"
    PID=`/bin/ps -e -u 0 | /bin/grep -w $ProcFile | /usr/bin/awk '{print $1}'`
    if [ "$PID" ] ;  then
        printf "%16s : [36m[1mRunning[0m\n" "$ProcName";
    else
        printf "%16s : [31m[1mStopped[0m\n" "$ProcName";
    fi;
}

case "$1" in
start)
    echo "[36m[1mStarting Telegram CLI Daemon...[0m"
    cd $TGPATH
    PID=`/bin/ps -e -u 0 | /bin/grep -w telegram-cli | awk '{print $1}'`

    if [ $PID ]; then
        echo "Telegram CLI Already Running"
        # exit 1
    else
        $TGBIN_PATH/$TGBIN_NAME &
        ProcChk "$TGBIN_NAME" "Telegram CLI Daemon"
    fi
    ;;
stop)
    echo "Telegram CLI safe stop Trying"
    `echo "safe_quit" | nc localhost 4500`

    PID=`/bin/ps -e -u 0 | /bin/grep -w telegram-cli | awk '{print $1}'`

    if [ -z $PID ]; then
        echo "Telegram CLI Already Stop"
        # exit 1
    else
        kill -9 $PID
    fi

    sleep 1
    ProcChk "$TGBIN_NAME" "Telegram CLI Daemon"
    ;;
chk)
    ProcChk "$TGBIN_NAME" "Telegram CLI Daemon"
    ;;
*)
    echo "Usage : `basename $0` [ start | stop | chk ]"
    ;;
esac
