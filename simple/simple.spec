%define __prefix /opt
%define __spec_install_post /usr/lib/rpm/brp-compress || :

Name: %{name}
Summary: %{summary}
Version: %{version}
Release: %{release}
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildRequires: python-argparse
License: proprietary
Group: Apps/sys
Autoreq: 0


%description
%{name} built with generic frontend (backbone/angular) project spec

%prep
if [ -d %{name} ]; then
    echo "Cleaning out stale build directory" 1>&2
    rm -rf %{name}
fi

%build
mkdir -p %{name}
cp -rf %{source} %{name}/ || true
cd %{name}

if [ -e "package.json" ]
then
    HASH=$(md5sum package.json | awk '{ print $1 }')
    CACHED_NODE_MODULES="/tmp/node_modules_${HASH}.tar"
    if [ -e "${CACHED_NODE_MODULES}" ]
    then
      echo "Found cached node_modules: ${CACHED_NODE_MODULES}, use it"
      tar xf ${CACHED_NODE_MODULES} ./
    else
      echo "No found cached node_modules, download..."
      npm install || exit 1
      echo "Save node_modules into cache: ${CACHED_NODE_MODULES}"
      tar cf ${CACHED_NODE_MODULES} ./node_modules || true
    fi
fi

if [ -e "bower.json" ]
then
    HASH=$(md5sum bower.json | awk '{ print $1 }')
    CACHED_BOWER_COMPONENTS="/tmp/bower_components_${HASH}.tar"
    if [ -e "${CACHED_BOWER_COMPONENTS}" ]
    then
      echo "Found cached bower_components: ${CACHED_BOWER_COMPONENTS}, use it"
      tar xf ${CACHED_BOWER_COMPONENTS} ./
    else
      echo "No found cached bower_components, download..."
      bower install --allow-root || exit 1
      if [ -e "./bower_components" ]
      then
        echo "Save bower_components into cache: ${CACHED_BOWER_COMPONENTS}"
        tar cf ${CACHED_BOWER_COMPONENTS} ./bower_components || true
      else
        echo "bower_components not found, not save"
      fi
    fi
fi

if [ -e "Gruntfile.js" ]
then
    grunt %{grunttask} || exit 1
fi

%install
mkdir -p %{buildroot}%{__prefix}/
mv %{name}/public %{buildroot}%{__prefix}/%{name}


%post

%preun

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{__prefix}/%{name}
