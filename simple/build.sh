#!/bin/bash
CURRENT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
SOURCE_DIR="${CURRENT_DIR}/../.."
META=$(echo "python ${CURRENT_DIR}/../meta.py --file ${CURRENT_DIR}/../../package.json --query")

source ${CURRENT_DIR}/../common.sh

COMMAND="exit 0"
PUBLIC_DIR_NAME="public"
NAME=$(${META} name)
VERSION_SUFFIX=""
SUMMARY=$(${META} name)
VERSION=$(${META} version)
RELEASE=$(date +%s)

GRUNTTASK=$(${META} grunttask)
[[ $GRUNTTASK == '' ]] && GRUNTTASK="default"


function opts {
        TEMP=`getopt -o g:s:b:h:c:p --long grunttask:,versionsuffix:,build:,command:,public:,help -- "$@"`
        eval set -- "$TEMP"
        while true; do
            case "$1" in
                -b|--build) RELEASE=$2; shift 2 ;;
                -s|--versionsuffix) VERSION_SUFFIX=$2; shift 2 ;;
                -g|--grunttask) GRUNTTASK=$2; shift 2 ;;
                -c|--command) COMMAND=$2; shift 2 ;;
                -p|--public) PUBLIC_DIR_NAME=$2; shift 2 ;;
                -h|--help) echo 'help under constuction' ; shift 1;;
                --) shift ; break ;;
                *) echo "Internal parsing error!: $1" ; exit 1 ;;
            esac
        done
}
opts "$@"
export FULLVERSION="${VERSION}-${RELEASE}"

cat ${CURRENT_DIR}/../logo.txt

echo
echo
echo "Building $NAME rpm, version $VERSION, release $RELEASE"
echo "Requires: $REQUIRES"
echo "Public dirname: $PUBLIC_DIR_NAME"
echo

rpmbuild -bb ${CURRENT_DIR}/simple.spec \
                   --define "name $NAME" \
                   --define "version $VERSION$VERSION_SUFFIX" \
                   --define "release $RELEASE" \
                   --define "source ${SOURCE_DIR}" \
                   --define "summary $SUMMARY" \
                   --define "meta ${META}" \
                   --define "grunttask ${GRUNTTASK}" \
                   --define "command ${COMMAND}" \
                   --define "public ${PUBLIC_DIR_NAME}"