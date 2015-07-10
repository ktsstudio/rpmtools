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
%{name} built with generic yii project spec

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
cp -rf %{source} %{name}/ || true
cd %{name}

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
    grunt || exit 1
fi

%install
mkdir -p %{buildroot}%{__prefix}/%{name}

files=$(%{meta} files --keys)
for file in $files; do
    file_escape=$(echo $file | sed 's/\./\\./g')
    dest=$(%{meta} "files.${file_escape}")
    mv "%{name}/$file" "%{buildroot}%{__prefix}/%{name}/$dest"
done
echo %{version} > %{buildroot}%{__prefix}/%{name}/version.txt

%post
mkdir -p /var/log/%{name}
mkdir -p /var/lib/%{name}/runtime
#temp fix
chmod -R 777 /var/log/%{name}
chmod -R 777 /var/lib/%{name}/runtime
chown -R %{name}:%{name} /var/log/%{name}
chown -R %{name}:%{name} /var/lib/%{name}/runtime

%preun

%clean
rm -rf %{buildroot}

%files
%defattr(-,root:%{name}{__prefix}/%{name}