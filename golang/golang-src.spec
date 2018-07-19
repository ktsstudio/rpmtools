%define __prefix /opt
%define projectlocation %{gopath}/src/%{gopackage}
%define __spec_install_post /usr/lib/rpm/brp-compress || :

Name: %{name}-src
Summary: %{summary}
Version: %{version}
Release: %{release}%{?dist}
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
Requires: golang
%if "%{requires}" != "none"
Requires: %{requires}
%endif
BuildRequires: %{buildrequires}
License: proprietary
Group: Apps/sys
Autoreq: 0


%description
%{name} built with generic golang project spec

%prep
if [ -d %{name} ]; then
    echo "Cleaning out stale build directory" 1>&2
    rm -rf %{name}
fi

if [ -d %{gopath} ]; then
    echo "Cleaning out stale GOPATH" 1>&2
    rm -rf %{gopath}
fi

# Setting up GOPATH and project location for building
mkdir -p %{projectlocation}

echo "Go version: $(go version)"

%build
pushd %{source}
    export rpmtools_version=%{version}
    export rpmtools_release=$(echo %{release} | sed s/%{?dist}//g)
    export rpmtools_git_hash_short=$(git rev-parse --short HEAD)

    echo "Version: ${rpmtools_version}"
    echo "Release: ${rpmtools_release}"
    echo "GIT short: ${rpmtools_git_hash_short}"
popd

cp -r '%{source}' %{gopath}/src/%{gopackage}

pushd %{projectlocation}
    for i in $(%{meta} excludeFiles); do
        echo "Remove files: ${i}"
        rm -rf ${i}
    done
popd

pushd %{projectlocation}
    VENDORLOCK=$(%{meta} vendorLock)
    if [ "${VENDORLOCK}" == '' ]; then
        VENDORLOCK="Gopkg.lock"
    else
        VENDORLOCK="${VENDORLOCK}"
    fi

    if [ -f "${VENDORLOCK}" ]; then
        VENDORLOCK_CONTENT=$(cat ${VENDORLOCK})
        VENDORLOCK_CONTENT_COMMAND=$(%{meta} vendorLockCommand)
        if [ "${VENDORLOCK_CONTENT_COMMAND}" != "" ]; then
            VENDORLOCK_CONTENT=$(bash -c "${VENDORLOCK_CONTENT_COMMAND}")
        fi

        HASH=$(echo "${VENDORLOCK_CONTENT}" | md5sum | awk '{ print $1 }')
        CACHED_VENDOR="/tmp/golang_vendor_${HASH}.tar"

        if [ -e "${CACHED_VENDOR}" ]
        then
          echo "Found cached vendor: ${CACHED_VENDOR}, use it"
          tar xf ${CACHED_VENDOR} ./vendor
        else
          echo "No found cached vendor, download..."

          echo "Installing dependencies..."
          go get -u github.com/golang/dep/cmd/dep
          %{gopath}/bin/dep ensure

          echo "Save vendor into cache: ${CACHED_VENDOR}"
          tar cf ${CACHED_VENDOR} ./vendor || true
        fi
    else
        echo 'Not found vendorlock, skipped...'
    fi
popd

rm -rf %{projectlocation}/.git*
rm -rf %{projectlocation}/rpmtools/.git*
rm -rf %{projectlocation}/.idea*

# removed grunt and bower stuff for now

find %{projectlocation}/ -type f -exec sed -i "s:%{_builddir}:%{__prefix}:" {} \;


%install
# making project root directory
mkdir -p %{buildroot}%{__prefix}/%{name}

# moving gopath to buildroot
mkdir -p %{buildroot}%{gopath}/src
mkdir -p $(dirname "%{buildroot}%{projectlocation}") # create every dir but the last
mv %{projectlocation} %{buildroot}%{projectlocation} # src

# linking gopath locations to project location
ln -sf %{projectlocation} %{buildroot}%{__prefix}/%{name}/src

rm -rf %{buildroot}%{projectlocation}/rpmtools
rm -rf %{buildroot}%{projectlocation}/build
rm -rf %{buildroot}%{projectlocation}/node_modules

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{__prefix}/%{name}/src
%{gopath}/src/%{gopackage}
