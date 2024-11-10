Name:             rspamd
Version:          3.10.2
Release:          2%{?dist}
Summary:          Rapid spam filtering system
License:          ASL 2.0 and LGPLv3 and BSD and MIT and CC0 and zlib
URL:              https://www.rspamd.com/
Source0:          https://github.com/rspamd/rspamd/archive/%{version}/%{name}-%{version}.tar.gz
Source1:          80-rspamd.preset
Source2:          rspamd.logrotate
Source3:          rspamd.sysusers
Source4:          rspamd.tmpfilesd

Patch0:           systemd-unit.patch
Patch1:           use-system-ssl-ciphers.patch

BuildRequires:    cmake
BuildRequires:    gcc-c++

BuildRequires:    file-devel
BuildRequires:    glib2-devel
%ifarch aarch64
BuildRequires:    vectorscan-devel
%else
BuildRequires:    hyperscan-devel
%endif
BuildRequires:    jemalloc-devel
BuildRequires:    lapack-devel
BuildRequires:    libevent-devel
BuildRequires:    libicu-devel
BuildRequires:    libsodium-devel
BuildRequires:    libunwind-devel
BuildRequires:    luajit-devel
BuildRequires:    openblas-devel
BuildRequires:    openssl-devel
%if 0%{?fedora} >= 41
BuildRequires:    openssl-devel-engine
%endif
BuildRequires:    pcre2-devel
BuildRequires:    ragel
BuildRequires:    sqlite-devel

BuildRequires:    fmt-devel
BuildRequires:    zlib-devel
BuildRequires:    libzstd-devel
BuildRequires:    libcurl-devel
BuildRequires:    libarchive-devel

BuildRequires:    systemd-rpm-macros

%{?systemd_requires}
%{?sysusers_requires_compat}
%ifarch aarch64
Requires:         vectorscan
%else
Requires:         hyperscan
%endif
Requires:         jemalloc
Requires:         logrotate
Requires:         openblas
Requires:         luajit
Requires:         pcre2

Requires:         fmt
Requires:         zlib
Requires:         libzstd
Requires:         libcurl
Requires:         libarchive

%description
Rspamd is a rapid, modular and lightweight spam filter. It is designed to work
with big amount of mail and can be easily extended with own filters written in
lua.

%prep
%autosetup -p1
rm -rf centos
rm -rf debian
rm -rf docker
rm -rf freebsd

%build
# NOTE: To disable tests during build, set DEBIAN_BUILD=1 option
%cmake \
%if 0%{?fedora} >= 36
  -DLINKER_NAME=/usr/bin/ld.bfd \
%endif
  -DCMAKE_BUILD_TYPE="Release" \
  -DCMAKE_C_FLAGS_RELEASE="%{optflags}" \
  -DCMAKE_CXX_FLAGS_RELEASE="%{optflags}" \
  -DCONFDIR=%{_sysconfdir}/%{name} \
  -DMANDIR=%{_mandir} \
  -DDBDIR=%{_sharedstatedir}/%{name} \
  -DRUNDIR=%{_rundir}/%{name} \
  -DLOGDIR=%{_localstatedir}/log/%{name} \
  -DSHAREDIR=%{_datadir}/%{name} \
  -DLIBDIR=%{_libdir}/%{name}/ \
  -DINCLUDEDIR=%{_includedir} \
  -DRSPAMD_GROUP=%{name} \
  -DRSPAMD_USER=%{name} \
  -DSYSTEMDDIR=%{_unitdir} \
  -DWANT_SYSTEMD_UNITS=OFF \
  -DNO_SHARED=ON \
  -DDEBIAN_BUILD=1 \
  -DENABLE_LIBUNWIND=ON \
  -DENABLE_HYPERSCAN=ON \
  -DENABLE_JEMALLOC=ON \
  -DENABLE_LUAJIT=ON \
  -DENABLE_BLAS=ON \
%if 0%{?fedora} <= 40
  -DSYSTEM_FMT=OFF \
%endif
  -DSYSTEM_ZSTD=ON \
  -DENABLE_URL_INCLUDE=ON \
  -DNO_TARGET_VERSIONS=ON

%cmake_build

%pre
%sysusers_create_compat %{SOURCE3}

%install
%cmake_install
# The tests install some files we don't want so ship
rm -f %{buildroot}%{_libdir}/debug/usr/bin/rspam*
install -Ddm 0755 %{buildroot}%{_localstatedir}/log/%{name}
install -Ddm 0755 %{buildroot}%{_rundir}/%{name}
install -Ddm 0755 %{buildroot}%{_sysconfdir}/%{name}/{local,override}.d/
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_presetdir}/80-rspamd.preset
install -Dpm 0644 rspamd.service %{buildroot}%{_unitdir}/rspamd.service
install -Dpm 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/rspamd
install -Dpm 0644 %{SOURCE3} %{buildroot}%{_sysusersdir}/%{name}.conf
install -Dpm 0644 %{SOURCE4} %{buildroot}%{_tmpfilesdir}/%{name}.conf
install -Dpm 0644 LICENSE.md %{buildroot}%{_docdir}/licenses/LICENSE.md

%post
%systemd_post rspamd.service

%preun
%systemd_preun rspamd.service

%postun
%systemd_postun_with_restart rspamd.service

%files
# TODO: Collect licenses from all bundled dependencies
%license %{_docdir}/licenses/LICENSE.md

%{_bindir}/rspam{adm,c,d}
%{_bindir}/rspamd_stats

%dir %{_datadir}/%{name}
%{_datadir}/%{name}/effective_tld_names.dat
%dir %{_datadir}/%{name}/{elastic,languages}
%{_datadir}/%{name}/{elastic,languages}/*.json
%{_datadir}/%{name}/languages/stop_words
%dir %{_datadir}/%{name}/{lualib,plugins,rules}
%{_datadir}/%{name}/{lualib,plugins,rules}/*.lua
%dir %{_datadir}/%{name}/lualib/*
%{_datadir}/%{name}/lualib/*/*.lua
%dir %{_datadir}/%{name}/rules/{controller,regexp}
%{_datadir}/%{name}/rules/{controller,regexp}/*.lua
%dir %{_datadir}/%{name}/www
%{_datadir}/%{name}/www/*

%dir %{_libdir}/%{name}
%{_libdir}/%{name}/*

%{_unitdir}/%{name}.service
%{_presetdir}/80-rspamd.preset

%{_mandir}/man8/rspamd.*
%{_mandir}/man1/rspamc.*
%{_mandir}/man1/rspamadm.*

%config(noreplace) %{_sysconfdir}/logrotate.d/rspamd

%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/*.{inc,conf}
%dir %{_sysconfdir}/%{name}/{local,maps,modules,override,scores}.d
%config(noreplace) %{_sysconfdir}/%{name}/{local,maps,modules,override,scores}.d/*

%dir %attr(0750,%{name},%{name}) %{_rundir}/%{name}
%dir %attr(0750,%{name},%{name}) %{_localstatedir}/log/%{name}

%{_sysusersdir}/%{name}.conf
%{_tmpfilesdir}/%{name}.conf

