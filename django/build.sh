#!/bin/bash
CURRENT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
SOURCE_DIR="${CURRENT_DIR}/../../"
BUILD_INFO="${SOURCE_DIR}/build/BUILD_INFO"

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

version=$(sed '1q;d' ${BUILD_INFO})
release=$(date +%s)
name=$(sed '2q;d' ${BUILD_INFO})
summary=$(sed '3q;d' ${BUILD_INFO})
requires=$(sed '4q;d' ${BUILD_INFO})
buildrequires=$(sed '5q;d' ${BUILD_INFO})
wsgi=$(sed '6q;d' ${BUILD_INFO})
echo "Building $name rpm. Version is $version. Release $release"
echo "Requires: $requires"
echo "Build requires: $buildrequires"

rpmbuild -bb ${CURRENT_DIR}/django.spec \
                   --define "name $name" \
                   --define "version $version" \
                   --define "release $release" \
                   --define "source ${SOURCE_DIR}" \
                   --define "summary $summary" \
                   --define "requires $requires" \
                   --define "buildrequires $buildrequires" \
                   --define "wsgi $wsgi" \
                   --define "virtualenv $VIRTUALENV"