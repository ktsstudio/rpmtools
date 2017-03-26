#!/bin/sh
name="#NAME#"
service="${name}-gunicorn"

# gunicorn startup script
#
# chkconfig: - 85 15
# processname: $prog
# config: /etc/sysconfig/$prog
# pidfile: /var/run/$prog.pid
# description: $service


. /etc/rc.d/init.d/functions

[ -f "/etc/sysconfig/$service" ] && . /etc/sysconfig/$service

pidfile="/var/run/${service}.pid"
lockfile="/var/lock/subsys/${service}"
export LANG=ru_RU.UTF-8
RETVAL=0

start() {
    echo -n $"Starting $service: "
    source /opt/${name}/env/bin/activate
    cd /opt/${name}/src/
    gunicorn -c /etc/${name}/gunicorn.conf -p ${pidfile} #WSGIPKG#.wsgi:application
    deactivate
    RETVAL=$?
    [ $RETVAL = 0 ] && { touch ${lockfile}; success; }
    echo
    return $RETVAL
}

stop() {
	echo -n $"Stopping $service: "
	killproc -p ${pidfile} ${service}
	RETVAL=$?
	echo
	[ $RETVAL = 0 ] && rm -f ${lockfile} ${pidfile}
}

rh_status() {
	status -p ${pidfile} ${service}
}

# See how we were called.
case "$1" in
	start)
		rh_status > /dev/null 2>&1 && exit 0
		start
	;;
	stop)
		stop
	;;
	status)
		rh_status
		RETVAL=$?
	;;
	restart)
		stop
		start
	;;
	*)
		echo $"Usage: $0 {start|stop|restart|status}"
		RETVAL=2
esac

exit $RETVAL
