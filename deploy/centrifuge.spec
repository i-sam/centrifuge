%define __prefix /opt
%define __spec_install_post /usr/lib/rpm/brp-compress || :
%define __descr "Simple real-time messaging server"

Name: centrifuge
Summary: %{__descr}
Version: %{version}
Release: %{release}
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildRequires: python rpm-build redhat-rpm-config zeromq3-devel postgresql-devel
Requires: python supervisor zeromq3
License: BSD


%description
%{__descr}


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
rm -rf %{name}/src/.idea*

virtualenv --distribute %{name}/env
%{name}/env/bin/easy_install -U distribute
%{name}/env/bin/pip install -r %{name}/src/src/requirements.txt --upgrade
virtualenv --relocatable %{name}/env

# remove pyc
find %{name}/ -type f -name "*.py[co]" -delete

# replace builddir path
find %{name}/ -type f -exec sed -i "s:%{_builddir}:%{__prefix}:" {} \;


%install
mkdir -p %{buildroot}%{__prefix}/%{name}
mv %{name} %{buildroot}%{__prefix}/

# hack for lib64
[ -d %{buildroot}%{__prefix}/%{name}/env/lib64 ] && rm -rf %{buildroot}%{__prefix}/%{name}/env/lib64 && ln -sf %{__prefix}/%{name}/env/lib %{buildroot}%{__prefix}/%{name}/env/lib64

# init.d files
%{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/src/deploy/%{name}.initd.sh %{buildroot}%{_initrddir}/%{name}

# configs
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
%{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/src/src/config.json %{buildroot}%{_sysconfdir}/%{name}/centrifuge.json

# supervisor config
%{__install} -p -D -m 0755 %{buildroot}%{__prefix}/%{name}/src/deploy/centrifuge.conf %{buildroot}%{_sysconfdir}/supervisor/conf.d/centrifuge.conf

mkdir -p %{buildroot}/var/log/%{name}
mkdir -p %{buildroot}/var/run/%{name}
mkdir -p %{buildroot}/var/db/%{name}

%post

if [ $1 -gt 1 ]; then
    echo "Upgraded"
else
    echo "Installed"
    echo "1. Fill Supervisor config file for Centrifuge"
    echo "2. Fill Centrifuge's json config file"
    echo "3. Run Centrifuge"
fi


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root)
%{__prefix}/%{name}/
%{_initrddir}/%{name}/
%config(noreplace) %{_sysconfdir}/%{name}/centrifuge.json
%config(noreplace) %{_sysconfdir}/supervisor/conf.d/centrifuge.conf

%defattr(-,%{name},%{name})
/var/log/%{name}/
/var/run/%{name}/
/var/db/%{name}/