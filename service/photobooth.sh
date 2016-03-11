#!/bin/sh
#/etc/init.d/photobooth.sh
case "$1" in
  start)
    echo "Starting Photobooth"
    # run application you want to start
    python /home/pi/Photobooth/counter.py >/dev/null 2>&1 &
    ;;
  stop)
    echo "Stopping Photobooth"
    # kill application you want to stop
    killall python
    ;;
  *)
    echo "Usage: /etc/init.d/photobooth {start|stop}"
    exit 1
    ;;
esac
exit 0