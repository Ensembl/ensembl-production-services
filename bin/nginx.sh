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
PATH=$PATH:/opt/nginx/sbin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin

DAEMON=`command -v nginx`
DESC="Production DB Service"

DAEMON_OPTS="-q -c $SCRIPT_PATH/nginx.conf -p $SCRIPT_PATH "
NAME="Run ${DAEMON} ${DAEMON_OPTS}"

command -v nginx > /dev/null 2>&1 || { echo >&2 "no nginx available"; exit 1; }

# Include nginx defaults if available
if [[ -f /etc/default/nginx ]] ; then
    . /etc/default/nginx
fi

set -e

case "$1" in
  start)
    echo -n "Starting $DESC: "
    ${DAEMON} ${DAEMON_OPTS}
    echo "$NAME."
    ;;
  stop)
    echo -n "Stopping $DESC: "
    if [[ -e $SCRIPT_PATH/nginx.pid ]]
    then
        ${DAEMON} ${DAEMON_OPTS} -s quit
    else
        echo "No process detected"
    fi
    ;;
  restart|force-reload|reload)
    echo -n "Restarting $DESC: "
    if [[ -e $SCRIPT_PATH/nginx.pid ]]
    then
        echo "Process detected - Reload gracefully"
        ${DAEMON} ${DAEMON_OPTS} -s reload
    else
        echo "No process detected - Start fresh"
        ${DAEMON} ${DAEMON_OPTS}
    fi
    echo "$NAME."
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|reload|force-reload}" >&2
    exit 1
    ;;
esac

exit 0