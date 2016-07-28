%define __prefix /opt
%define __spec_install_post /usr/lib/rpm/brp-compress || :

Name: %{name}
Summary: %{summary}
Version: %{version}
Release: %{release}%{?dist}
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
Requires: %{requires} supervisor = 3.1.3
BuildRequires: %{buildrequires}
License: proprietary
Group: Apps/sys
Autoreq: 0


%description
%{name} built with generic tornado project spec

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
cp -r '%{source}' %{name}/src
rm -rf %{name}/src/.git*
rm -rf %{name}/src/rpmtools/.git*
rm -rf %{name}/src/.idea*


HASH=$(echo "$(cat %{name}/src/requirements.txt)%{virtualenv}" | md5sum | awk '{ print $1 }')
CACHED_VIRTUALENV="/tmp/virtualenv_${HASH}.tar"
if [ -e "${CACHED_VIRTUALENV}" ]
then
  echo "Found cached virtualenv: ${CACHED_VIRTUALENV}, use it"
  tar xf ${CACHED_VIRTUALENV} %{name}
else
  echo "No found cached virtualenv, download..."

  %{virtualenv} --distribute %{name}/env
  %{name}/env/bin/easy_install -U distribute
  %{name}/env/bin/pip install -r %{name}/src/requirements.txt --upgrade
  %{virtualenv} --relocatable %{name}/env

  echo "Save virtualenv into cache: ${CACHED_VIRTUALENV}"
  tar cf ${CACHED_VIRTUALENV} %{name}/env || true
fi

find %{name}/ -type f -name "*.py[co]" -delete
find %{name}/ -type f -exec sed -i "s:%{_builddir}:%{__prefix}:" {} \;

pushd %{name}/src
    gruntCwd=$(%{meta} gruntCwd)
    if [ $gruntCwd != '' ]
    then
        cd $gruntCwd
    fi

    if [ -e "package.json" ]
    then
        HASH=$(cat package.json | grep -v 'version' | md5sum | awk '{ print $1 }')
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
        HASH=$(cat bower.json | grep -v 'version' | md5sum | awk '{ print $1 }')
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
        grunt $(%{meta} grunt_task) || exit 1
    fi
popd

pushd %{name}/src
    for i in $(%{meta} excludeFiles); do
        echo "Remove files: ${i}"
        rm -rf ${i}
    done
popd

%install
mkdir -p %{buildroot}%{__prefix}/%{name}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/programs
mkdir -p %{buildroot}/var/run/%{name}

mv %{name} %{buildroot}%{__prefix}/

# hack for lib64
[ -d %{buildroot}%{__prefix}/%{name}/env/lib64 ] && rm -rf %{buildroot}%{__prefix}/%{name}/env/lib64 && ln -sf %{__prefix}/%{name}/env/lib %{buildroot}%{__prefix}/%{name}/env/lib64

%if 0%{?rhel}  == 6
%{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/src/rpmtools/tornado/c6/main.init.sh %{buildroot}%{_initrddir}/%{name}
%endif

%if 0%{?rhel}  == 7
%{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/src/rpmtools/tornado/c7/systemd %{buildroot}/usr/lib/systemd/system/%{name}.service
sed -i 's/#NAME#/%{name}/g' %{buildroot}/usr/lib/systemd/system/%{name}.service
%endif

# configs
%{__install} -p -D -m 0644 %{buildroot}%{__prefix}/%{name}/src/build/default.conf %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf

%{__install} -p -D -m 0644 %{buildroot}%{__prefix}/%{name}/src/rpmtools/tornado/etc/supervisord.conf %{buildroot}%{_sysconfdir}/%{name}/supervisord.conf
sed -i 's/#NAME#/%{name}/g' %{buildroot}%{_sysconfdir}/%{name}/supervisord.conf

if [ -d %{buildroot}%{__prefix}/%{name}/src/build/programs ]; then
    %{__install} -p -D -m 0644 --target-directory=%{buildroot}%{_sysconfdir}/%{name}/programs %{buildroot}%{__prefix}/%{name}/src/build/programs/*
else
    %{__install} -p -D -m 0644 %{buildroot}%{__prefix}/%{name}/src/rpmtools/tornado/etc/program.conf %{buildroot}%{_sysconfdir}/%{name}/programs/%{name}.conf
    sed -i 's/#NAME#/%{name}/g' %{buildroot}%{_sysconfdir}/%{name}/programs/%{name}.conf
fi

rm -rf %{buildroot}%{__prefix}/%{name}/src/rpmtools
rm -rf %{buildroot}%{__prefix}/%{name}/src/env

%post
if [ $1 -gt 1 ]; then
    echo "Upgrade"
    mkdir -p /var/log/%{name}
else
    echo "Install"

    %if 0%{?rhel}  == 6
    /sbin/chkconfig --list %{name} > /dev/null 2>&1 || /sbin/chkconfig --add %{name}
    /sbin/chkconfig %{name} on
    %endif

    %if 0%{?rhel}  == 7
    systemctl enable %{name}.service
    %endif

    mkdir -p /var/log/%{name}
    chown -R %{name}:%{name} /var/log/%{name}
fi

%preun
if [ $1 -eq 0 ]; then
    %if 0%{?rhel}  == 6
    /sbin/chkconfig --del %{name}
    %endif

    %if 0%{?rhel}  == 7
    systemctl disable %{name}.service
    %endif
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{__prefix}/%{name}/
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/%{name}/supervisord.conf
%config(noreplace) %{_sysconfdir}/%{name}/programs/*
%defattr(-,%{name},%{name})
/var/run/%{name}/
%if 0%{?rhel}  == 6
%{_initrddir}/%{name}
%endif
%if 0%{?rhel}  == 7
/usr/lib/systemd/system/%{name}.service
%endif