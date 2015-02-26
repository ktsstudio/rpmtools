#!/bin/sh
name="PROJECT_NAME"

# gunicorn startup script
#
# chkconfig: - 85 15
# processname: $prog
# config: /etc/sysconfig/$prog
# pidfile: /var/run/$prog.pid
# description: $prog

# Setting `prog` here allows you to symlink this init script, making it easy to run multiple processes on the system.
prog="$(basename $0)"

# Source function library.
. /etc/rc.d/init.d/functions

# Also look at sysconfig; this is where environmental variables should be set on RHEL systems.
[ -f "/etc/sysconfig/$prog" ] && . /etc/sysconfig/$prog

pidfile="/var/run/${prog}.pid"
lockfile="/var/lock/subsys/${prog}"

RETVAL=0

start() {
    echo -n $"Starting $prog: "
    source /opt/${name}/env/bin/activate
    cd /opt/${name}/src/
    gunicorn -c /etc/${name}/gunicorn.conf -p ${pidfile} WSGI_APPLICATION.wsgi:application
    deactivate
    RETVAL=$?
    [ $RETVAL = 0 ] && { touch ${lockfile}; success; }
    echo
    return $RETVAL
}

stop() {
	echo -n $"Stopping $prog: "
	killproc -p ${pidfile} ${prog}
	RETVAL=$?
	echo
	[ $RETVAL = 0 ] && rm -f ${lockfile} ${pidfile}
}

rh_status() {
	status -p ${pidfile} ${prog}
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
