#!/bin/sh
name="PROJECT_NAME"

# celerycam startup script
#
# chkconfig: - 85 15
# processname: $prog
# config: /etc/sysconfig/$prog
# pidfile: /var/run/${name}/$prog.pid
# description: $prog

# Setting `prog` here allows you to symlink this init script, making it easy to run multiple processes on the system.
prog="$(basename $0)"

# Source function library.
. /etc/rc.d/init.d/functions

# Also look at sysconfig; this is where environmental variables should be set on RHEL systems.
[ -f "/etc/sysconfig/$prog" ] && . /etc/sysconfig/$prog

pidfile="/var/run/${name}/${prog}.pid"
lockfile="/var/lock/subsys/${prog}"

bin="/usr/bin/${name}"
opts="celerycam --detach --pidfile=${pidfile} --uid=$(id -u ${name}) --gid=$(id -g ${name}) --workdir=/opt/${name}/src"

RETVAL=0


start() {
	echo -n $"Starting $prog: "
	${bin} ${opts}
	RETVAL=$?
	[ $RETVAL = 0 ] && { touch ${lockfile}; success; }
    echo
	return $RETVAL
}

stop() {
	echo -n $"Stopping $prog: "
	killproc -p ${pidfile} ${name}
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
    restart_if_running)
        if [ -f ${pidfile} ]; then
            stop
            start
        else
            echo "not running"
        fi
	;;
	restart)
		stop
		start
	;;
	*)
		echo $"Usage: $0 {start|stop|restart|status|restart_if_running}"
		RETVAL=2
esac

exit $RETVAL
