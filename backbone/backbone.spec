%define __prefix /opt
%define __spec_install_post /usr/lib/rpm/brp-compress || :

Name: %{name}
Summary: %{summary}
Version: %{version}
Release: %{release}
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildRequires: python-argparse
License: proprietary
Group: Apps/sys
Autoreq: 0


%description
%{name} built with generic backbone project spec

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

if [ -e "package.json" ]
then
    npm install || exit 1
fi

if [ -e "bower.json" ]
then
    bower install --allow-root || exit 1
fi

if [ -e "Gruntfile.js" ]
then
    grunt %{grunttask} || exit 1
fi

cp -rf %{source}/public/* %{name}/


%install
mkdir -p %{buildroot}%{__prefix}/
mv %{name} %{buildroot}%{__prefix}/


%post

%preun

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{__prefix}/%{name}