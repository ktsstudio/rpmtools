#!/bin/bash
CURRENT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
SOURCE_DIR=$(echo "${CURRENT_DIR}/../..")

source ${CURRENT_DIR}/../common.sh

NAME=""
NAMESUFFIX=""
GOPACKAGE=""
VERSION=""
VERSIONSUFFIX=""
RELEASE=$(date +%s)
SUMMARY=""
REQUIRES=""
BUILD_REQUIRES=""
INSTALL_BUILD_REQUIRES=1
AFTER_INSTALL_CMD=""
PACKAGEJSON="build/package.json"
if [ -z $GOPATH ]; then
    export GOPATH="/opt/go"
fi

function opts {
        TEMP=`getopt -o b:h --long packagejson:,build:,versionsuffix:,namesuffix:,help,disable-build-requires -- "$@"`
        eval set -- "$TEMP"
        while true; do
            case "$1" in
                -h|--help) echo 'help under constuction' ; shift 1;;
                -b|--build) RELEASE=$2; shift 2 ;;
                --versionsuffix) VERSIONSUFFIX=$2; shift 2 ;;
                --namesuffix) NAMESUFFIX=$2; shift 2 ;;
                --disable-build-requires) INSTALL_BUILD_REQUIRES=0; shift 1;;
                --packagejson) PACKAGEJSON=$2; shift 2 ;;
                --) shift ; break ;;
                *) echo "Internal parsing error!: $1" ; exit 1 ;;
            esac
        done
}
opts "$@"

if [ ! -f "${SOURCE_DIR}/${PACKAGEJSON}" ]; then
    echo "package.json file not found in ${SOURCE_DIR}/${PACKAGEJSON}"
    exit 1
fi
echo "Using package.json file: ${SOURCE_DIR}/${PACKAGEJSON}"

META=$(echo "python ${CURRENT_DIR}/../meta.py --file ${SOURCE_DIR}/${PACKAGEJSON} --query")

NAME="$(${META} name)"
GOPACKAGE=$(${META} gopackage)
VERSION=$(${META} version)
SUMMARY=$(${META} description)
REQUIRES=$(${META} yumDependencies)
BUILD_REQUIRES="$(${META} yumBuildDependencies) python-argparse golang rpm-build redhat-rpm-config"
AFTER_INSTALL_CMD=$(${META} afterInstallCmd)
USE_SRC=$(${META} srcRPM)

[[ $USE_SRC == '' ]] && USE_SRC="true"

INIT_PRESENTS=0
if [[ "$(${META} template)" != '' || "$(${META} initScripts)" != '' ]]; then
    INIT_PRESENTS=1
fi

[[ ${AFTER_INSTALL_CMD} == '' ]] && AFTER_INSTALL_CMD="exit 0"

SPECFILE=$(${META} specfile)
SPECFILE_SRC=$(${META} specfile_src)
[[ $SPECFILE == '' ]] && SPECFILE="${CURRENT_DIR}/golang.spec"
[[ $SPECFILE_SRC == '' ]] && SPECFILE_SRC="${CURRENT_DIR}/golang-src.spec"

echo
echo
echo "Building ${NAME}${NAMESUFFIX} rpm, go package ${GOPACKAGE}, version ${VERSION}, release ${RELEASE}"
echo "Requires: '${REQUIRES}'"
echo "Build requires: ${BUILD_REQUIRES}"
echo

if [ ${INSTALL_BUILD_REQUIRES} -eq 1 ]; then
    yuminstall ${BUILD_REQUIRES}
fi

rpmbuild -bb ${SPECFILE} \
                           --define "name ${NAME}${NAMESUFFIX}" \
                           --define "name_no_suffix ${NAME}" \
                           --define "gopackage ${GOPACKAGE}" \
                           --define "version ${VERSION}${VERSIONSUFFIX}" \
                           --define "release ${RELEASE}" \
                           --define "source ${SOURCE_DIR}" \
                           --define "summary ${SUMMARY}" \
                           --define "requires $([[ ${REQUIRES} == '' ]] && echo 'none' || echo ${REQUIRES} )" \
                           --define "buildrequires ${BUILD_REQUIRES}" \
                           --define "meta ${META}" \
                           --define "$([ ${INIT_PRESENTS} -eq 1 ] && echo 'initPresents' || echo 'initAbsent' ) 1" \
                           --define "afterInstallCmd ${AFTER_INSTALL_CMD}" \
                           --define "gopath ${GOPATH}" || exit 1
if [[ "$(${META} srcRPM)" == 'true' ]]; then
    echo "Building src RPM"
    rpmbuild -bb ${SPECFILE_SRC} \
                           --define "name ${NAME}${NAMESUFFIX}" \
                           --define "name_no_suffix ${NAME}" \
                           --define "gopackage ${GOPACKAGE}" \
                           --define "version ${VERSION}${VERSIONSUFFIX}" \
                           --define "release ${RELEASE}" \
                           --define "source ${SOURCE_DIR}" \
                           --define "summary ${SUMMARY}" \
                           --define "requires $([ ${REQUIRES} == '' ] && echo 'none' || echo ${REQUIRES} )" \
                           --define "buildrequires ${BUILD_REQUIRES}" \
                           --define "meta ${META}" \
                           --define "$([ ${INIT_PRESENTS} -eq 1 ] && echo 'initPresents' || echo 'initAbsent' ) 1" \
                           --define "afterInstallCmd ${AFTER_INSTALL_CMD}" \
                           --define "gopath ${GOPATH}"
fi

