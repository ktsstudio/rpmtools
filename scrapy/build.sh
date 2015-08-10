#!/bin/bash
CURRENT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
SOURCE_DIR="${CURRENT_DIR}/../../"
META="python ${CURRENT_DIR}/../meta.py --file ${CURRENT_DIR}/../../package.json --query"

VIRTUALENV=$(which virtualenv)

function opts {
        TEMP=`getopt -o v:h --long virtualenv:,help -- "$@"`
        eval set -- "$TEMP"
        while true; do
            case "$1" in
                -v|--virtualenv) VIRTUALENV=$2; shift 2 ;;
                -h|--help) echo 'help under constuction' ; shift 1;;
                --) shift ; break ;;
                *) echo "Internal parsing error!: $1" ; exit 1 ;;
            esac
        done
}
opts "$@"


name=$(${META} name)
summary=$(${META} name)
version=$(${META} version)
release=$(date +%s)
requires=$(${META} yumDependencies)
buildrequires="$(${META} yumBuildDependencies) python-argparse"
meta=$(echo ${META})

echo "Building $name rpm. Version is $version. Release $release"
echo "Requires: $requires"
echo "Build requires: $buildrequires"

rpmbuild -bb ${CURRENT_DIR}/scrapy.spec \
                   --define "name $name" \
                   --define "version $version" \
                   --define "release $release" \
                   --define "source ${SOURCE_DIR}" \
                   --define "summary $summary" \
                   --define "requires $requires" \
                   --define "buildrequires $buildrequires" \
                   --define "meta $meta" \
                   --define "virtualenv $VIRTUALENV"
