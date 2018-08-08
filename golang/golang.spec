%define __prefix /opt
%define projectlocation %{gopath}/src/%{gopackage}
%define __spec_install_post /usr/lib/rpm/brp-compress || :

Name: %{name}
Summary: %{summary}
Version: %{version}
Release: %{release}%{?dist}
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
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

if [ -d "%{projectlocation}" ]; then
    echo "Cleaning out stale project GOPATH files" 1>&2
    rm -rf %{projectlocation}
    rm -rf %{gopath}/bin/%{name}
fi

# Setting up GOPATH and project location for building
mkdir -p %{name}
mkdir -p %{gopath}/bin
mkdir -p %{gopath}/pkg
mkdir -p %{projectlocation}

echo "Go version: $(go version)"
echo "GOPATH: %{gopath}"

%pre
/usr/bin/getent group %{name} || /usr/sbin/groupadd -r %{name}
/usr/bin/getent passwd %{name} || /usr/sbin/useradd -r -d /opt/%{name}/ -s /bin/false %{name} -g %{name}

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
    %{meta} buildCmds | while read i; do
        echo "Execute: ${i}"
        /bin/sh -c "${i}" || exit 1
    done

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
        set +x;
        VENDORLOCK_CONTENT=$(cat ${VENDORLOCK})
        #VENDORLOCK_CONTENT_COMMAND=$(%{meta} vendorLockCommand)
        #if [ "${VENDORLOCK_CONTENT_COMMAND}" != "" ]; then
        #    VENDORLOCK_CONTENT=$(bash -c "${VENDORLOCK_CONTENT_COMMAND}")
        #fi

        HASH=$(echo "${VENDORLOCK_CONTENT}" | md5sum | awk '{ print $1 }')
        set -x;

        echo "HASH=${HASH}"
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

    # Building
    mkdir -p %{gopath}/bin/%{name}
    %{meta} goMain | while read i; do
        go_build_ldflags="$(%{meta} "goBuild_ldflags._all $(%{meta} "goBuild_ldflags.$(echo ${i} | sed 's/\./\\./g')")"
        go_build_ldflags=$(eval "echo $go_build_ldflags")
        echo "${i}: ${go_build_ldflags}"
        go build -o "%{gopath}/bin/%{name}/`basename ${i%.*}`" -ldflags "${go_build_ldflags}" "${i}" || exit 1
    done

popd

rm -rf %{projectlocation}/.git*
rm -rf %{projectlocation}/rpmtools/.git*
rm -rf %{projectlocation}/.idea*

# removed grunt and bower stuff for now

find %{projectlocation}/ -type f -exec sed -i "s:%{_builddir}:%{__prefix}:" {} \;
# rm -rf %{gopath}/src/%{gopackage}


%install
# making project root directory
mkdir -p %{buildroot}%{__prefix}/%{name}

# moving gopath to buildroot
mkdir -p %{buildroot}%{gopath}/{pkg,bin}
mv %{gopath}/bin/%{name} %{buildroot}%{gopath}/bin/%{name} # bin

# config and /var/run
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}/var/run/%{name}

# linking gopath locations to project location
ln -sf %{projectlocation} %{buildroot}%{__prefix}/%{name}/src
ln -sf %{gopath}/bin/%{name} %{buildroot}%{__prefix}/%{name}/bin

for file in $(%{meta} copy --keys); do
    file_escape=$(echo $file | sed 's/\./\\./g')
    dest=$(%{meta} "copy.${file_escape}")

    echo "Copying $file -> $dest"
    cp -aR "%{projectlocation}/$file" "%{buildroot}%{__prefix}/%{name}/$dest"
done

%{meta} initScripts | while read i; do
    echo $i
    %if 0%{?rhel}  == 6
        %{__install} -p -D -m 0755 %{projectlocation}/${i} %{buildroot}%{_initrddir}/$(basename ${i})
        sed -i 's/#NAME#/%{name}/g' %{buildroot}%{_initrddir}/$(basename ${i})
    %endif

    %if 0%{?rhel}  == 7
        %{__install} -p -D -m 0755 %{projectlocation}/${i} %{buildroot}/usr/lib/systemd/system/$(basename ${i})
        sed -i 's/#NAME#/%{name}/g' %{buildroot}/usr/lib/systemd/system/$(basename ${i})
    %endif
done

# replace etc folder
if [ -d %{projectlocation}/build/etc ]; then
    rm -rf %{buildroot}%{_sysconfdir}/%{name}
    cp -rf %{projectlocation}/build/etc %{buildroot}%{_sysconfdir}/%{name}
fi

mkdir -p %{buildroot}%{_bindir}

rm -rf %{buildroot}%{projectlocation}/rpmtools
rm -rf %{buildroot}%{projectlocation}/build
rm -rf %{buildroot}%{projectlocation}/node_modules

%post
if [ $1 -gt 1 ]; then
    echo "Upgrade"
    mkdir -p /var/log/%{name}

    find %{__prefix}/%{name} -type f -name "*.py[co]" -delete
else
    echo "Install"

    %if 0%{?rhel}  == 6
        if [ -e /etc/init.d/%{name} ]; then
            /sbin/chkconfig --list %{name} > /dev/null 2>&1 || /sbin/chkconfig --add %{name}
            /sbin/chkconfig %{name} on
        fi
    %endif

    %if 0%{?rhel}  == 7
    if [ -e /usr/lib/systemd/system/%{name}.service ]; then
        systemctl enable %{name}.service
    fi
    %endif

    mkdir -p /var/log/%{name}
    chown -R %{name}:%{name} /var/log/%{name}
fi

%if 0%{?rhel}  == 7
    /bin/systemctl daemon-reload
%endif

/bin/bash -c "%{afterInstallCmd}" || true

%preun
if [ $1 -eq 0 ]; then
    %if 0%{?rhel}  == 6
    /sbin/chkconfig --del %{name}
    %endif

    %if 0%{?rhel}  == 7
    if [ -e /usr/lib/systemd/system/%{name}.service ]; then
        systemctl disable %{name}.service
    fi
    %endif
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{__prefix}/%{name}/
%{gopath}/bin/%{name}

%config(noreplace) %{_sysconfdir}/%{name}

%defattr(-,%{name_no_suffix},%{name_no_suffix})
/var/run/%{name}/

%if 0%{?rhel}  == 6 && 0%{?initPresents:1} == 1
%{_initrddir}/%{name_no_suffix}*
%endif

%if 0%{?rhel} == 7 && 0%{?initPresents:1} == 1
%config(noreplace) /usr/lib/systemd/system/%{name_no_suffix}*
%endif
