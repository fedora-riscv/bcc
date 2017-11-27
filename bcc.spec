# luajit is not available for some architectures
%ifarch ppc64 ppc64le
%bcond_with lua
%else
%bcond_without lua
%endif

Name:           bcc
Version:        0.4.0
Release:        2%{?dist}
Summary:        BPF Compiler Collection (BCC)
License:        ASL 2.0
URL:            https://github.com/iovisor/bcc
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
# https://github.com/iovisor/bcc/pull/1426
Patch0:         0001-set-SOVERSION-for-bpf-shared.patch

# Arches will be included as upstream support is added and dependencies are
# satisfied in the respective arches
ExclusiveArch:  x86_64 %{power64}

BuildRequires:  bison, cmake >= 2.8.7, flex, libxml2-devel
BuildRequires:  python3-devel
BuildRequires:  elfutils-libelf-devel
BuildRequires:  llvm-devel llvm-static clang-devel
BuildRequires:  ncurses-devel
%if %{with lua}
BuildRequires:  pkgconfig(luajit)
%endif

Requires:       %{name}-tools = %{version}-%{release}

%description
BCC is a toolkit for creating efficient kernel tracing and manipulation
programs, and includes several useful tools and examples. It makes use of
extended BPF (Berkeley Packet Filters), formally known as eBPF, a new feature
that was first added to Linux 3.15. BCC makes BPF programs easier to write,
with kernel instrumentation in C (and includes a C wrapper around LLVM), and
front-ends in Python and lua. It is suited for many tasks, including
performance analysis and network traffic control.


%package devel
Summary:        Shared library for BPF Compiler Collection (BCC)
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and header files for developing
application that use BPF Compiler Collection (BCC).


%package doc
Summary:        Examples for BPF Compiler Collection (BCC)
Recommends:     python3-%{name} = %{version}-%{release}
Recommends:     %{name}-lua = %{version}-%{release}
BuildArch:      noarch

%description doc
Examples for BPF Compiler Collection (BCC)


%package -n python3-%{name}
Summary:        Python3 bindings for BPF Compiler Collection (BCC)
Requires:       %{name}%{?_isa} = %{version}-%{release}
%{?python_provide:%python_provide python3-%{srcname}}

%description -n python3-%{name}
Python3 bindings for BPF Compiler Collection (BCC)


%if %{with lua}
%package lua
Summary:        Standalone tool to run BCC tracers written in Lua
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description lua
Standalone tool to run BCC tracers written in Lua
%endif


%package tools
Summary:        Command line tools for BPF Compiler Collection (BCC)
Requires:       python3-%{name} = %{version}-%{release}
Requires:       python3-netaddr
Requires:       kernel-devel
BuildArch:      noarch

%description tools
Command line tools for BPF Compiler Collection (BCC)


%prep
%autosetup -p1


%build
%cmake . \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo \
        -DREVISION_LAST=%{version} -DREVISION=%{version} -DPYTHON_CMD=python3
%make_build


%install
%make_install

# Fix python shebangs
for i in `find %{buildroot}%{_datadir}/%{name}/tools/ -type f`; do
  sed -i '1s=^#!/usr/bin/\(python\|env python\)[0-9.]*=#!%{__python3}=' $i
done

for i in `find %{buildroot}%{_datadir}/%{name}/examples/ -type f`; do
  sed -i '1s=^#!/usr/bin/\(python\|env python\)[0-9.]*=#!%{__python3}=' $i
  sed -i '1s=^#!/usr/bin/env bcc-lua.*=#!/usr/bin/bcc-lua=' $i
done

# Move man pages to the right location
mkdir -p %{buildroot}%{_mandir}
mv %{buildroot}%{_datadir}/%{name}/man/* %{buildroot}%{_mandir}/
# Avoid conflict with other manpages
# https://bugzilla.redhat.com/show_bug.cgi?id=1517408
for i in `find %{buildroot}%{_mandir} -name "*.8"`; do
  tname=$(basename $i)
  rename $tname %{name}-$tname $i
done
mkdir -p %{buildroot}%{_docdir}/%{name}
mv %{buildroot}%{_datadir}/%{name}/examples %{buildroot}%{_docdir}/%{name}/

# We cannot run the test suit since it requires root and it makes changes to
# the machine (e.g, IP address)
#%check

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%doc README.md
%license LICENSE.txt COPYRIGHT.txt
%{_libdir}/lib%{name}.so.*
%{_libdir}/libbpf.so.*

%files devel
%{_libdir}/lib%{name}.so
%{_libdir}/libbpf.so
%{_libdir}/pkgconfig/lib%{name}.pc
%{_includedir}/%{name}/

%files -n python3-%{name}
%{python3_sitelib}/%{name}*

%files doc
%dir %{_docdir}/%{name}
%doc %{_docdir}/%{name}/examples/

%files tools
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/tools
%{_datadir}/%{name}/tools/*
%exclude %{_datadir}/%{name}/tools/old/
%{_mandir}/man8/*

%if %{with lua}
%files lua
%{_bindir}/bcc-lua
%endif


%changelog
* Mon Nov 27 2017 Rafael Santos <rdossant@redhat.com> - 0.4.0-2
- Resolves #1517408 - avoid conflict with other manpages

* Wed Nov 01 2017 Rafael Fonseca <rdossant@redhat.com> - 0.4.0-1
- Resolves #1460482 - rebase to new release
- Resolves #1505506 - add support for LLVM 5.0
- Resolves #1460482 - BPF module compilation issue
- Partially address #1479990 - location of man pages
- Enable ppc64(le) support without lua
- Soname versioning for libbpf by ignatenkobrain

* Thu Mar 30 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.3.0-2
- Rebuild for LLVM4
- Trivial fixes in spec

* Fri Mar 10 2017 Rafael Fonseca <rdossant@redhat.com> - 0.3.0-1
- Rebase to new release.

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jan 10 2017 Rafael Fonseca <rdossant@redhat.com> - 0.2.0-2
- Fix typo

* Tue Nov 29 2016 Rafael Fonseca <rdossant@redhat.com> - 0.2.0-1
- Initial import
