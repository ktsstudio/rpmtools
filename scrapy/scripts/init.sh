#!/bin/sh
prog="$(basename $0)"
# chkconfig: - 85 15
# processname: $prog
# config: /etc/$prog/$prog.conf
# pidfile: /var/run/$prog.pid
# description: $prog

. /etc/rc.d/init.d/functions

[ -f "/etc/sysconfig/${prog}" ] && . /etc/sysconfig/${prog}

RETVAL=0
pidfile="/var/run/${prog}/supervisord.pid"

status() {
    /opt/${prog}/env/bin/supervisorctl --configuration=/etc/${prog}/supervisord.conf status
}

start() {
    echo -n "Starting ${prog}: "

    if [ -f "/var/run/${prog}/supervisord.pid" ]
    then
        echo "${prog} seems to be running"
    else
        /opt/${prog}/env/bin/supervisord --configuration=/etc/${prog}/supervisord.conf
    fi
    RETVAL=$?
    echo
    [ $RETVAL = 0 ] && { success; }
    echo
    return $RETVAL
}

stop() {
    echo -n "Stopping $prog: "
    /opt/${prog}/env/bin/supervisorctl --configuration=/etc/${prog}/supervisord.conf stop ${prog} all
    /opt/${prog}/env/bin/supervisorctl --configuration=/etc/${prog}/supervisord.conf shutdown
    [ -f "/var/run/${prog}/supervisord.pid" ] && rm -f `cat /var/run/${prog}/supervisord.pid`
    RETVAL=$?
    [ $RETVAL = 0 ] && { success; }
    echo
    return $RETVAL
}

case "$1" in
    start)
        start
    ;;
    stop)
        stop
    ;;
    status)
        status
    ;;
    restart)
        stop
        start
    ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        RETVAL=2
esac

exit $RETVAL