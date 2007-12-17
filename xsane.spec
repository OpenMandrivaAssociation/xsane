%define	name	xsane
%define	version	0.995
%define	release	%mkrel 1
# Enable debug mode
%define debug 0

Name:		%name
Version:	%version
Release:	%release
Summary:	Xsane is a frontend for the SANE scanner interface
Group:		Graphics
URL:		http://www.xsane.org/
Source:		ftp://ftp.sane-project.org/pub/sane/xsane/%name-%version.tar.gz
Source1:	xsane16.png
Source2:	xsane32.png
Source3:	xsane48.png
Patch:		xsane-0.99-browser.patch
License:	GPLv2+
Requires:	libsane >= 1.0.4
# Contains "www-browser" script
Requires:	desktop-common-data
# This is for the drakxtools so that they can install a GUI for scanning
# but decide depending on the system environment which GUI actually to
# install
Provides:       scanner-gui
BuildRequires:	sane-devel gimp-devel >= 2.0 libjpeg-devel libpng-devel libusb-devel

%description
XSane is an X based interface for the SANE (Scanner Access Now Easy)
library, which provides access to scanners, digital cameras, and other
capture devices.  XSane is written in GTK+ and provides control for
performing the scan and then manipulating the captured image.

You may install xsane-gimp if you want the GIMP plug-in.

%package gimp
Summary: 	A GIMP plug-in which provides the SANE scanner interface
Group: 		Graphics
Requires: 	sane >= 1.0, %{name} >= %{version}
 
%description gimp
This package provides the regular XSane frontend for the SANE scanner
interface, but it works as a GIMP 2.0 plug-in.  You must have GIMP 2.0 (or
newer) installed to use this package.


%prep
%setup -q
%patch -p0 -b .www-browser

%build
%if %debug
export DONT_STRIP=1
CFLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`" CXXFLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`" %configure2_5x --with-install-root=%{buildroot}
%else
%configure2_5x --with-install-root=%{buildroot} 
%endif
perl -pi -e 's#LDFLAGS  =  -L/usr/lib -Wl,-rpath,/usr/lib#LDFLAGS  =  -L/usr/lib -Wl#' src/Makefile
##perl -pi -e 's#ja\.(po|gmo)##' po/Makefile
%make
mv src/xsane src/xsane-gimp

make clean
%if %debug
CFLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`" CXXFLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`" %configure2_5x --with-install-root=%{buildroot} --disable-gimp
%else
%configure2_5x --with-install-root=%{buildroot} --disable-gimp
%endif
perl -pi -e 's#LDFLAGS  =  -L/usr/lib -Wl,-rpath,/usr/lib#LDFLAGS  =  -L/usr/lib -Wl#' src/Makefile
##perl -pi -e 's#ja\.(po|gmo)##' po/Makefile
%make

%install

rm -rf $RPM_BUILD_ROOT

%if %debug
export DONT_STRIP=1
%endif

%makeinstall
install src/xsane-gimp %{buildroot}%{_bindir}
%find_lang %{name}

mkdir -p %{buildroot}/{%{_miconsdir},%{_liconsdir},%{_menudir}}
install -m 0644 %SOURCE1 %{buildroot}/%{_miconsdir}/xsane.png
install -m 0644 %SOURCE2 %{buildroot}/%{_iconsdir}/xsane.png
install -m 0644 %SOURCE3 %{buildroot}/%{_liconsdir}/xsane.png

mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=XSane
Comment=XSane
Exec=%{_bindir}/xsane
Icon=%{name}
Terminal=false
Type=Application
Categories=Graphics;Scanning;GTK;
EOF

# dynamic desktop support
%define launchers /etc/dynamic/launchers/scanner
mkdir -p $RPM_BUILD_ROOT%launchers
cat > $RPM_BUILD_ROOT%launchers/%name.desktop << EOF
[Desktop Entry]
Name=XSane \$device
Comment=XSane
Exec=%_bindir/xsane
Terminal=false
Icon=%name
Type=Application
EOF

%clean
rm -fr %buildroot

%files -f %{name}.lang
%defattr(-,root,root)
%doc xsane*
%config(noreplace) %launchers/%name.desktop
%_bindir/xsane
%dir %_datadir/sane
%_datadir/sane/*
%_mandir/man1/*
%{_datadir}/applications/mandriva-%{name}.desktop
%_iconsdir/*

%post
%update_menus
update-alternatives --install %{launchers}/kde.desktop scanner.kde.dynamic %launchers/%name.desktop 30
update-alternatives --install %{launchers}/gnome.desktop scanner.gnome.dynamic %launchers/%name.desktop 30

%postun
%update_menus

if [ $1 = 0 ]; then
  update-alternatives --remove scanner.kde.dynamic %launchers/%name.desktop
  update-alternatives --remove scanner.gnome.dynamic %launchers/%name.desktop
fi

%files gimp
%defattr(-,root,root)
%doc xsane*
%{_bindir}/xsane-gimp

%post gimp
if [ -d %_libdir/gimp ]; then
  GIMPDIR=`ls -d %_libdir/gimp/[012]*`
  [ -z "$GIMPDIR" ] && exit 0
  for i in $GIMPDIR;do
  [ -d $i/plug-ins ] || mkdir -p $i/plug-ins
  %{__ln_s} -f %_bindir/xsane-gimp $i/plug-ins/xsane
  done
fi
 
%postun gimp
if [ $1 = 0 ]; then
  if [ -d %_libdir/gimp ]; then
    GIMPDIR=`ls -d %_libdir/gimp/[012]*`
        [ -z "$GIMPDIR" ] && exit 0
        for i in $GIMPDIR;do
    [ -d $i/plug-ins ] || mkdir -p $i/plug-ins
    %{__rm} -f $i/plug-ins/xsane
        done
  fi
fi
