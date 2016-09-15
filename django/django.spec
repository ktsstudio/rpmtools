%define __prefix /opt
%define __spec_install_post /usr/lib/rpm/brp-compress || :

Name: %{name}
Summary: %{summary}
Version: %{version}
Release: %{release}
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
Requires: %{requires}
BuildRequires: %{buildrequires}
License: proprietary
Group: Apps/sys
Autoreq: 0


%description
%{name} built with generic django project spec

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

[ ! -f %{name}/src/wsgi.py ] && cp %{name}/src/rpmtools/django/wsgi.py %{name}/src/wsgi.py

HASH=$(echo "$(cat %{name}/src/requirements.txt)%{virtualenv}" | md5sum | awk '{ print $1 }')
CACHED_VIRTUALENV="/tmp/virtualenv_${HASH}.tar"
if [ -e "${CACHED_VIRTUALENV}" ]
then
  echo "Found cached virtualenv: ${CACHED_VIRTUALENV}, use it"
  tar xf ${CACHED_VIRTUALENV} %{name}
else
  echo "No found cached virtualenv, download..."

  %{virtualenv} %{name}/env
  %{name}/env/bin/pip install -U pip
  %{name}/env/bin/pip install -U setuptools

  %{name}/env/bin/pip install -r %{name}/src/requirements.txt --upgrade
  %{virtualenv} --relocatable %{name}/env

  echo "Save virtualenv into cache: ${CACHED_VIRTUALENV}"
  tar cf ${CACHED_VIRTUALENV} %{name}/env || true
fi

mkdir -p '%{source}/conf'
cp '%{source}/build/default.conf' '%{source}/conf/%{name}.conf'
pwd
pushd '%{name}/src'
    if [ -e "bower.json" ]
    then
        bower install --allow-root || exit 1
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
popd

%{name}/env/bin/python '%{name}/src/manage.py' collectstatic --noinput
pushd '%{name}/src'
    if [ -e "Gruntfile.js" ]
    then
        grunt %{grunttask} || exit 1
    fi
popd

mv -f '%{name}/src/static' %{name}/static
rm -rf '%{name}/src/core/static/bower_components'

# remove pyc
find %{name}/ -type f -name "*.py[co]" -delete

# replace builddir path
find %{name}/ -type f -exec sed -i "s:%{_builddir}:%{__prefix}:" {} \;


%install

mkdir -p %{buildroot}%{__prefix}/%{name}
mv %{name} %{buildroot}%{__prefix}/

# hack for lib64
[ -d %{buildroot}%{__prefix}/%{name}/env/lib64 ] && rm -rf %{buildroot}%{__prefix}/%{name}/env/lib64 && ln -sf %{__prefix}/%{name}/env/lib %{buildroot}%{__prefix}/%{name}/env/lib64

# init.d files for gunicorn, celeryd, celerycam
%{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/src/rpmtools/django/init.d/gunicorn.initd.sh %{buildroot}%{_initrddir}/%{name}-gunicorn
sed -i 's/PROJECT_NAME/%{name}/g' %{buildroot}%{_initrddir}/%{name}-gunicorn
sed -i 's/WSGI_APPLICATION/%{wsgi}/g' %{buildroot}%{_initrddir}/%{name}-gunicorn
%{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/src/rpmtools/django/init.d/celeryd.initd.sh %{buildroot}%{_initrddir}/%{name}-celeryd
sed -i 's/PROJECT_NAME/%{name}/g' %{buildroot}%{_initrddir}/%{name}-celeryd
%{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/src/rpmtools/django/init.d/celeryd_without_beat.initd.sh %{buildroot}%{_initrddir}/%{name}-celeryd_without_beat
sed -i 's/PROJECT_NAME/%{name}/g' %{buildroot}%{_initrddir}/%{name}-celeryd_without_beat
%{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/src/rpmtools/django/init.d/celerycam.initd.sh %{buildroot}%{_initrddir}/%{name}-celerycam
sed -i 's/PROJECT_NAME/%{name}/g' %{buildroot}%{_initrddir}/%{name}-celerycam

rm -f %{buildroot}%{__prefix}/%{name}/src/rpmtools/*.initd.sh


# configs
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
%{__install} -p -D -m 0644 %{buildroot}%{__prefix}/%{name}/src/build/default.conf %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
%{__install} -p -D -m 0644 %{buildroot}%{__prefix}/%{name}/src/rpmtools/django/conf/gunicorn.conf %{buildroot}%{_sysconfdir}/%{name}/gunicorn.conf
sed -i 's/PROJECT_NAME/%{name}/g' %{buildroot}%{_sysconfdir}/%{name}/gunicorn.conf
rm -rf %{buildroot}%{__prefix}/%{name}/src/rpmtools/gunicorn.conf
rm -rf %{buildroot}%{__prefix}/%{name}/src/build/default.conf

# bin
mkdir -p %{buildroot}%{_bindir}
ln -s %{__prefix}/%{name}/src/rpmtools/django/manage.sh %{buildroot}%{_bindir}/%{name}

rm -rf %{buildroot}%{__prefix}/%{name}/src/local_settings.py
rm -rf %{buildroot}%{__prefix}/%{name}/src/node_modules

mkdir -p %{buildroot}/var/run/%{name}
mkdir -p %{buildroot}%{__prefix}/%{name}/media/

%post
chmod +x /usr/bin/%{name}

mkdir -p /var/log/%{name}
chown %{name}:%{name} /var/log/%{name}

if [ $1 -gt 1 ]; then
    echo "Upgrade"

    # DB
    if %{name} > /dev/null 2>&1; then
        %{name} migrate
    fi
else
    echo "Install"

    /sbin/chkconfig --list %{name}-gunicorn > /dev/null 2>&1 || /sbin/chkconfig --add %{name}-gunicorn
    /sbin/chkconfig --list %{name}-celeryd > /dev/null 2>&1 || /sbin/chkconfig --add %{name}-celeryd
    /sbin/chkconfig --list %{name}-celeryd_without_beat > /dev/null 2>&1 || /sbin/chkconfig --add %{name}-celeryd_without_beat
    /sbin/chkconfig --list %{name}-celerycam > /dev/null 2>&1 || /sbin/chkconfig --add %{name}-celerycam

    # logs
    mkdir -p /var/log/%{name}
    chown -R %{name}:%{name} /var/log/%{name}

    echo "1. fill configuration files in /etc/%{name}/"
fi

%preun
if [ $1 -eq 0 ]; then
    /sbin/chkconfig --del %{name}-gunicorn
    /sbin/chkconfig --del %{name}-celeryd
    /sbin/chkconfig --del %{name}-celerycam
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_initrddir}/%{name}-gunicorn
%{_initrddir}/%{name}-celeryd
%{_initrddir}/%{name}-celeryd_without_beat
%{_initrddir}/%{name}-celerycam
%{__prefix}/%{name}/
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/%{name}/gunicorn.conf
%{_bindir}/%{name}

%defattr(-,%{name},%{name})
/var/run/%{name}/