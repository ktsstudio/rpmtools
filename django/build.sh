#!/bin/bash
CURRENT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
SOURCE_DIR="${CURRENT_DIR}/../../"
BUILD_INFO="${SOURCE_DIR}/build/BUILD_INFO"
VIRTUALENV=$(which virtualenv)
GRUNTTASK="default"
ADDITIONAL_INIT_SCRIPTS=()
AUTO_MIGRATE=1
ENABLE_CELERYCAM=1

version=$(sed '1q;d' ${BUILD_INFO})
release=$(date +%s)
name=$(sed '2q;d' ${BUILD_INFO})
summary=$(sed '3q;d' ${BUILD_INFO})
requires=$(sed '4q;d' ${BUILD_INFO})
buildrequires=$(sed '5q;d' ${BUILD_INFO})
wsgi=$(sed '6q;d' ${BUILD_INFO})
keys=$(sed '7q;d' ${BUILD_INFO})

function opts {
        TEMP=`getopt -o v:g:b:h -l virtualenv:,grunttask:,build:,add-init:,help,disable-auto-migrate,disable-celerycam -- "$@"`
        eval set -- "$TEMP"
        while true; do
            case "$1" in
                -b|--build) release=$2; shift 2 ;;
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
for j in $keys;
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
echo "Building $name rpm, version $version, release $release"
echo "Requires: $requires"
echo "Build requires: $buildrequires"
echo

yum install -y $buildrequires || true
rpmbuild -bb ${CURRENT_DIR}/django.spec \
                   --define "name $name" \
                   --define "version $version" \
                   --define "release $release" \
                   --define "source ${SOURCE_DIR}" \
                   --define "summary $summary" \
                   --define "requires $requires" \
                   --define "buildrequires $buildrequires" \
                   --define "wsgi $wsgi" \
                   --define "additional_init_scripts ${ADDITIONAL_INIT_SCRIPTS[*]}" \
                   --define "auto_migrate ${AUTO_MIGRATE}" \
                   --define "enable_celerycam ${ENABLE_CELERYCAM}" \
                   --define "virtualenv ${VIRTUALENV}" \
                   --define "grunttask ${GRUNTTASK}"