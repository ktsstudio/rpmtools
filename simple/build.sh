#!/bin/bash
CURRENT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
SOURCE_DIR="${CURRENT_DIR}/../.."
META="python ${CURRENT_DIR}/../meta.py --file ${CURRENT_DIR}/../../package.json --query"
GRUNTTASK="default"
COMMAND="exit 0"
PUBLIC_DIR_NAME="public"

name=$(${META} name)
versionsuffix=""
summary=$(${META} name)
version=$(${META} version)
release=$(date +%s)
meta=$(echo ${META})

function opts {
        TEMP=`getopt -o g:s:b:h:c:p --long grunttask:,versionsuffix:,build:,command:,public:,help -- "$@"`
        eval set -- "$TEMP"
        while true; do
            case "$1" in
                -b|--build) release=$2; shift 2 ;;
                -s|--versionsuffix) versionsuffix=$2; shift 2 ;;
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

echo "Building $name rpm. Version is $version. Release $release"
echo "Requires: $requires"
echo "Build requires: $buildrequires"
echo "Public dirname: $PUBLIC_DIR_NAME"

rpmbuild -bb ${CURRENT_DIR}/simple.spec \
                   --define "name $name" \
                   --define "version $version$versionsuffix" \
                   --define "release $release" \
                   --define "source ${SOURCE_DIR}" \
                   --define "summary $summary" \
                   --define "meta $meta" \
                   --define "grunttask ${GRUNTTASK}" \
                   --define "command ${COMMAND}" \
                   --define "public ${PUBLIC_DIR_NAME}"
