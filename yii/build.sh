#!/bin/bash
CURRENT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
SOURCE_DIR="${CURRENT_DIR}/../../"
META="python ${CURRENT_DIR}/../meta.py --file ${CURRENT_DIR}/../../package.json --query"

NAME=$(${META} name)
SUMMARY=$(${META} name)
VERSION=$(${META} version)
RELEASE=$(date +%s)
REQUIRES=$(${META} yumDependencies)
BUILDREQUIRES="$(${META} yumBuildDependencies) python-argparse"
META=$(echo ${META})

COMMAND=$(${META} command)
[[ ${COMMAND} == '' ]] && COMMAND="exit 0"

function opts {
        TEMP=`getopt -o b:c:h --long build:,command:,help -- "$@"`
        eval set -- "${TEMP}"
        while true; do
            case "$1" in
                -c|--command) COMMAND=$2; shift 2 ;;
                -b|--build) RELEASE=$2; shift 2 ;;
                -h|--help) echo 'help under constuction' ; shift 1;;
                --) shift ; break ;;
                *) echo "Internal parsing error!: $1" ; exit 1 ;;
            esac
        done
}
opts "$@"

cat ${CURRENT_DIR}/../logo.txt

echo
echo
echo "Building $NAME rpm, version $VERSION, release $RELEASE"
echo "Requires: $REQUIRES"
echo "Build requires: $BUILDREQUIRES"
echo

yum install -y $BUILDREQUIRES
rpmbuild -bb ${CURRENT_DIR}/yii.spec \
                   --define "name $NAME" \
                   --define "version $VERSION" \
                   --define "release $RELEASE" \
                   --define "source $SOURCE_DIR" \
                   --define "summary $SUMMARY" \
                   --define "requires $REQUIRES" \
                   --define "buildrequires $BUILDREQUIRES" \
                   --define "meta $META" \
                   --define "command $COMMAND"
