# Enable debug mode
%define debug 0

Name:		xsane
Version:	0.996
Release:	%mkrel 4
Summary:	Frontend for the SANE scanner interface
Group:		Graphics
URL:		http://www.xsane.org/
Source:		ftp://ftp.sane-project.org/pub/sane/xsane/%{name}-%version.tar.gz
Patch0:		xsane-0.99-browser.patch
Patch1:		xsane-desktop.patch
Patch2:     xsane-0.996-fix-gcc44.patch
License:	GPLv2+
Requires:	libsane >= 1.0.4
# Contains "www-browser" script
Requires:	desktop-common-data
# This is for the drakxtools so that they can install a GUI for scanning
# but decide depending on the system environment which GUI actually to
# install
Provides:       scanner-gui
BuildRequires:	sane-devel
BuildRequires:	libjpeg-devel
BuildRequires:	gimp-devel >= 2.0
BuildRequires:	imagemagick
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-root

%description
XSane is an X based interface for the SANE (Scanner Access Now Easy)
library, which provides access to scanners, digital cameras, and other
capture devices.  XSane is written in GTK+ and provides control for
performing the scan and then manipulating the captured image.

You may install xsane-gimp if you want the GIMP plug-in.

%package gimp
Summary: 	GIMP plug-in which provides the SANE scanner interface
Group: 		Graphics
Requires: 	sane >= 1.0, %{name} >= %{version}
 
%description gimp
This package provides the regular XSane frontend for the SANE scanner
interface, but it works as a GIMP 2.0 plug-in.  You must have GIMP 2.0 (or
newer) installed to use this package.


%prep
%setup -q
%patch0 -p0 -b .www-browser
%patch1 -p1 -b .desktop-file
%patch2 -p0 -b .gcc44

%build
%if %debug
export DONT_STRIP=1
CFLAGS="`echo %{optflags} |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`" CXXFLAGS="`echo %{optflags} |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`" %configure2_5x --with-install-root=%{buildroot}
%else
%configure2_5x --with-install-root=%{buildroot} 
%endif
perl -pi -e 's#LDFLAGS  =  -L/usr/lib -Wl,-rpath,/usr/lib#LDFLAGS  =  -L/usr/lib -Wl#' src/Makefile
##perl -pi -e 's#ja\.(po|gmo)##' po/Makefile
%make
mv src/xsane src/xsane-gimp

make clean
%if %debug
CFLAGS="`echo %{optflags} |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`" CXXFLAGS="`echo %{optflags} |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`" %configure2_5x --with-install-root=%{buildroot} --disable-gimp
%else
%configure2_5x --with-install-root=%{buildroot} --disable-gimp
%endif
perl -pi -e 's#LDFLAGS  =  -L/usr/lib -Wl,-rpath,/usr/lib#LDFLAGS  =  -L/usr/lib -Wl#' src/Makefile
##perl -pi -e 's#ja\.(po|gmo)##' po/Makefile
%make

%install

rm -rf %{buildroot}

%if %debug
export DONT_STRIP=1
%endif

%makeinstall_std
install src/xsane-gimp %{buildroot}%{_bindir}
%find_lang %{name}
mkdir -p %{buildroot}%{_iconsdir}/hicolor/{48x48,32x32,16x16}/apps
convert -scale 48 %{buildroot}/usr/share/pixmaps/xsane.xpm %{buildroot}%{_iconsdir}/hicolor/48x48/apps/%{name}.png 
convert -scale 32 %{buildroot}/usr/share/pixmaps/xsane.xpm %{buildroot}%{_iconsdir}/hicolor/32x32/apps/%{name}.png
convert -scale 16 %{buildroot}/usr/share/pixmaps/xsane.xpm %{buildroot}%{_iconsdir}/hicolor/16x16/apps/%{name}.png

# dynamic desktop support
%define launchers /etc/dynamic/launchers/scanner
mkdir -p %{buildroot}%{launchers}
cat > %{buildroot}%{launchers}/%{name}.desktop << EOF
[Desktop Entry]
Name=XSane \$device
Comment=XSane
Exec=%_bindir/xsane
Terminal=false
Icon=%{name}
Type=Application
EOF

%clean
rm -fr %{buildroot}

%files -f %{name}.lang
%defattr(-,root,root)
%doc xsane*
%config(noreplace) %{launchers}/%{name}.desktop
%{_bindir}/xsane
%dir %{_datadir}/sane
%{_datadir}/sane/*
%{_mandir}/man1/*
%{_datadir}/applications/%{name}.desktop
%{_datadir}/pixmaps/%{name}.xpm
%{_iconsdir}/hicolor/*/apps/*

%post
%if %mdkversion < 200900
%update_menus
%endif
update-alternatives --install %{launchers}/kde.desktop scanner.kde.dynamic %{launchers}/%{name}.desktop 30
update-alternatives --install %{launchers}/gnome.desktop scanner.gnome.dynamic %{launchers}/%{name}.desktop 30

%postun
%if %mdkversion < 200900
%update_menus
%endif

if [ $1 = 0 ]; then
  update-alternatives --remove scanner.kde.dynamic %{launchers}/%{name}.desktop
  update-alternatives --remove scanner.gnome.dynamic %{launchers}/%{name}.desktop
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
