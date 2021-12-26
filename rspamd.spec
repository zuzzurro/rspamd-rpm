Name:             rspamd
Version:          3.1
Release:          1%{?dist}
Summary:          Rapid spam filtering system
License:          ASL 2.0 and LGPLv3 and BSD and MIT and CC0 and zlib
URL:              https://www.rspamd.com/
Source0:          https://github.com/%{name}/%{name}/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:          80-rspamd.preset
Source2:          rspamd.logrotate
Source3:          rspamd.sysusers

Patch0:           rspamd-secure-ssl-ciphers.patch
Patch1:           systemd-unit-modify.patch

BuildRequires:    gcc-c++
BuildRequires:    cmake
BuildRequires:    file-devel
BuildRequires:    glib2-devel
BuildRequires:    hyperscan-devel
BuildRequires:    jemalloc-devel
BuildRequires:    libaio-devel
BuildRequires:    libcurl-devel
BuildRequires:    libicu-devel
BuildRequires:    libnsl2-devel
BuildRequires:    libsodium-devel
BuildRequires:    libunwind-devel
BuildRequires:    luajit-devel
BuildRequires:    openssl-devel
BuildRequires:    pcre2-devel
BuildRequires:    perl
BuildRequires:    perl-Digest-MD5
BuildRequires:    ragel
BuildRequires:    systemd-rpm-macros
BuildRequires:    sqlite-devel
BuildRequires:    fmt-devel
%{?systemd_requires}
Requires:         logrotate
Requires:         hyperscan
Requires:         jemalloc
Requires:         luajit
Requires:         fmt


%description
Rspamd is a rapid, modular and lightweight spam filter. It is designed to work
with big amount of mail and can be easily extended with own filters written in
lua.

%prep
%autosetup -p1

%build
# NOTE: To disable tests during build, set DEBIAN_BUILD=1 option
%cmake \
  -DCONFDIR=%{_sysconfdir}/%{name} \
  -DMANDIR=%{_mandir} \
  -DDBDIR=%{_sharedstatedir}/%{name} \
  -DRUNDIR=%{_localstatedir}/run/%{name} \
  -DLOGDIR=%{_localstatedir}/log/%{name} \
  -DSHAREDIR=%{_datadir}/%{name} \
  -DLIBDIR=%{_libdir}/%{name}/ \
  -DSYSTEMDDIR=%{_unitdir} \
  -DENABLE_LUAJIT=ON \
  -DENABLE_HYPERSCAN=ON \
  -DENABLE_JEMALLOC=ON \
  -DENABLE_LIBUNWIND=ON \
  -DSYSTEM_FMT=ON \
  -DRSPAMD_USER=%{name} \
  -DRSPAMD_GROUP=%{name}

%cmake_build

%pre
%sysusers_create_package %{name} %{SOURCE3}

%install
%cmake_install
rm -f %{buildroot}%{_libdir}/debug/usr/bin/rspam*

install -Dpm 0644 LICENSE.md %{buildroot}%{_docdir}/licenses/LICENSE.md
install -Ddpm 0755 %{buildroot}%{_sysconfdir}/%{name}/{local,override}.d/
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_presetdir}/80-rspamd.preset
install -Dpm 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/rspamd
install -Dpm 0644 %{SOURCE3} %{buildroot}%{_sysusersdir}/%{name}.conf
install -Dpm 0644 rspamd.service %{buildroot}%{_unitdir}/rspamd.service

%post
%systemd_post rspamd.service

%preun
%systemd_preun rspamd.service

%postun
%systemd_postun_with_restart rspamd.service

%files
# TODO: Collect licenses from all bundled dependencies
%license %{_docdir}/licenses/LICENSE.md
%{_bindir}/rspam{adm,c,d}{,-%{version}}
%{_bindir}/rspamd_stats

%dir %{_datadir}/%{name}
%{_datadir}/%{name}/effective_tld_names.dat

%dir %{_datadir}/%{name}/{elastic,languages}
%{_datadir}/%{name}/{elastic,languages}/*.json
%{_datadir}/%{name}/languages/stop_words

%dir %{_datadir}/%{name}/{lualib,plugins,rules}
%{_datadir}/%{name}/{lualib,plugins,rules}/*.lua

%dir %{_datadir}/%{name}/lualib/{lua_content,lua_ffi,lua_magic,lua_scanners,lua_selectors,plugins,rspamadm}
%{_datadir}/%{name}/lualib/{lua_content,lua_ffi,lua_magic,lua_scanners,lua_selectors,plugins,rspamadm}/*.lua

%dir %{_datadir}/%{name}/rules/{controller,regexp}
%{_datadir}/%{name}/rules/{controller,regexp}/*.lua

%dir %{_datadir}/%{name}/www
%{_datadir}/%{name}/www/*

%dir %{_libdir}/%{name}
%{_libdir}/%{name}/*
%{_presetdir}/80-rspamd.preset
%{_mandir}/man1/rspamadm.*
%{_mandir}/man1/rspamc.*
%{_mandir}/man8/rspamd.*
%config(noreplace) %{_sysconfdir}/logrotate.d/rspamd
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/maps.d
%config(noreplace) %{_sysconfdir}/%{name}/*.conf
%config(noreplace) %{_sysconfdir}/%{name}/*.inc
%config(noreplace) %{_sysconfdir}/%{name}/maps.d/*.inc
%dir %{_sysconfdir}/%{name}/{local,modules,override,scores}.d
%config(noreplace) %{_sysconfdir}/%{name}/{modules,scores}.d/*
%{_unitdir}/%{name}.service
%{_sysusersdir}/%{name}.conf
