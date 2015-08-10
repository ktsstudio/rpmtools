#!/usr/bin/env bash
CURRENT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
SCRAPY=${CURRENT_DIR}/../env/bin/scrapy
MODULE=$1

[ -z "$1" ] && echo 'First arg must be name of project' && exit 1

export PYTHONPATH=$CURRENT_DIR
export SCRAPY_SETTINGS_MODULE=${1}.settings

SPIDERS=$(${SCRAPY} list)
for SPIDER in $SPIDERS
do
    ${SCRAPY} crawl $SPIDER
done