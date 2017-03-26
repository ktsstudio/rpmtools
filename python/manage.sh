#!/bin/sh
BINARY="manage.py"
VIRTUALENV_DIRECTORY="env"
SELF_DIR=$(readlink "${0}"); [ -z ${SELF_DIR} ] && SELF_DIR=${0}
SOURCE_ROOT=$(cd $(dirname "${SELF_DIR}"); pwd)

if [ -f ${SOURCE_ROOT}/${BINARY} ]; then
    echo "Execute ${SOURCE_ROOT}/${BINARY}"
    PROJECT_ROOT=$(dirname "${SOURCE_ROOT}")
    ENV_ROOT=${PROJECT_ROOT}/${VIRTUALENV_DIRECTORY}

    ${ENV_ROOT}/bin/python ${SOURCE_ROOT}/manage.py $@
    RETVAL=$?
else
    echo "Error: ${BINARY} not found" >&2
    RETVAL=1
fi

exit $RETVAL