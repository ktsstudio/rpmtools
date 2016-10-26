#!/bin/bash
CURRENT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
SOURCE_DIR="${CURRENT_DIR}/../../"
VIRTUALENV=$(which virtualenv)

source ${CURRENT_DIR}/../common.sh

BUILD_INFO="${SOURCE_DIR}/build/BUILD_INFO"
GRUNTTASK="default"
ADDITIONAL_INIT_SCRIPTS=()
AUTO_MIGRATE=1
ENABLE_CELERYCAM=1

VERSION=$(sed '1q;d' ${BUILD_INFO})
RELEASE=$(date +%s)
NAME=$(sed '2q;d' ${BUILD_INFO})
SUMMARY=$(sed '3q;d' ${BUILD_INFO})
REQUIRES=$(sed '4q;d' ${BUILD_INFO})
BUILDREQUIRES=$(sed '5q;d' ${BUILD_INFO})
WSGI=$(sed '6q;d' ${BUILD_INFO})
KEYS=$(sed '7q;d' ${BUILD_INFO})

function opts {
        TEMP=`getopt -o v:g:b:h -l virtualenv:,grunttask:,build:,add-init:,help,disable-auto-migrate,disable-celerycam -- "$@"`
        eval set -- "$TEMP"
        while true; do
            case "$1" in
                -b|--build) RELEASE=$2; shift 2 ;;
                -g|--grunttask) GRUNTTASK=$2; shift 2 ;;
                -v|--virtualenv) VIRTUALENV=$2; shift 2 ;;
                --add-init) ADDITIONAL_INIT_SCRIPTS+=($2); shift 2;;
                --disable-auto-migrate) AUTO_MIGRATE=0; shift 1;;
                --disable-celerycam) ENABLE_CELERYCAM=0; shift 1;;
                -h|--help) echo 'help under constuction' ; shift 1;;
                --) shift ; break ;;
                *) echo "Internal parsing error!: $1" ; exit 1 ;;
            esac
        done
}

params=$@
for j in $KEYS;
do
    params+=($j)
done
opts ${params[@]}

if [ -z ${ADDITIONAL_INIT_SCRIPTS} ]; then
    ADDITIONAL_INIT_SCRIPTS=0
fi

export FULLVERSION="${VERSION}-${RELEASE}"

cat ${CURRENT_DIR}/../logo.txt

echo
echo
echo "Building $NAME rpm, version $VERSION, release $RELEASE"
echo "Requires: $REQUIRES"
echo "Build requires: $BUILDREQUIRES"
echo

yuminstall ${BUILDREQUIRES}

rpmbuild -bb ${CURRENT_DIR}/django.spec \
                   --define "name $NAME" \
                   --define "version $VERSION" \
                   --define "release $RELEASE" \
                   --define "source ${SOURCE_DIR}" \
                   --define "summary $SUMMARY" \
                   --define "requires $REQUIRES" \
                   --define "buildrequires $BUILDREQUIRES" \
                   --define "wsgi $WSGI" \
                   --define "additional_init_scripts ${ADDITIONAL_INIT_SCRIPTS[*]}" \
                   --define "auto_migrate ${AUTO_MIGRATE}" \
                   --define "enable_celerycam ${ENABLE_CELERYCAM}" \
                   --define "virtualenv ${VIRTUALENV}" \
                   --define "grunttask ${GRUNTTASK}"