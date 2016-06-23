#!/bin/bash
CURRENT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
SOURCE_DIR="${CURRENT_DIR}/../../"
META="python ${CURRENT_DIR}/../meta.py --file ${SOURCE_DIR}/build/package.json --query"

name=$(${META} name)
version=$(${META} version)
versionsuffix=""
release=$(date +%s)
summary=$(${META} description)
requires=$(${META} yumDependencies)
buildrequires="$(${META} yumBuildDependencies) python-argparse"
meta=$(echo ${META})

VIRTUALENV=$(which virtualenv)

function opts {
        TEMP=`getopt -o s:v:b:f:h --long supervisor:,virtualenv:,build:,versionsuffix:,help -- "$@"`
        eval set -- "$TEMP"
        while true; do
            case "$1" in
                -h|--help) echo 'help under constuction' ; shift 1;;
                -b|--build) release=$2; shift 2 ;;
                -f|--versionsuffix) versionsuffix=$2; shift 2 ;;
                -v|--virtualenv) VIRTUALENV=$2; shift 2 ;;
                --) shift ; break ;;
                *) echo "Internal parsing error!: $1" ; exit 1 ;;
            esac
        done
}
opts "$@"

echo "Building $name rpm. Version is $version. Release $release"
echo "Requires: $requires"
echo "Build requires: $buildrequires"

rpmbuild -bb ${CURRENT_DIR}/tornado.spec \
                   --define "name $name" \
                   --define "version $version$versionsuffix" \
                   --define "release $release" \
                   --define "source ${SOURCE_DIR}" \
                   --define "summary $summary" \
                   --define "requires $requires" \
                   --define "buildrequires $buildrequires" \
                   --define "virtualenv $VIRTUALENV" \
                   --define "meta $meta"
