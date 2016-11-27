#!/bin/bash
CURRENT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
SOURCE_DIR="${CURRENT_DIR}/../../"
META=$(echo "python ${CURRENT_DIR}/../meta.py --file ${SOURCE_DIR}/build/package.json --query")

INIT_PRESENTS=0
if [ "$(${META} template)" == 'supervisor' ]; then
    INIT_PRESENTS=1
fi
if [ "$(${META} initScripts)" != ''  ]; then
    INIT_PRESENTS=1
fi

source ${CURRENT_DIR}/../common.sh

NAME=$(${META} name)
VERSION=$(${META} version)
VERSIONSUFFIX=""
RELEASE=$(date +%s)
SUMMARY=$(${META} description)
REQUIRES=$(${META} yumDependencies)
BUILD_REQUIRES="$(${META} yumBuildDependencies) python-argparse"
VIRTUALENV=$(${META} virtualenv)
COMMAND=$(${META} command)
INSTALL_BUILD_REQUIRES=1

[[ $VIRTUALENV == '' ]] && VIRTUALENV=$(which virtualenv)
[[ $COMMAND == '' ]] && COMMAND="exit 0"

SPECFILE=$(${META} specfile)
[[ $SPECFILE == '' ]] && SPECFILE="${CURRENT_DIR}/python.spec"

function opts {
        TEMP=`getopt -o c:s:v:b:f:h --long command:,supervisor:,virtualenv:,build:,versionsuffix:,help,disable-build-requires -- "$@"`
        eval set -- "$TEMP"
        while true; do
            case "$1" in
                -c|--command) COMMAND=$2; shift 2 ;;
                -h|--help) echo 'help under constuction' ; shift 1;;
                -b|--build) RELEASE=$2; shift 2 ;;
                -f|--versionsuffix) VERSIONSUFFIX=$2; shift 2 ;;
                -v|--virtualenv) VIRTUALENV=$2; shift 2 ;;
                --disable-build-requires) INSTALL_BUILD_REQUIRES=0; shift 1;;
                --) shift ; break ;;
                *) echo "Internal parsing error!: $1" ; exit 1 ;;
            esac
        done
}

opts "$@"

echo
echo
echo "Building ${NAME} rpm, version ${VERSION}, release ${RELEASE}"
echo "Requires: ${REQUIRES}"
echo "Build requires: ${BUILD_REQUIRES}"
echo "Virtualenv: ${VIRTUALENV}"
echo

if [ $INSTALL_BUILD_REQUIRES -eq 1 ]; then
    yuminstall ${BUILD_REQUIRES}
fi

rpmbuild -bb ${SPECFILE} \
                           --define "name ${NAME}" \
                           --define "version ${VERSION}${VERSIONSUFFIX}" \
                           --define "release ${RELEASE}" \
                           --define "source ${SOURCE_DIR}" \
                           --define "summary ${SUMMARY}" \
                           --define "requires ${REQUIRES}" \
                           --define "buildrequires ${BUILD_REQUIRES}" \
                           --define "command ${COMMAND}" \
                           --define "virtualenv ${VIRTUALENV}" \
                           --define "meta ${META}" \
                           --define "$([ ${INIT_PRESENTS} -eq 1 ] && echo 'initPresents' || echo 'initAbsent' ) 1"