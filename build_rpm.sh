#!/bin/bash
version=$(sed '1q;d' ../BUILD_INFO)
release=$(date +%s)
name=$(sed '2q;d' ../BUILD_INFO)
summary=$(sed '3q;d' ../BUILD_INFO)
requires=$(sed '4q;d' ../BUILD_INFO)
buildrequires=$(sed '5q;d' ../BUILD_INFO)
echo "Building $name rpm. Version is $version. Release $release"
echo "Requires: $requires"
echo "Build requires: $buildrequires"
rpmbuild -bb generic_django.spec --define "name $name" --define "version $version" --define "release $release" --define "source $(cd ..;pwd)" --define "summary $summary" --define "requires $requires" --define "buildrequires $buildrequires"
