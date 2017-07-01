%define __prefix /opt
%define __spec_install_post /usr/lib/rpm/brp-compress || :

Name: %{name}
Summary: %{summary}
Version: %{version}
Release: %{release}%{?dist}
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
Requires: %{requires}
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

%pre
/usr/bin/getent group %{name} || /usr/sbin/groupadd -r %{name}
/usr/bin/getent passwd %{name} || /usr/sbin/useradd -r -d /opt/%{name}/ -s /bin/false %{name} -g %{name}

%build

# Setting up GOPATH and project location for building
mkdir -p %{gopath}/src/%{gopackage}
mkdir -p %{gopath}/bin
rm -rf %{gopath}/bin/*

cp -r '%{source}' %{gopath}/src/%{gopackage}

mkdir -p %{name}

pushd %{gopath}/src/%{gopackage}
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
    
    # Building
    %{meta} goMain | while read i; do
        echo "Executing: go build ${i}"
        go build -o "%{gopath}/bin/`basename ${i%.*}`" "${i}" || exit 1
    done

popd

cp -r '%{gopath}/src/%{gopackage}' %{name}/src
cp -r '%{gopath}/bin' %{name}/bin

rm -rf %{name}/src/.git*
rm -rf %{name}/src/rpmtools/.git*
rm -rf %{name}/src/.idea*

# removed grunt and bower stuff for now

pushd %{name}/src
    %{meta} buildCmds | while read i; do
        echo "Execute: ${i}"
        /bin/sh -c "${i}" || exit 1
    done

    for i in $(%{meta} excludeFiles); do
        echo "Remove files: ${i}"
        rm -rf ${i}
    done
popd

# find %{name}/ -type f -name "*.py[co]" -delete
find %{name}/ -type f -exec sed -i "s:%{_builddir}:%{__prefix}:" {} \;


%install
mkdir -p %{buildroot}%{__prefix}/%{name}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}/var/run/%{name}

mv %{name} %{buildroot}%{__prefix}/

%{meta} initScripts | while read i; do
    echo $i
    %if 0%{?rhel}  == 6
        %{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/src/${i} %{buildroot}%{_initrddir}/$(basename ${i})
        sed -i 's/#NAME#/%{name}/g' %{buildroot}%{_initrddir}/$(basename ${i})
    %endif

    %if 0%{?rhel}  == 7
        %{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/src/${i} %{buildroot}/usr/lib/systemd/system/$(basename ${i})
        sed -i 's/#NAME#/%{name}/g' %{buildroot}/usr/lib/systemd/system/$(basename ${i})
    %endif
done

# replace etc folder
if [ -d %{buildroot}%{__prefix}/%{name}/src/build/etc ]; then
    rm -rf %{buildroot}%{_sysconfdir}/%{name}
    cp -rf %{buildroot}%{__prefix}/%{name}/src/build/etc %{buildroot}%{_sysconfdir}/%{name}
fi

if [ ! -e %{buildroot}%{__prefix}/%{name}/src/manage.sh ]; then
    cp -r %{buildroot}%{__prefix}/%{name}/src/rpmtools/python/manage.sh %{buildroot}%{__prefix}/%{name}/src/manage.sh
fi

chmod 755 %{buildroot}%{__prefix}/%{name}/src/manage.sh

mkdir -p %{buildroot}%{_bindir}
ln -sf %{__prefix}/%{name}/src/manage.sh %{buildroot}%{_bindir}/%{name}

rm -rf %{buildroot}%{__prefix}/%{name}/src/rpmtools
rm -rf %{buildroot}%{__prefix}/%{name}/src/env
rm -rf %{buildroot}%{__prefix}/%{name}/src/build
rm -rf %{buildroot}%{__prefix}/%{name}/src/local_settings.py
rm -rf %{buildroot}%{__prefix}/%{name}/src/node_modules

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
%{_bindir}/%{name}

%config(noreplace) %{_sysconfdir}/%{name}

%defattr(-,%{name},%{name})
/var/run/%{name}/

%if 0%{?rhel}  == 6 && 0%{?initPresents:1} == 1
%{_initrddir}/%{name}*
%endif

%if 0%{?rhel} == 7 && 0%{?initPresents:1} == 1
%config(noreplace) /usr/lib/systemd/system/%{name}*
%endif
