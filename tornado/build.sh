#!/bin/bash
CURRENT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
SOURCE_DIR="${CURRENT_DIR}/../../"
META="python ${CURRENT_DIR}/../meta.py --file ${SOURCE_DIR}/build/package.json --query"

NAME=$(${META} name)
VERSION=$(${META} version)
VERSIONSUFFIX=""
RELEASE=$(date +%s)
SUMMARY=$(${META} description)
REQUIRES=$(${META} yumDependencies)
BUILDREQUIRES="$(${META} yumBuildDependencies) python-argparse"
VIRTUALENV=$(${META} virtualenv)
COMMAND=$(${META} command)
META=$(echo ${META})

[[ $VIRTUALENV == '' ]] && VIRTUALENV=$(which virtualenv)
[[ $COMMAND == '' ]] && COMMAND="exit 0"

function opts {
        TEMP=`getopt -o c:s:v:b:f:h --long command:,supervisor:,virtualenv:,build:,versionsuffix:,help -- "$@"`
        eval set -- "$TEMP"
        while true; do
            case "$1" in
                -c|--command) COMMAND=$2; shift 2 ;;
                -h|--help) echo 'help under constuction' ; shift 1;;
                -b|--build) RELEASE=$2; shift 2 ;;
                -f|--versionsuffix) VERSIONSUFFIX=$2; shift 2 ;;
                -v|--virtualenv) VIRTUALENV=$2; shift 2 ;;
                --) shift ; break ;;
                *) echo "Internal parsing error!: $1" ; exit 1 ;;
            esac
        done
}
opts "$@"

cat ${CURRENT_DIR}/../logo.txt

echo
echo
echo "Building ${NAME} rpm, version ${VERSION}, release ${RELEASE}"
echo "Requires: ${REQUIRES}"
echo "Build requires: ${BUILDREQUIRES}"
echo "Virtualenv: ${VIRTUALENV}"
echo

yum install -y $BUILDREQUIRES || true
rpmbuild -bb ${CURRENT_DIR}/tornado.spec \
                   --define "name ${NAME}" \
                   --define "version ${VERSION}${VERSIONSUFFIX}" \
                   --define "release ${RELEASE}" \
                   --define "source ${SOURCE_DIR}" \
                   --define "summary ${SUMMARY}" \
                   --define "requires ${REQUIRES}" \
                   --define "buildrequires ${BUILDREQUIRES}" \
                   --define "command ${COMMAND}" \
                   --define "virtualenv ${VIRTUALENV}" \
                   --define "meta ${META}"
