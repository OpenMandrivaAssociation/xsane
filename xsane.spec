# Enable debug mode
%define debug 0

Name:		xsane
Version:	0.999
Release:	14
Summary:	Frontend for the SANE scanner interface
Group:		Graphics
URL:		http://www.xsane.org/
License:	GPLv2+
Source0:	ftp://ftp.sane-project.org/pub/sane/xsane/%{name}-%version.tar.gz
Source1:        xsane-russian-docs.tar.xz
Source2:        xsane.desktop
Patch0:		xsane-0.99-browser.patch
Patch2:		xsane-ru-po.patch
Patch3:		xsane-0.995-close-fds.patch
Patch4:		xsane-0.997-no-file-selected.patch
Patch5:		xsane-0.998-libpng.patch
Patch6:		xsane-0.998-preview-selection.patch
Patch7:		xsane-0.998-wmclass.patch
# Weird hack needed to work around rpm causing checksum errors when
# packaging the pnm
Patch8:		xsane-0.998-pnm-to-png.patch
# (tpg) add support for LCMS2
Patch9:		xsane-0.999-lcms2.patch
# autoconf-generated files
Patch100: xsane-0.999-7-autoconf.patch.bz2
# Contains "www-browser" script
Requires:	desktop-common-data
Requires(post,postun):	rpm-helper
# This is for the drakxtools so that they can install a GUI for scanning
# but decide depending on the system environment which GUI actually to
# install
Provides:	scanner-gui
BuildRequires:	intltool
BuildRequires:	imagemagick
BuildRequires:	jpeg-devel
BuildRequires:	tiff-devel
BuildRequires:	pkgconfig(gimp-2.0)
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(gtk+-2.0)
BuildRequires:	pkgconfig(lcms2)
BuildRequires:	pkgconfig(libgphoto2)
BuildRequires:	pkgconfig(libpng)
BuildRequires:	pkgconfig(libv4l1)
BuildRequires:	pkgconfig(libv4l2)
BuildRequires:	pkgconfig(sane-backends)

%description
XSane is an X based interface for the SANE (Scanner Access Now Easy)
library, which provides access to scanners, digital cameras, and other
capture devices.  XSane is written in GTK+ and provides control for
performing the scan and then manipulating the captured image.

You may install xsane-gimp if you want the GIMP plug-in.

%package gimp
Summary:	GIMP plug-in which provides the SANE scanner interface
Group:		Graphics
Requires:	sane >= 1.0
Requires:	%{name} >= %{version}

%description gimp
This package provides the regular XSane frontend for the SANE scanner
interface, but it works as a GIMP 2.0 plug-in.  You must have GIMP 2.0 (or
newer) installed to use this package.

%prep
%setup -q
cat %{SOURCE2} > src/xsane.desktop
%patch0 -p0 -b .www-browser
%patch2 -p1 -b .po-file
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch100 -p1

%build
%if %{debug}
export DONT_STRIP=1
CFLAGS="`echo %{optflags} |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`" CXXFLAGS="`echo %{optflags} |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`" %configure --with-install-root=%{buildroot}
%else
%configure --with-install-root=%{buildroot}
%endif
perl -pi -e 's#LDFLAGS  =  -L/usr/lib -Wl,-rpath,/usr/lib#LDFLAGS  =  -L/usr/lib -Wl#' src/Makefile
##perl -pi -e 's#ja\.(po|gmo)##' po/Makefile
%make
mv src/xsane src/xsane-gimp

make clean
%if %debug
CFLAGS="`echo %{optflags} |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`" CXXFLAGS="`echo %{optflags} |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`" %configure --with-install-root=%{buildroot} --disable-gimp
%else
%configure --with-install-root=%{buildroot} --disable-gimp
%endif
perl -pi -e 's#LDFLAGS  =  -L/usr/lib -Wl,-rpath,/usr/lib#LDFLAGS  =  -L/usr/lib -Wl#' src/Makefile
##perl -pi -e 's#ja\.(po|gmo)##' po/Makefile
%make

%install
%if %debug
export DONT_STRIP=1
%endif

%makeinstall_std
install src/xsane-gimp %{buildroot}%{_bindir}

# (tpg) icons
for i in 16 32 48; do
mkdir -p %{buildroot}%{_iconsdir}/hicolor/$i"x"$i/apps
install src/xsane-$i"x"$i.png %{buildroot}%{_iconsdir}/hicolor/$i"x"$i/apps/%{name}.png;
done

# dynamic desktop support
%define launchers /etc/dynamic/launchers/scanner
mkdir -p %{buildroot}%{launchers}
cat > %{buildroot}%{launchers}/%{name}.desktop << EOF
[Desktop Entry]
Name=XSane \$device
Comment=XSane
Exec=%{_bindir}/xsane
Terminal=false
Icon=%{name}
Type=Application
EOF

convert %{buildroot}%{_datadir}/sane/xsane/xsane-startimage.pnm %{buildroot}%{_datadir}/sane/xsane-startimage.png
rm %{buildroot}%{_datadir}/sane/xsane/xsane-startimage.pnm

mkdir -p %{buildroot}%{_datadir}/sane/xsane/doc/ru/
tar xf %{SOURCE1} -C %{buildroot}%{_datadir}/sane/xsane/doc/ru/

%find_lang %{name}

%post
update-alternatives --install %{launchers}/kde.desktop scanner.kde.dynamic %{launchers}/%{name}.desktop 30
update-alternatives --install %{launchers}/gnome.desktop scanner.gnome.dynamic %{launchers}/%{name}.desktop 30

%postun
if [ $1 = 0 ]; then
  update-alternatives --remove scanner.kde.dynamic %{launchers}/%{name}.desktop
  update-alternatives --remove scanner.gnome.dynamic %{launchers}/%{name}.desktop
fi

%post gimp
if [ -d %{_libdir}/gimp ]; then
  GIMPDIR=`ls -d %{_libdir}/gimp/[012]*`
  [ -z "$GIMPDIR" ] && exit 0
  for i in $GIMPDIR;do
  [ -d $i/plug-ins ] || mkdir -p $i/plug-ins
  %{__ln_s} -f %{_bindir}/xsane-gimp $i/plug-ins/xsane
  done
fi

%postun gimp
if [ $1 = 0 ]; then
  if [ -d %{_libdir}/gimp ]; then
    GIMPDIR=`ls -d %{_libdir}/gimp/[012]*`
        [ -z "$GIMPDIR" ] && exit 0
        for i in $GIMPDIR;do
    [ -d $i/plug-ins ] || mkdir -p $i/plug-ins
    %{__rm} -f $i/plug-ins/xsane
        done
  fi
fi

%files -f %{name}.lang
%doc xsane*
%config(noreplace) %{launchers}/%{name}.desktop
%{_bindir}/xsane
%dir %{_datadir}/sane
%{_datadir}/sane/*
%{_mandir}/man1/*
%{_datadir}/applications/%{name}.desktop
%{_datadir}/pixmaps/%{name}.xpm
%{_iconsdir}/hicolor/*/apps/*

%files gimp
%doc xsane*
%{_bindir}/xsane-gimp
