%define __prefix /opt
%define projectlocation %{gopath}/src/%{gopackage}
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

if [ -d %{gopath} ]; then
    echo "Cleaning out stale GOPATH" 1>&2
    rm -rf %{gopath}
fi

# Setting up GOPATH and project location for building
mkdir -p %{gopath}/bin
mkdir -p %{gopath}/pkg
mkdir -p %{projectlocation}

%pre
/usr/bin/getent group %{name} || /usr/sbin/groupadd -r %{name}
/usr/bin/getent passwd %{name} || /usr/sbin/useradd -r -d /opt/%{name}/ -s /bin/false %{name} -g %{name}

%build
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
    mkdir -p %{gopath}/bin/%{name}
    %{meta} goMain | while read i; do
        echo "Executing: go build ${i}"
        go build -o "%{gopath}/bin/%{name}/`basename ${i%.*}`" "${i}" || exit 1
    done

popd

rm -rf %{projectlocation}/.git*
rm -rf %{projectlocation}/rpmtools/.git*
rm -rf %{projectlocation}/.idea*

# removed grunt and bower stuff for now

find %{projectlocation}/ -type f -exec sed -i "s:%{_builddir}:%{__prefix}:" {} \;


%install
# making project root directory
mkdir -p %{buildroot}%{__prefix}/%{name}

# movinf gopath to buildroot
mv %{gopath} %{buildroot}%{__prefix}

# config and /var/run
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}/var/run/%{name}

# linking gopath locations to project location
ln -sf %{projectlocation} %{buildroot}%{__prefix}/%{name}/src
ln -sf %{gopath}/bin/%{name} %{buildroot}%{__prefix}/%{name}/bin

for SRC in $(%{meta} copy --keys); do
    DEST=$(%{meta} "copy.$SRC")
    
    echo "Copying $SRC -> $DEST"
    cp -aR %{buildroot}%{projectlocation}/$SRC %{buildroot}%{__prefix}/%{name}
done

%{meta} initScripts | while read i; do
    echo $i
    %if 0%{?rhel}  == 6
        %{__install} -p -D -m 0755 %{buildroot}%{projectlocation}/${i} %{buildroot}%{_initrddir}/$(basename ${i})
        sed -i 's/#NAME#/%{name}/g' %{buildroot}%{_initrddir}/$(basename ${i})
    %endif

    %if 0%{?rhel}  == 7
        %{__install} -p -D -m 0755 %{buildroot}%{projectlocation}/${i} %{buildroot}/usr/lib/systemd/system/$(basename ${i})
        sed -i 's/#NAME#/%{name}/g' %{buildroot}/usr/lib/systemd/system/$(basename ${i})
    %endif
done

# replace etc folder
if [ -d %{buildroot}%{projectlocation}/build/etc ]; then
    rm -rf %{buildroot}%{_sysconfdir}/%{name}
    cp -rf %{buildroot}%{projectlocation}/build/etc %{buildroot}%{_sysconfdir}/%{name}
fi

if [ ! -e %{buildroot}%{projectlocation}/manage.sh ]; then
    cp -r %{buildroot}%{projectlocation}/rpmtools/python/manage.sh %{buildroot}%{projectlocation}/manage.sh
fi

chmod 755 %{buildroot}%{projectlocation}/manage.sh

mkdir -p %{buildroot}%{_bindir}
ln -sf %{projectlocation}/manage.sh %{buildroot}%{_bindir}/%{name}

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
%{gopath}/src/%{gopackage}
%{gopath}/bin/%{name}
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
