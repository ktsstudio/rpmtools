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

%{virtualenv} --distribute %{name}/env
%{name}/env/bin/easy_install -U distribute
%{name}/env/bin/pip install -r %{name}/src/requirements.txt --upgrade
%{virtualenv} --relocatable %{name}/env

find %{name}/ -type f -name "*.py[co]" -delete
find %{name}/ -type f -exec sed -i "s:%{_builddir}:%{__prefix}:" {} \;

%install
mkdir -p %{buildroot}%{__prefix}/%{name}
mv %{name} %{buildroot}%{__prefix}/

# hack for lib64
[ -d %{buildroot}%{__prefix}/%{name}/env/lib64 ] && rm -rf %{buildroot}%{__prefix}/%{name}/env/lib64 && ln -sf %{__prefix}/%{name}/env/lib %{buildroot}%{__prefix}/%{name}/env/lib64

%{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/src/rpmtools/tornado/init.d/main.init.sh %{buildroot}%{_initrddir}/%{name}

# configs
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
%{__install} -p -D -m 0644 %{buildroot}%{__prefix}/%{name}/src/build/default.conf %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
%{__install} -p -D -m 0644 %{buildroot}%{__prefix}/%{name}/src/rpmtools/tornado/conf/supervisord.conf %{buildroot}%{_sysconfdir}/%{name}/supervisord.conf
sed -i 's/#NAME#/%{name}/g' %{buildroot}%{_sysconfdir}/%{name}/supervisord.conf


rm -rf %{buildroot}%{__prefix}/%{name}/src/rpmtools
rm -rf %{buildroot}%{__prefix}/%{name}/src/env
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
fi

%preun
if [ $1 -eq 0 ]; then
    /sbin/chkconfig --del %{name}
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_initrddir}/%{name}
%{__prefix}/%{name}/
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/%{name}/supervisord.conf
%defattr(-,%{name},%{name})
/var/run/%{name}/