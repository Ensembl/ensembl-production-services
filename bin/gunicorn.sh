#!/usr/bin/env bash

### BEGIN INIT INFO
# Provides:          nginx
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts the gunicorn processes
# Description:       starts gunicorn
### END INIT INFO

SCRIPT=$(readlink -f $0)
SCRIPT_PATH=`dirname ${SCRIPT}`
APP_PATH=`dirname ${SCRIPT_PATH}`
PATH=$PATH:$SCRIPT_PATH:$APP_PATH

DAEMON=`command -v gunicorn`

NAME=${SCRIPT_PATH}/gunicorn
DESC="Production DB Service"

DAEMON_OPTS="-c $SCRIPT_PATH/gunicorn.conf.py production_services.wsgi:application --daemon"

PYTHONPATH=${PYTHONPATH}:${SCRIPT_PATH}/../
export PYTHONPATH

command -v gunicorn > /dev/null 2>&1 || { echo >&2 "no gunicorn available"; exit 1; }

cd ${SCRIPT_PATH}/../

function init_django() {
    echo "Check Django Updates / Upgrades"
    python manage.py makemigrations ensembl_production
    python manage.py migrate ensembl_production
    python manage.py makemigrations
    python manage.py migrate
    python manage.py collectstatic --no-input
}

set -e

case "$1" in
  start)
    echo "Starting $DESC"
    init_django
    ${DAEMON} ${DAEMON_OPTS}
    echo "$NAME."
    ;;
  stop)
    echo -n "Stopping $DESC: "
    kill -9 `ps aux | grep gunicorn | grep ensembl_production_api | awk '{ print $2 }'`
    # start-stop-daemon --stop --quiet --pidfile ${NAME}.pid --exec ${DAEMON}  -- ${DAEMON_OPTS}
    echo "$NAME."
    ;;
  restart)
    echo -n "Restarting $DESC: "
    kill -9 `ps aux | grep gunicorn | grep ensembl_production_api | awk '{ print $2 }'`
    sleep 1
    ${DAEMON} ${DAEMON_OPTS}
    echo "$NAME."
    ;;
  *)
    #N=/etc/init.d/$NAME
    echo "Usage: $0 {start|stop|restart}" >&2
    exit 1
    ;;
esac

exit 0