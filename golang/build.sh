#!/bin/bash
CURRENT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
SOURCE_DIR="${CURRENT_DIR}/../../"

source ${CURRENT_DIR}/../common.sh

PACKAGEJSON=$(get_packagejson ${SOURCE_DIR} "$@")
echo
if [ -z "${PACKAGEJSON}" ]; then
    echo "package.json file not found"
    exit 1
fi
echo "Using package.json file: ${SOURCE_DIR}${PACKAGEJSON}"

META=$(echo "python ${CURRENT_DIR}/../meta.py --file ${SOURCE_DIR}${PACKAGEJSON} --query")

INIT_PRESENTS=0
if [[ "$(${META} template)" != '' || "$(${META} initScripts)" != '' ]]; then
    INIT_PRESENTS=1
fi

NAME=$(${META} name)
GOPACKAGE=$(${META} gopackage)
VERSION=$(${META} version)
VERSIONSUFFIX=""
RELEASE=$(date +%s)
SUMMARY=$(${META} description)
REQUIRES=$(${META} yumDependencies)
BUILD_REQUIRES="$(${META} yumBuildDependencies) python-argparse"
INSTALL_BUILD_REQUIRES=1
AFTER_INSTALL_CMD=$(${META} afterInstallCmd)
export GOPATH="/opt/go"

[[ ${AFTER_INSTALL_CMD} == '' ]] && AFTER_INSTALL_CMD="exit 0"

SPECFILE=$(${META} specfile)
[[ $SPECFILE == '' ]] && SPECFILE="${CURRENT_DIR}/golang.spec"


function opts {
        TEMP=`getopt -o b:h --long build:,name:,versionsuffix:,namesuffix:,packagejson:,help,disable-build-requires -- "$@"`
        eval set -- "$TEMP"
        while true; do
            case "$1" in
                -h|--help) echo 'help under constuction' ; shift 1;;
                -b|--build) RELEASE=$2; shift 2 ;;
                --versionsuffix) VERSIONSUFFIX=$2; shift 2 ;;
                --name) NAME=$2; shift 2 ;;
                --namesuffix) NAMESUFFIX="$2"; shift 2 ;;
                --disable-build-requires) INSTALL_BUILD_REQUIRES=0; shift 1;;
                --packagejson) shift ; break ;;
                --) shift ; break ;;
                *) echo "Internal parsing error!: $1" ; exit 1 ;;
            esac
        done
}
opts "$@"


echo
echo
echo "Building ${NAME} rpm, go package ${GOPACKAGE}, version ${VERSION}, release ${RELEASE}"
echo "Requires: ${REQUIRES}"
echo "Build requires: ${BUILD_REQUIRES}"
echo

if [ ${INSTALL_BUILD_REQUIRES} -eq 1 ]; then
    yuminstall ${BUILD_REQUIRES}
fi

rpmbuild -bb ${SPECFILE} \
                           --define "name ${NAME}" \
                           --define "gopackage ${GOPACKAGE}" \
                           --define "version ${VERSION}${VERSIONSUFFIX}" \
                           --define "release ${RELEASE}" \
                           --define "source ${SOURCE_DIR}" \
                           --define "summary ${SUMMARY}" \
                           --define "requires ${REQUIRES}" \
                           --define "buildrequires ${BUILD_REQUIRES}" \
                           --define "meta ${META}" \
                           --define "$([ ${INIT_PRESENTS} -eq 1 ] && echo 'initPresents' || echo 'initAbsent' ) 1" \
                           --define "afterInstallCmd ${AFTER_INSTALL_CMD}" \
                           --define "gopath ${GOPATH}"
