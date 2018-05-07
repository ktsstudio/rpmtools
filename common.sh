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

cat ${CURRENT_DIR}/../logo.txt
echo