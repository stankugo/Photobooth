#!/bin/sh
#/etc/init.d/photobooth.sh
case "$1" in
  start)
    echo "Starting Photobooth"
    # run application you want to start
    now=`date +'%H'`

    # check if it's during the day
    if [ $now -gt 6 ] && [ $now -lt 23 ]
    then
        echo 'It is about time!';
        timestamp=`date '+%Y%m%d-%H%M%S'`;
        python /home/pi/Photobooth/photo.py > /var/log/photobooth-$timestamp.log 2>&1 &
    else
        echo 'Not yet.';
    fi
    ;;
  stop)
    echo "Stopping Photobooth"
    # kill application you want to stop
    killall python
    killall pngview
    killall spriteview
    ;;
  *)
    echo "Usage: /etc/init.d/photobooth {start|stop}"
    exit 1
    ;;
esac
exit 0