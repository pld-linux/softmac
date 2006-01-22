#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
%ifarch sparc
%undefine	with_smp
%endif
#
%define		_snap	20060120
%define		_rel	0.%{_snap}.1
Summary:	Layer intended to be a software MAC layer
Name:		softmac
Version:	0.1
Release:	%{_rel}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://softmac.sipsolutions.net/%{name}-snapshot.tar.bz2
# Source0-md5:	4f9f11bd0648c1739e74b090f7516627
URL:		http://softmac.sipsolutions.net/
Patch0:		%{name}-local_headers.patch
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.217
%endif
BuildRequires:	sed >= 4.0
Requires(post,postun):	/sbin/depmod
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The ieee80211 softmac layer is intended to be a software MAC layer
complementing ieee80211 layer in Linux with protocol management
features that a lot of hardware no longer does but instead hands off
to software. It is intended to handle scanning, assocation and similar
tasks.

%package devel
Summary:	Kernel headers
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel

%description devel
SoftMAC kernel headers.

%package -n kernel-net-softmac
Summary:	Layer intended to be a software MAC layer
Summary(pl):	***
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel-net-softmac
The ieee80211 softmac layer is intended to be a software MAC layer
complementing ieee80211 layer in Linux with protocol management
features that a lot of hardware no longer does but instead hands off
to software. It is intended to handle scanning, assocation and similar
tasks.

%package -n kernel-smp-net-softmac
Summary:	Broadcom BCM4400 driver for Linux SMP
Summary(pl):	Sterownik do karty Broadcom BCM4400 dla Linuksa SMP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel-smp-net-softmac
The ieee80211 softmac layer is intended to be a software MAC layer
complementing ieee80211 layer in Linux with protocol management
features that a lot of hardware no longer does but instead hands off
to software. It is intended to handle scanning, assocation and similar
tasks.

%prep
%setup -q -n %{name}-snapshot
%patch0 -p1
sed 's/$(CONFIG_[A-Za-z0-9_]*)/m/' 	\
	-i net/ieee80211/Makefile	\
	-i net/ieee80211/softmac/Makefile
cp -rf include/net net/ieee80211/
cp -rf include/net net/ieee80211/softmac/

%build
cd net/ieee80211


%if %{with kernel}
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
%ifarch ppc ppc64
	install -d include/asm
	[ ! -d %{_kernelsrcdir}/include/asm-powerpc ] || ln -sf %{_kernelsrcdir}/include/asm-powerpc/* include/asm
	[ ! -d %{_kernelsrcdir}/include/asm-%{_target_base_arch} ] || ln -snf %{_kernelsrcdir}/include/asm-%{_target_base_arch}/* include/asm
%else
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
%endif

	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
	touch include/config/MARKER

	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}

	for MOD in ieee80211_crypt_ccmp ieee80211_crypt_tkip \
			ieee80211 ieee80211_crypt ieee80211_crypt_wep \
			softmac/ieee80211softmac; do
		mv $MOD.ko $MOD-$cfg.ko
	done
done
%endif

%install
rm -rf $RPM_BUILD_ROOT
cd net/ieee80211

%if %{with kernel}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/%{_kernel_ver}{,smp}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/net/sm_ieee80211

for MOD in ieee80211 ieee80211_crypt ieee80211_crypt_wep	\
		ieee80211_crypt_ccmp ieee80211_crypt_tkip; do
	install $MOD-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
		$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/sm_ieee80211/sm_$MOD.ko
	echo "alias $MOD sm_$MOD" \
		>> $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/%{_kernel_ver}/softmac.conf
done
install softmac/ieee80211softmac-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/sm_ieee80211/ieee80211softmac.ko

%if %{with smp} && %{with dist_kernel}
for MOD in ieee80211 ieee80211_crypt ieee80211_crypt_wep	\
		ieee80211_crypt_ccmp ieee80211_crypt_tkip; do
	install $MOD-smp.ko \
		$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/net/sm_ieee80211/sm_$MOD.ko
	echo "alias $MOD sm_$MOD" \
		>> $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/%{_kernel_ver}smp/softmac.conf
done
install softmac/ieee80211softmac-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/net/sm_ieee80211/ieee80211softmac.ko
%endif
%endif

install -d $RPM_BUILD_ROOT%{_includedir}/linux/softmac
cp -a net $RPM_BUILD_ROOT%{_includedir}/linux/softmac

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel-net-softmac
%depmod %{_kernel_ver}

%postun	-n kernel-net-softmac
%depmod %{_kernel_ver}

%post	-n kernel-smp-net-softmac
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-net-softmac
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files devel
%defattr(644,root,root,755)
%{_includedir}/linux/softmac
%endif

%if %{with kernel}
%files -n kernel-net-softmac
%defattr(644,root,root,755)
%dir /lib/modules/%{_kernel_ver}/kernel/net/sm_ieee80211
/lib/modules/%{_kernel_ver}/kernel/net/sm_ieee80211/*.ko*
%{_sysconfdir}/modprobe.d/%{_kernel_ver}/softmac.conf

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-net-softmac
%defattr(644,root,root,755)
%dir /lib/modules/%{_kernel_ver}smp/kernel/net/sm_ieee80211
/lib/modules/%{_kernel_ver}smp/kernel/net/sm_ieee80211/*.ko*
%{_sysconfdir}/modprobe.d/%{_kernel_ver}smp/softmac.conf
%endif
%endif
