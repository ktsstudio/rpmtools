#!/bin/bash
CURRENT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
SOURCE_DIR="${CURRENT_DIR}/../../"
BUILD_INFO="${SOURCE_DIR}/build/BUILD_INFO"
META="python ${CURRENT_DIR}/../meta.py --file ${CURRENT_DIR}/../../package.json --query"

name=$(${META} name)
summary=$(${META} name)
version=$(${META} version)
release=$(date +%s)
requires=$(${META} yumDependencies)
buildrequires=$(${META} yumBuildDependencies)
meta=$(echo ${META})

echo "Building $name rpm. Version is $version. Release $release"
echo "Requires: $requires"
echo "Build requires: $buildrequires"

rpmbuild -bb ${CURRENT_DIR}/yii.spec \
                   --define "name $name" \
                   --define "version $version" \
                   --define "release $release" \
                   --define "source ${SOURCE_DIR}" \
                   --define "summary $summary" \
                   --define "requires $requires" \
                   --define "buildrequires $buildrequires" \
                   --define "meta $meta"
