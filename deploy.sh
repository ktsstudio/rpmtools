#!/bin/bash

#Script automatically increments revision in revision file. Creates tag and pushes it to git origin for deploy.
rev=$(head -n 1 BUILD_INFO);
package_name=$(head -n 2 BUILD_INFO | tac | head -n 1);
new_rev=$(echo "$rev" | awk -F. -v OFS=. 'NF==1{print ++$NF}; NF>1{if(length($NF+1)>length($NF))$(NF-1)++; $NF=sprintf("%0*d", length($NF), ($NF+1)%(10^length($NF))); print}');
echo "New version is $new_rev";
cat BUILD_INFO > /tmp/BUILD_INFO.$package_name;
sed '1d' /tmp/BUILD_INFO.$package_name > BUILD_INFO
sed -i -e '1 s/^/'"$new_rev"'\n/;' BUILD_INFO
rm -f /tmp/BUILD_INFO.$package_name
sed -i -e '1 s/^/\n\n\nv'"$new_rev"'\n=========\n\n/;' CHANGELOG
git commit BUILD_INFO CHANGELOG -m "Revision updated $new_rev";
git tag -a v$new_rev -m "Deploy tag";
git push origin master --tags;

