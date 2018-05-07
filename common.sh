#!/bin/bash

python -c 'import argparse' 2>/dev/null
if [ $? -ne 0 ];
then
	echo 'Python has not argparse module, abort'
	exit 1
fi

function yuminstall {
    PKGS=$@
    if [[ ${PKGS} != '' ]]; then
        if [ $(id -u) -eq 0 ];
        then
            echo "Install packages"
            yum install -y ${PKGS}
        else
            echo "If you want yum install, be root"
        fi
    fi
}

function get_packagejson {
    SOURCE_DIR=$1
    shift
    PACKAGEJSON="build/package.json"

    function meta_opts {
        TEMP=`getopt --long packagejson: -- "$@"`
        eval set -- "$TEMP"
        while true; do
            case "$1" in
                --packagejson) PACKAGEJSON="$2"; shift 2 ;;
                --) shift ; break ;;
                *) echo "Internal parsing error!: $1" ; exit 1 ;;
            esac
        done
    }

    meta_opts "$@"

    if [ ! -f "${SOURCE_DIR}${PACKAGEJSON}" ]; then
        return
    fi

    echo ${PACKAGEJSON}
}

cat ${CURRENT_DIR}/../logo.txt