#!/usr/bin/env bash

### BEGIN INIT INFO
# Provides:          nginx
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts the nginx web server
# Description:       starts nginx using start-stop-daemon
### END INIT INFO

SCRIPT=$(readlink -f $0)
SCRIPT_PATH=`dirname ${SCRIPT}`
PATH=/opt/nginx/sbin:/sbin:/bin:/usr/sbin:/usr/bin

DAEMON=`command -v nginx`
NAME=${SCRIPT_PATH}/nginx
DESC="Production DB Service"

DAEMON_OPTS="-q -c $SCRIPT_PATH/nginx.conf -p $SCRIPT_PATH "

command -v nginx > /dev/null 2>&1 || { echo >&2 "no nginx available"; exit 1; }

# Include nginx defaults if available
if [[ -f /etc/default/nginx ]] ; then
    . /etc/default/nginx
fi

set -e

case "$1" in
  start)
    echo -n "Starting $DESC: "
    start-stop-daemon --start --quiet --chdir `dirname ${SCRIPT_PATH}` --pidfile ${NAME}.pid --exec ${DAEMON} -- ${DAEMON_OPTS}
    echo "$NAME."
    ;;
  stop)
    echo -n "Stopping $DESC: "
    start-stop-daemon --stop --quiet --pidfile ${NAME}.pid --exec ${DAEMON} -- ${DAEMON_OPTS}
    echo "$NAME."
    ;;
  restart|force-reload)
    echo -n "Restarting $DESC: "
    start-stop-daemon --stop --quiet --pidfile ${NAME}.pid --exec ${DAEMON} -- ${DAEMON_OPTS}
    sleep 1
    start-stop-daemon --start --quiet --chdir `dirname ${SCRIPT_PATH}` --pidfile ${NAME}.pid --exec ${DAEMON} -- ${DAEMON_OPTS}
    echo "$NAME."
    ;;
  reload)
    echo -n "Reloading $DESC configuration: "
    start-stop-daemon --stop --signal HUP --quiet --pidfile ${NAME}.pid --exec ${DAEMON} -- ${DAEMON_OPTS}
    echo "$NAME."
    ;;
  *)
    #N=/etc/init.d/$NAME
    echo "Usage: $0 {start|stop|restart|reload|force-reload}" >&2
    exit 1
    ;;
esac

exit 0