#!/bin/sh
name="#NAME#"
service="${name}-celeryd"

# celeryd startup script
#
# chkconfig: - 85 15
# processname: $prog
# config: /etc/sysconfig/$prog
# pidfile: /var/run/${name}/$prog.pid
# description: $service

. /etc/rc.d/init.d/functions

[ -f "/etc/sysconfig/$service" ] && . /etc/sysconfig/$service

pidfile="/var/run/${name}/${service}.pid"
lockfile="/var/lock/subsys/${service}"

source /opt/${name}/env/bin/activate
bin="/usr/bin/${name}"
opts="multi start worker -A application -EB --pidfile=${pidfile} -c 5 -l INFO --logfile=/var/log/${name}/celeryd.log --uid=$(id -u ${name}) --gid=$(id -g ${name}) --workdir=/opt/${name}/src"

RETVAL=0

start() {
	echo -n $"Starting $service: "
	celery ${opts}
	RETVAL=$?
	[ $RETVAL = 0 ] && { touch ${lockfile}; success; }
        echo
	return ${RETVAL}
}

stop() {
	echo -n $"Stopping $service: "
	celery multi stopwait worker --pidfile=${pidfile}
	RETVAL=$?
	echo
	[ ${RETVAL} = 0 ] && rm -f ${lockfile} ${pidfile}
}

restart() {
    echo -n $"Restarting $service; "
    celery multi restart worker ${opts}
	RETVAL=$?
	return ${RETVAL}
}

rh_status() {
	status -p ${pidfile} ${service}
}

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
            restart
        else
            echo "not running"
        fi
	;;
	restart)
        restart
	;;
	*)
		echo $"Usage: $0 {start|stop|restart|status|restart_if_running}"
		RETVAL=2
esac

exit ${RETVAL}