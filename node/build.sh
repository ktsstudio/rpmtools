#!/bin/bash
set -e

CURRENT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
SOURCE_DIR="${CURRENT_DIR}/../../"
META="python ${CURRENT_DIR}/../meta.py --file ${SOURCE_DIR}/package.json --query"

name=$(${META} name)
version=$(${META} version)
release=$(date +%s)
summary=$(${META} description)
requires=$(${META} yumDependencies)
buildrequires="$(${META} yumBuildDependencies) python-argparse"
meta=$(echo ${META})

function opts {
        TEMP=`getopt -o b:h --long build:,help -- "$@"`
        eval set -- "$TEMP"
        while true; do
            case "$1" in
                -h|--help) echo 'help under constuction' ; shift 1;;
                -b|--build) release=$2; shift 2 ;;
                --) shift ; break ;;
                *) echo "Internal parsing error!: $1" ; exit 1 ;;
            esac
        done
}
opts "$@"

echo "Building $name rpm. Version is $version. Release $release"
echo "Requires: $requires"
echo "Build requires: $buildrequires"

rpmbuild -bb ${CURRENT_DIR}/node.spec \
                   --define "name $name" \
                   --define "version $version" \
                   --define "release $release" \
                   --define "source ${SOURCE_DIR}" \
                   --define "summary $summary" \
                   --define "requires $requires" \
                   --define "buildrequires $buildrequires" \
                   --define "meta $meta"