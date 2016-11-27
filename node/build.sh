#!/bin/bash
CURRENT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
SOURCE_DIR="${CURRENT_DIR}/../../"
META=$(echo "python ${CURRENT_DIR}/../meta.py --file ${SOURCE_DIR}/package.json --query")

source ${CURRENT_DIR}/../common.sh

NAME=$(${META} name)
VERSION=$(${META} version)
RELEASE=$(date +%s)
summary=$(${META} description)
REQUIRES=$(${META} yumDependencies)
BUILDREQUIRES="$(${META} yumBuildDependencies) python-argparse"

function opts {
        TEMP=`getopt -o b:h --long build:,help -- "$@"`
        eval set -- "${TEMP}"
        while true; do
            case "$1" in
                -h|--help) echo 'help under constuction' ; shift 1;;
                -b|--build) RELEASE=$2; shift 2 ;;
                --) shift ; break ;;
                *) echo "Internal parsing error!: $1" ; exit 1 ;;
            esac
        done
}

opts "$@"

echo
echo
echo "Building $NAME rpm, version $VERSION, release $RELEASE"
echo "Requires: $REQUIRES"
echo "Build requires: $BUILDREQUIRES"
echo

yuminstall ${BUILDREQUIRES}

rpmbuild -bb ${SPECFILE} \
                   --define "name $NAME" \
                   --define "version $VERSION" \
                   --define "release $RELEASE" \
                   --define "source ${SOURCE_DIR}" \
                   --define "summary $summary" \
                   --define "requires $REQUIRES" \
                   --define "buildrequires $BUILDREQUIRES" \
                   --define "meta $META"