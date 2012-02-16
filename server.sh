#!/bin/bash
### BEGIN INIT INFO
# Provides:          mysite
# Required-Start:    $syslog $remote_fs $network
# Required-Stop:     $syslog $remote_fs $network
# Should-Start:      fam
# Should-Stop:       fam
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start fcgi server.
### END INIT INFO

NAME=grakon
PIDFILE=/var/run/$NAME.pid
SCRIPTNAME=/etc/init.d/$NAME
SOCKET=/home/serg/sites/grakon.sock
DIR="/home/serg/sites/grakon/"
ENV="/home/serg/env/grakon/bin/activate"

METHOD="threaded" # "prefork"

action=${1:-restart}

start() {
    cd ${DIR}
    source ${ENV}
    python manage.py runfcgi method=${METHOD} socket=${SOCKET} pidfile=${PIDFILE} && echo "fcgi started."
    chown nginx:nginx ${SOCKET}
}

stop() {
    if [ -e ${PIDFILE} ]
    then
        kill `cat ${PIDFILE}` && rm -f ${PIDFILE} &&  echo "fcgi stoped."
    fi
}

restart() {
    stop
    start
}

usage() {
echo "Arguments should be: start, stop, restart or None."
}

case ${action} in
    start   ) start   ;;
    stop    ) stop    ;;
    restart ) restart ;;
    *       ) usage   ;;
esac
