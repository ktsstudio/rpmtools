#!/bin/sh
name="$(basename $0)"
#
# Note runlevel 2345, 86 is the Start order and 85 is the Stop order
#
# chkconfig: 2345 86 85
# description: Description of the Service
#
# Below is the source function library, leave it be
. /etc/init.d/functions

# result of whereis forever or whereis node
export PATH=$PATH:/opt/${name}/src/node_modules/bin:/opt/${name}/src/node_modules/.bin
export NODE_PATH=$NODE_PATH:/opt/${name}/src/node_modules
export NODE_CONFIG_DIR=/etc/${name}
export NODE_ENV=production
SCRIPT=/opt/${name}/src/bin/www

mkdir -p /var/run/${name}

start() {
        forever start -c "node --harmony" -a -l /var/log/${name}/forever.log -o /var/log/${name}/std.out -e /var/log/${name}/std.err --pidFile /var/run/${name}/${name}.pid  ${SCRIPT}
}

stop() {
        forever stop -c "node --harmony" -a -l /var/log/${name}/forever.log --pidFile /var/run/${name}/${name}.pid ${SCRIPT}
}

restart() {
        forever restart -c "node --harmony" -a -l /var/log/${name}/forever.log --pidFile /var/run/${name}/${name}.pid ${SCRIPT}
}

case "$1" in
        start)
                echo "Start service ${name}"
                start
                ;;
        stop)
                echo "Stop service ${name}"
                stop
                ;;
        restart)
                echo "Restart service ${name}"
                restart
                ;;
        *)
                echo "Usage: $0 {start|stop|restart}"
                exit 1
                ;;
esac