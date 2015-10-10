#!/usr/bin/env bash

function log {
    echo `date +%Y-%m-%d:%H:%M:%S` $1
}

SCRIPT_PATH=$(readlink ${BASH_SOURCE[0]})
if [ -z "$SCRIPT_PATH" ]
then
    SCRIPT_PATH=${BASH_SOURCE[0]}
fi

CURRENT_DIR=$(cd "$( dirname "$SCRIPT_PATH" )" && pwd)
NAME=$(basename "$( dirname "$CURRENT_DIR" )")
SCRAPY=${CURRENT_DIR}/../env/bin/scrapy
MODULE=$1

if [ -z "$1" ];
then
    echo 'First arg must be name of project' && exit 1
fi

export PYTHONPATH=${CURRENT_DIR}
export SCRAPY_SETTINGS_MODULE=${1}.settings

count=10
while [ -f "/var/run/${NAME}/pause.lock" ]
do
    log "Scrapy pause. Wait ${count} seconds..."
    sleep ${count}
    if [ ${count} -lt 60 ];
    then
        count=$((count+10))
    fi
done

log "Scrapy start"
SPIDERS=$(${SCRAPY} list)
log "Scrapy list: ${SPIDERS}"
for SPIDER in $SPIDERS
do
    log "Scrapy start crawl: ${SPIDER}"
    touch /var/run/${NAME}/scrapy.lock
    ${SCRAPY} crawl ${SPIDER}
    log "Scrapy stop crawl: ${SPIDER}"
    rm -rf /var/run/${NAME}/scrapy.lock
done
log "Scrapy end"

return 0