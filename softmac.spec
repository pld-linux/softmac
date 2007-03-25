#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
%define		_snap	20060319
%define		_rel	0.%{_snap}.1
Summary:	Layer intended to be a software MAC layer
Summary(pl.UTF-8):	Warstwa mająca być programową warstwą MAC
Name:		softmac
Version:	0.1
Release:	%{_rel}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://softmac.sipsolutions.net/%{name}-snapshot.tar.bz2
# Source0-md5:	6731ffb088fe9dc42a17737b69892a34
URL:		http://softmac.sipsolutions.net/
Patch0:		%{name}-local_headers.patch
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
BuildRequires:	sed >= 4.0
Requires(post,postun):	/sbin/depmod
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define	ieeemod	ieee80211,ieee80211_crypt{,_ccmp,_tkip,_wep}

%description
The ieee80211 softmac layer is intended to be a software MAC layer
complementing ieee80211 layer in Linux with protocol management
features that a lot of hardware no longer does but instead hands off
to software. It is intended to handle scanning, association and
similar tasks.

%description -l pl.UTF-8
softmac ma być programową warstwą MAC zgodną z warstwą ieee80211 w
Linuksie z opcjami zarządzania protokołem, których znaczna część
sprzętu już nie obsługuje, ale pozostawia oprogramowaniu. Ma
obsługiwać skanowanie, kojarzenie i podobne zadania.

%package devel
Summary:	Kernel headers
Summary(pl.UTF-8):	Pliki nagłówkowe jądra
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel

%description devel
SoftMAC kernel headers.

%description devel -l pl.UTF-8
Pliki nagłówkowe jądra SoftMAC

%package -n kernel%{_alt_kernel}-net-softmac
Summary:	Software MAC layer - Linux kernel drivers
Summary(pl.UTF-8):	Programowa warstwa MAC - sterowniki jądra Linuksa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif

%description -n kernel%{_alt_kernel}-net-softmac
The ieee80211 softmac layer is intended to be a software MAC layer
complementing ieee80211 layer in Linux with protocol management
features that a lot of hardware no longer does but instead hands off
to software. It is intended to handle scanning, assocation and similar
tasks.

This package contains Linux kernel drivers.

%description -n kernel%{_alt_kernel}-net-softmac -l pl.UTF-8
softmac ma być programową warstwą MAC zgodną z warstwą ieee80211 w
Linuksie z opcjami zarządzania protokołem, których znaczna część
sprzętu już nie obsługuje, ale pozostawia oprogramowaniu. Ma
obsługiwać skanowanie, kojarzenie i podobne zadania.

Ten pakiet zawiera sterowniki jądra Linuksa.

%prep
%setup -q -n %{name}-snapshot
%patch0 -p1
sed 's/$(CONFIG_[A-Za-z0-9_]*)/m/' 	\
	-i net/ieee80211/Makefile	\
	-i net/ieee80211/softmac/Makefile
cp -rf include/net net/ieee80211
cp -rf include/net net/ieee80211/softmac

%build
%if %{with kernel}
%build_kernel_modules -m %{ieeemod},softmac/ieee80211softmac -C net/ieee80211
%endif

%install
rm -rf $RPM_BUILD_ROOT
cd net/ieee80211

%if %{with kernel}
%install_kernel_modules -s %{name} -n %{name} -m %{ieeemod} -d kernel/net/ieee80211-%{name}
%install_kernel_modules -m softmac/ieee80211softmac -d kernel/net/ieee80211-%{name}/%{name}
%endif

install -d $RPM_BUILD_ROOT%{_includedir}/linux/softmac
cp -a net $RPM_BUILD_ROOT%{_includedir}/linux/softmac

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-net-softmac
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-net-softmac
%depmod %{_kernel_ver}

%if %{with userspace}
%files devel
%defattr(644,root,root,755)
%{_includedir}/linux/softmac
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-net-softmac
%defattr(644,root,root,755)
%dir /lib/modules/%{_kernel_ver}/kernel/net/ieee80211-%{name}
/lib/modules/%{_kernel_ver}/kernel/net/ieee80211-%{name}/*.ko*
%dir /lib/modules/%{_kernel_ver}/kernel/net/ieee80211-%{name}/%{name}
/lib/modules/%{_kernel_ver}/kernel/net/ieee80211-%{name}/%{name}/ieee80211softmac.ko*
%{_sysconfdir}/modprobe.d/%{_kernel_ver}/%{name}.conf
%endif
