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
%{name} built with generic python project spec

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

REQUIREMENTS=$(%{meta} requirementsPath)
if [ "${REQUIREMENTS}" == '' ]; then
    REQUIREMENTS="%{name}/src/requirements.txt"
else
    REQUIREMENTS="%{name}/src/${REQUIREMENTS}"
fi

if [ -f "${REQUIREMENTS}" ]; then
    REQUIREMENTS_CONTENT=$(cat ${REQUIREMENTS})
    REQUIREMENTS_CONTENT_COMMAND=$(%{meta} requirementsContentCommand)
    if [ "${REQUIREMENTS_CONTENT_COMMAND}" != "" ]; then
        pushd %{name}/src
            REQUIREMENTS_CONTENT=$(bash -c "${REQUIREMENTS_CONTENT_COMMAND}")
        popd
    fi

    HASH=$(echo "${REQUIREMENTS_CONTENT}%{virtualenv}" | md5sum | awk '{ print $1 }')
    CACHED_VIRTUALENV="/tmp/virtualenv_${HASH}.tar"
    if [ -e "${CACHED_VIRTUALENV}" ]
    then
      echo "Found cached virtualenv: ${CACHED_VIRTUALENV}, use it"
      tar xf ${CACHED_VIRTUALENV} %{name}
    else
      echo "No found cached virtualenv, download..."

      %{virtualenv} %{name}/env

      %{name}/env/bin/pip install -U pip setuptools
      %{name}/env/bin/pip install -r ${REQUIREMENTS} --upgrade

      %{virtualenv} --relocatable %{name}/env

      echo "Save virtualenv into cache: ${CACHED_VIRTUALENV}"
      tar cf ${CACHED_VIRTUALENV} %{name}/env || true
    fi
else
    echo 'Not found requirements, skipped...'
fi

pushd %{name}/src
    gruntCwd=$(%{meta} gruntCwd)
    if [ "${gruntCwd}" != '' ]
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
          yarn=$(which yarn 2>/dev/null || true)
          if [ "${yarn}" != "" ]; then
            ${yarn} || exit 1
          else
            npm install || exit 1
          fi
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
        grunt $(%{meta} gruntTask) || exit 1
    fi
popd

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

find %{name}/ -type f -name "*.py[co]" -delete
find %{name}/ -type f -exec sed -i "s:%{_builddir}:%{__prefix}:" {} \;

%install
mkdir -p %{buildroot}%{__prefix}/%{name}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}/var/run/%{name}

mv %{name} %{buildroot}%{__prefix}/

[ -d %{buildroot}%{__prefix}/%{name}/env/lib64 ] && rm -rf %{buildroot}%{__prefix}/%{name}/env/lib64 && ln -sf %{__prefix}/%{name}/env/lib %{buildroot}%{__prefix}/%{name}/env/lib64

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

# templates
if [ "$(%{meta} template)" == 'supervisor' ]; then
    mkdir -p %{buildroot}%{_sysconfdir}/%{name}/programs

    if [ -e %{buildroot}%{__prefix}/%{name}/src/build/default.conf ]; then
        %{__install} -p -D -m 0644 %{buildroot}%{__prefix}/%{name}/src/build/default.conf %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
    else
        touch %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
    fi

    %{__install} -p -D -m 0644 %{buildroot}%{__prefix}/%{name}/src/rpmtools/python/templates/supervisor/configs/supervisord.conf %{buildroot}%{_sysconfdir}/%{name}/supervisord.conf
    sed -i 's/#NAME#/%{name}/g' %{buildroot}%{_sysconfdir}/%{name}/supervisord.conf

    if [ -d %{buildroot}%{__prefix}/%{name}/src/build/programs ]; then
        %{__install} -p -D -m 0644 --target-directory=%{buildroot}%{_sysconfdir}/%{name}/programs %{buildroot}%{__prefix}/%{name}/src/build/programs/*
    else
        %{__install} -p -D -m 0644 %{buildroot}%{__prefix}/%{name}/src/rpmtools/python/templates/supervisor/configs/program.conf %{buildroot}%{_sysconfdir}/%{name}/programs/%{name}.conf
        sed -i 's/#NAME#/%{name}/g' %{buildroot}%{_sysconfdir}/%{name}/programs/%{name}.conf
    fi

    %if 0%{?rhel} == 6
        %{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/src/rpmtools/python/templates/supervisor/init/c6/main.init.sh %{buildroot}%{_initrddir}/%{name}
        sed -i 's/#NAME#/%{name}/g' %{buildroot}%{_initrddir}/%{name}
    %endif

    %if 0%{?rhel} == 7
        %{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/src/rpmtools/python/templates/supervisor/init/c7/systemd %{buildroot}/usr/lib/systemd/system/%{name}.service
        sed -i 's/#NAME#/%{name}/g' %{buildroot}/usr/lib/systemd/system/%{name}.service
    %endif
fi

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


%post
if [ $1 -gt 1 ]; then
    echo "Upgrade"
    mkdir -p /var/log/%{name}

    find %{__prefix}/%{name} -type f -name "*.py[co]" -delete

    %if 0%{?rhel}  == 7
    /bin/systemctl daemon-reload
    %endif
else
    echo "Install"

    %if 0%{?rhel}  == 6
    /sbin/chkconfig --list %{name} > /dev/null 2>&1 || /sbin/chkconfig --add %{name}
    /sbin/chkconfig %{name} on
    %endif

    %if 0%{?rhel}  == 7
    if [ -e /usr/lib/systemd/system/%{name}.service ]; then
        systemctl enable %{name}.service
    fi
    %endif

    mkdir -p /var/log/%{name}
    chown -R %{name}:%{name} /var/log/%{name}
fi

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