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
cp -r %{source} %{name}/src
rm -rf %{name}/src/.git*
rm -rf %{name}/src/rpmtools/.git*
if [ -d %{name}/src/sso_client/ ]; then
    rm -rf %{name}/src/sso_client/.git*
fi
rm -rf %{name}/src/.idea*

[ ! -f %{name}/src/wsgi.py ] && cp %{name}/src/rpmtools/wsgi.py %{name}/src/wsgi.py

if [ -d %{source}/env ]; then
    virtualenv --relocatable %{source}/env
    cp -r %{source}/env %{name}/env 
else
    virtualenv --distribute %{name}/env
    %{name}/env/bin/easy_install -U distribute
    %{name}/env/bin/pip install -r %{name}/src/requirements.txt --upgrade
    virtualenv --relocatable %{name}/env
fi

#if [ -d %{source}/../static ]; then
#    cp -r %{source}/../static %{name}/static
#fi

%{name}/env/bin/python %{source}/manage.py collectstatic --noinput
mv -f %{source}/collected_static %{name}/static

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
%{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/src/rpmtools/gunicorn.initd.sh %{buildroot}%{_initrddir}/%{name}-gunicorn
sed -i 's/PROJECT_NAME/%{name}/g' %{buildroot}%{_initrddir}/%{name}-gunicorn
%{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/src/rpmtools/celeryd.initd.sh %{buildroot}%{_initrddir}/%{name}-celeryd
sed -i 's/PROJECT_NAME/%{name}/g' %{buildroot}%{_initrddir}/%{name}-celeryd
%{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/src/rpmtools/celeryd_without_beat.initd.sh %{buildroot}%{_initrddir}/%{name}-celeryd_without_beat
sed -i 's/PROJECT_NAME/%{name}/g' %{buildroot}%{_initrddir}/%{name}-celeryd_without_beat
%{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/src/rpmtools/celerycam.initd.sh %{buildroot}%{_initrddir}/%{name}-celerycam
sed -i 's/PROJECT_NAME/%{name}/g' %{buildroot}%{_initrddir}/%{name}-celerycam

rm -f %{buildroot}%{__prefix}/%{name}/src/rpmtools/*.initd.sh


# configs
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
%{__install} -p -D -m 0644 %{buildroot}%{__prefix}/%{name}/src/default.conf %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
%{__install} -p -D -m 0644 %{buildroot}%{__prefix}/%{name}/src/rpmtools/gunicorn.conf %{buildroot}%{_sysconfdir}/%{name}/gunicorn.conf
sed -i 's/PROJECT_NAME/%{name}/g' %{buildroot}%{_sysconfdir}/%{name}/gunicorn.conf
rm -rf %{buildroot}%{__prefix}/%{name}/src/rpmtools/gunicorn.conf
rm -rf %{buildroot}%{__prefix}/%{name}/src/default.conf

# bin
mkdir -p %{buildroot}%{_bindir}
ln -s %{__prefix}/%{name}/src/rpmtools/manage.sh %{buildroot}%{_bindir}/%{name}

rm -rf %{buildroot}%{__prefix}/%{name}/src/local_settings.py

mkdir -p %{buildroot}/var/log/%{name}
mkdir -p %{buildroot}/var/run/%{name}
mkdir -p %{buildroot}%{__prefix}/%{name}/media/

%post

chmod +x /usr/bin/%{name}

if [ $1 -gt 1 ]; then
    echo "Upgrade"

    # DB
    if %{name} > /dev/null 2>&1; then
        %{name} syncdb --migrate --noinput

        service %{name}-gunicorn restart
        service %{name}-celeryd restart_if_running
        service %{name}-celeryd_without_beat restart_if_running
        service %{name}-celerycam restart_if_running
    fi
else
    echo "Install"

    /sbin/chkconfig --list %{name}-gunicorn > /dev/null 2>&1 || /sbin/chkconfig --add %{name}-gunicorn
    /sbin/chkconfig --list %{name}-celeryd > /dev/null 2>&1 || /sbin/chkconfig --add %{name}-celeryd
    /sbin/chkconfig --list %{name}-celeryd_without_beat > /dev/null 2>&1 || /sbin/chkconfig --add %{name}-celeryd_without_beat
    /sbin/chkconfig --list %{name}-celerycam > /dev/null 2>&1 || /sbin/chkconfig --add %{name}-celerycam

    # logs
    mkdir -p /var/log/%{name}

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

/var/log/%{name}/
/var/run/%{name}/
%{__prefix}/%{name}/media/