#!/bin/bash
CURRENT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
SOURCE_DIR="${CURRENT_DIR}/../../"
META="python ${CURRENT_DIR}/../meta.py --file ${CURRENT_DIR}/../../package.json --query"

name=$(${META} name)
summary=$(${META} name)
version=$(${META} version)
release=$(date +%s)
requires=$(${META} yumDependencies)
buildrequires="$(${META} yumBuildDependencies) python-argparse"
meta=$(echo ${META})

function opts {
        TEMP=`getopt -o b:h --long build:,help -- "$@"`
        eval set -- "$TEMP"
        while true; do
            case "$1" in
                -b|--build) release=$2; shift 2 ;;
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
echo "Building $name rpm, version $version, release $release"
echo "Requires: $requires"
echo "Build requires: $buildrequires"
echo

rpmbuild -bb ${CURRENT_DIR}/yii.spec \
                   --define "name $name" \
                   --define "version $version" \
                   --define "release $release" \
                   --define "source ${SOURCE_DIR}" \
                   --define "summary $summary" \
                   --define "requires $requires" \
                   --define "buildrequires $buildrequires" \
                   --define "meta $meta"
