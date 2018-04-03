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
%{name} built with generic node project spec

%prep
if [ -d %{name} ]; then
    echo "Cleaning out stale build directory" 1>&2
    rm -rf %{name}
fi

%pre
/usr/bin/getent group %{name} || /usr/sbin/groupadd -r %{name}
/usr/bin/getent passwd %{name} || /usr/sbin/useradd -r -d /opt/%{name}/ -s /bin/false %{name} -g %{name}


%build

mkdir -p %{name}
cp -r '%{source}' %{name}
rm -rf %{name}/.git*
rm -rf %{name}/rpmtools/.git*
rm -rf %{name}/.idea*


pushd %{name}
    if [ -e "package.json" ]
    then
        if [ -e "package-lock.json" ]; then
            HASH=$(cat package-lock.json | grep 'version' | md5sum | awk '{ print $1 }')
        else
            HASH=$(cat package.json | grep -v 'version' | md5sum | awk '{ print $1 }')
        fi
        CACHED_NODE_MODULES="/tmp/node_modules_${HASH}.tar"
        if [ -e "${CACHED_NODE_MODULES}" ]
        then
          echo "Found cached node_modules: ${CACHED_NODE_MODULES}, use it"
          tar xf ${CACHED_NODE_MODULES} ./
          npm install --unsafe-perm
        else
          echo "No found cached node_modules, download..."
          npm install --unsafe-perm || exit 1
          echo "Save node_modules into cache: ${CACHED_NODE_MODULES}"
          tar cf ${CACHED_NODE_MODULES} ./node_modules || true
        fi
    fi

    for i in $(%{meta} excludeFiles); do
        echo "Remove files: ${i}"
        rm -rf ${i}
    done
popd

%install
# making project root directory
mkdir -p %{buildroot}%{__prefix}/%{name}
mv %{name} %{buildroot}%{__prefix}/

ls -lah "%{buildroot}%{__prefix}/%{name}"

mkdir -p "%{buildroot}/etc/%{name}"

# install systemd scripts
%{meta} initScripts | while read i; do
    echo $i
    %if 0%{?rhel}  == 6
        %{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/${i} %{buildroot}%{_initrddir}/$(basename ${i})
        sed -i 's/#NAME#/%{name}/g' %{buildroot}%{_initrddir}/$(basename ${i})
    %endif

    %if 0%{?rhel}  == 7
        %{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/${i} %{buildroot}/usr/lib/systemd/system/$(basename ${i})
        sed -i 's/#NAME#/%{name}/g' %{buildroot}/usr/lib/systemd/system/$(basename ${i})
    %endif
done

# copy files
for file in $(%{meta} copy --keys); do
    file_escape=$(echo $file | sed 's/\./\\./g')
    dest=$(%{meta} "copy.${file_escape}")
    if [[ ! $dest =~ ^/ ]]; then
        dest="%{__prefix}/%{name}/$dest"
    fi
    
    echo "Copying $file -> $dest"
    destdirname=$(dirname "%{buildroot}%{__prefix}/%{name}/$file")
    mkdir -p "$destdirname"
    cp -aR "%{buildroot}%{__prefix}/%{name}/$file" "%{buildroot}/$dest"
done

# misc
rm -rf %{buildroot}%{__prefix}/%{name}/rpmtools
mkdir -p %{buildroot}/var/run/%{name}

%post
if [ $1 -gt 1 ]; then
    echo "Upgrade"
else
    echo "Install"
    /sbin/chkconfig --list %{name} > /dev/null 2>&1 || /sbin/chkconfig --add %{name}
    /sbin/chkconfig %{name} on

    mkdir -p /var/log/%{name}
    chown -R %{name}:%{name} /var/log/%{name}

    mkdir -p /var/lib/%{name}
    chown -R %{name}:%{name} /var/lib/%{name}

    mkdir -p /opt/%{name}/.config
    chown -R %{name}:%{name} /opt/%{name}/.config
fi

%preun
if [ $1 -eq 0 ]; then
    /sbin/chkconfig --del %{name}
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{__prefix}/%{name}/

%if 0%{?rhel} == 6 
%{_initrddir}/*
%endif

%if 0%{?rhel} == 7 
%config(noreplace) /usr/lib/systemd/system/*
%endif

%config(noreplace) /etc/%{name}/*

%defattr(-,%{name},%{name})
/var/run/%{name}/