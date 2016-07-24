#!/bin/sh
name="$(basename $0)"
supervisor_path="/opt/supervisor/bin/"
# chkconfig: - 85 15
# processname: $prog
# config: /etc/$prog/$prog.conf
# pidfile: /var/run/$prog.pid
# description: $prog

. /etc/rc.d/init.d/functions

[ -f "/etc/sysconfig/${name}" ] && . /etc/sysconfig/${name}

RETVAL=0
pidfile="/var/run/${name}/supervisord.pid"

status() {
    ${supervisor_path}/supervisorctl --configuration=/etc/${name}/supervisord.conf status
}

start() {
    echo -n "Starting ${name}: "

    if [ -f "/var/run/${name}/supervisord.pid" ]
    then
        echo "${name} seems to be running"
    else
        ${supervisor_path}/supervisord --configuration=/etc/${name}/supervisord.conf
    fi
    RETVAL=$?
    echo
    [ $RETVAL = 0 ] && { success; }
    echo
    return $RETVAL
}

stop() {
    echo -n "Stopping $name: "
    ${supervisor_path}/supervisorctl --configuration=/etc/${name}/supervisord.conf stop ${name} all
    ${supervisor_path}/supervisorctl --configuration=/etc/${name}/supervisord.conf shutdown
    [ -f "/var/run/${name}/supervisord.pid" ] && rm -f `cat /var/run/${name}/supervisord.pid`
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