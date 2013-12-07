# Enable debug mode
%define debug 0

Name:		xsane
Version:	0.999
Release:	4
Summary:	Frontend for the SANE scanner interface
Group:		Graphics
URL:		http://www.xsane.org/
License:	GPLv2+
Source0:	ftp://ftp.sane-project.org/pub/sane/xsane/%{name}-%version.tar.gz
Patch0:		xsane-0.99-browser.patch
Patch1:		xsane-desktop.patch
Patch2:		xsane-ru-po.patch
Patch3:		xsane-0.995-close-fds.patch
Patch4:		xsane-0.997-no-file-selected.patch
Patch5:		xsane-0.998-libpng.patch
Patch6:		xsane-0.998-preview-selection.patch
Patch7:		xsane-0.998-wmclass.patch
# Weird hack needed to work around rpm causing checksum errors when
# packaging the pnm
Patch8:		xsane-0.998-pnm-to-png.patch
# Contains "www-browser" script
Requires:	desktop-common-data
Requires(post,postun):	rpm-helper
# This is for the drakxtools so that they can install a GUI for scanning
# but decide depending on the system environment which GUI actually to
# install
Provides:		scanner-gui
BuildRequires:	imagemagick
BuildRequires:	jpeg-devel
BuildRequires:	tiff-devel
BuildRequires:	pkgconfig(gimp-2.0)
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(gtk+-2.0)
BuildRequires:	pkgconfig(lcms)
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
Requires:	sane >= 1.0, %{name} >= %{version}

%description gimp
This package provides the regular XSane frontend for the SANE scanner
interface, but it works as a GIMP 2.0 plug-in.  You must have GIMP 2.0 (or
newer) installed to use this package.

%prep
%setup -q
%patch0 -p0 -b .www-browser
%patch1 -p1 -b .desktop-file
%patch2 -p1 -b .po-file
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1

%build
%if %{debug}
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
Exec=%{_bindir}/xsane
Terminal=false
Icon=%{name}
Type=Application
EOF

convert %buildroot%_datadir/sane/xsane/xsane-startimage.pnm %buildroot%_datadir/sane/xsane-startimage.png
rm %buildroot%_datadir/sane/xsane/xsane-startimage.pnm

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

%post
update-alternatives --install %{launchers}/kde.desktop scanner.kde.dynamic %{launchers}/%{name}.desktop 30
update-alternatives --install %{launchers}/gnome.desktop scanner.gnome.dynamic %{launchers}/%{name}.desktop 30

%postun
if [ $1 = 0 ]; then
  update-alternatives --remove scanner.kde.dynamic %{launchers}/%{name}.desktop
  update-alternatives --remove scanner.gnome.dynamic %{launchers}/%{name}.desktop
fi

%files gimp
%doc xsane*
%{_bindir}/xsane-gimp

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


%changelog
* Wed Aug 24 2011 Alex Burmashev <burmashev@mandriva.org> 0.998-3mdv2011.0
+ Revision: 696500
- update ru locale patch

  + Alexander Barakin <abarakin@mandriva.org>
    - Updated Russian translation

* Sat May 21 2011 JosÃ© Melo <ze@mandriva.org> 0.998-1
+ Revision: 676467
- version 0.998
- remove patch2 (fixed upstream)

* Sat May 07 2011 Oden Eriksson <oeriksson@mandriva.com> 0.997-4
+ Revision: 671362
- mass rebuild

* Sat Dec 04 2010 Oden Eriksson <oeriksson@mandriva.com> 0.997-3mdv2011.0
+ Revision: 608238
- rebuild

* Mon Jun 21 2010 Frederic Crozat <fcrozat@mandriva.com> 0.997-2mdv2010.1
+ Revision: 548363
- Add missing buildrequires
- Add lcms build requirement (Mdv bug #59855)

* Tue Mar 09 2010 Sandro Cazzaniga <kharec@mandriva.org> 0.997-1mdv2010.1
+ Revision: 516855
- update to 0.997

* Mon Jan 11 2010 Funda Wang <fwang@mandriva.org> 0.996-4mdv2010.1
+ Revision: 489570
- BR jpeg

  + Oden Eriksson <oeriksson@mandriva.com>
    - rebuilt against libjpeg v8

* Tue Aug 18 2009 Funda Wang <fwang@mandriva.org> 0.996-3mdv2010.0
+ Revision: 417585
- rebuild for new libjpeg v7

  + Nicolas LÃ©cureuil <nlecureuil@mandriva.com>
    - Fix gcc44 patch

* Wed May 27 2009 Nicolas LÃ©cureuil <nlecureuil@mandriva.com> 0.996-2mdv2010.0
+ Revision: 380117
- Fix build with gcc 4.4
- Rediff patches

* Thu Nov 27 2008 Frederik Himpe <fhimpe@mandriva.org> 0.996-1mdv2009.1
+ Revision: 307320
- Update to new version 0.966
- Use desktop file and icon now included in upstream package
- Remove redundant BuildRequires
- Clean up SPEC file (use braces around variables, no more
  $RPM_BUILD_ROOT)

* Thu Jun 12 2008 Pixel <pixel@mandriva.com> 0.995-2mdv2009.0
+ Revision: 218427
- rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas

* Mon Feb 18 2008 Thierry Vignaud <tv@mandriva.org> 0.995-2mdv2008.1
+ Revision: 171191
- rebuild
- fix "foobar is blabla" summary (=> "blabla") so that it looks nice in rpmdrake
- kill re-definition of %%buildroot on Pixel's request
- kill explicit icon extension

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Mon Nov 26 2007 Funda Wang <fwang@mandriva.org> 0.995-1mdv2008.1
+ Revision: 112146
- New version 0.995

* Wed Aug 29 2007 Funda Wang <fwang@mandriva.org> 0.994-2mdv2008.0
+ Revision: 73529
- fix menu category -> only Graphics/Scanning now.

* Fri Jun 08 2007 Funda Wang <fwang@mandriva.org> 0.994-1mdv2008.0
+ Revision: 37118
- New version
- bunzip2 the patch
- Import xsane



* Tue Sep 05 2006 Nicolas Lécureuil <neoclust@mandriva.org> 0.991-2mdv2007.0
- Use mkrel
- XDG

* Fri Feb  3 2006 Till Kamppeter <till@mandrakesoft.com> 0.991-1mdk
- Updated to version 0.991 (Bug fixes). 

* Sat Jan 14 2006 Till Kamppeter <till@mandrakesoft.com> 0.99-1mdk
- Updated to version 0.99 (Multipage project to create multipage documents, 
  types: ps, pdf, tiff; ASMTP support; improved ADF handling; several
  bugfixes and small improvements).
- Rediffed the www-browser patch.
- Introduced %%mkrel.

* Thu Dec 15 2005 Till Kamppeter <till@mandrakesoft.com> 0.98b-1mdk
- Updated to version 0.98b.

* Wed Nov 23 2005 Till Kamppeter <till@mandrakesoft.com> 0.98a-1mdk
- Updated to version 0.98a.

* Mon Sep 19 2005 Till Kamppeter <till@mandrakesoft.com> 0.97-2mdk
- Fixed web browser call for help functions (bug 14876, modified patch).
- Added "Requires: desktop-common-data" (for the "www-browser" script).

* Sat Jan 22 2005 Till Kamppeter <till@mandrakesoft.com> 0.97-1mdk
- Updated to version 0.97.

* Fri Jan  7 2005 Till Kamppeter <till@mandrakesoft.com> 0.96-2mdk
- Removed GIMP from "Requires:" so that the "xsane-gimp" package works with
  both GIMP 2.0.x and 2.2.x.
 
* Fri Jan  7 2005 Till Kamppeter <till@mandrakesoft.com> 0.96-1mdk
- Updated to version 0.96.

* Tue Oct 19 2004 Till Kamppeter <till@mandrakesoft.com> 0.93-2mdk
- Introduced and enabled debug mode (macro "%%debug").

* Wed Apr 28 2004 Till Kamppeter <till@mandrakesoft.com> 0.93-1mdk
- Updated to version 0.93.
- GIMP plug-in built for GIMP 2.0 now.

* Fri Mar 12 2004 Till Kamppeter <till@mandrakesoft.com> 0.92-2mdk
- Added "Provides: scanner-gui" (For the drakxtools to install a GUI for
  scanning dependent on the system environment).

* Tue Dec 16 2003 Till Kamppeter <till@mandrakesoft.com> 0.92-1mdk
- Updated to version 0.92.

* Fri Sep 19 2003 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 0.91-2mdk
- fix deps

* Thu Jul  3 2003 Daouda LO <daouda@mandrakesoft.com> 0.91-1mdk
- 0.91
- patch to replace netscape by $$BROWSER for doc(#2995) 

* Tue Apr 29 2003 Daouda LO <daouda@mandrakesoft.com> 0.90-3mdk
- Buildrequires

* Sat Feb  1 2003 Till Kamppeter <till@mandrakesoft.com> 0.90-2mdk
- Rebuilt against SANE 1.0.10.
- Removed obsolete "Packager:" tag.

* Thu Dec 26 2002 Daouda LO <daouda@mandrakesoft.com> 0.90-1mdk
- release 0.90 

* Mon Jul 15 2002 Yves Duret <yduret@mandrakesoft.com> 0.87-1mdk
- new upstream release.
- fix hardcoded-library-path.

* Wed May 22 2002 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 0.86-2mdk
- Automated rebuild with gcc 3.1-1mdk

* Sat Apr 27 2002 Yves Duret <yduret@mandrakesoft.com> 0.86-1mdk
- version 0.86

* Tue Apr 16 2002 Yves Duret <yduret@mandrakesoft.com> 0.85-2mdk
- add patch0 to fix gtk crashes (Oliver Rauch)

* Sun Apr 14 2002 Yves Duret <yduret@mandrakesoft.com> 0.85-1mdk
- version 0.85

* Sat Mar 09 2002 Yves Duret <yduret@mandrakesoft.com> 0.84-6mdk
- fix %%post (gimpdir/plug-ins) thanx Michael Reinsch <mr@uue.org>

* Sat Mar 02 2002 David BAUDENS <baudens@mandrakesoft.com> 0.84-5mdk
- Don't use ugly icons in menu and dynamic entries
- Requires: %%version-%%release and not only %%version

* Sun Feb 17 2002 Yves Duret <yduret@mandrakesoft.com> 0.84-4mdk
- fix dynamic launcher entry

* Fri Feb 01 2002 Yves Duret <yduret@mandrakesoft.com> 0.84-3mdk
- added Packager: tag on myself

* Mon Jan 28 2002 Yves Duret <yduret@mandrakesoft.com> 0.84-2mdk
- rebuild against libusb 0.1.4

* Wed Jan 23 2002 Yves Duret <yduret@mandrakesoft.com> 0.84-1mdk
- version 0.84
- fix menu entry (png icons)

* Mon Jan 07 2002 Yves Duret <yduret@mandrakesoft.com> 0.83-1mdk
- version 0.83

* Sat Dec 08 2001 Yves Duret <yduret@mandrakesoft.com> 0.82-1mdk
- version 0.82 (add spanish l10n)
- put back jap l10n

* Wed Nov 28 2001 Yves Duret <yduret@mandrakesoft.com> 0.81-1mdk
- version 0.81
- rebuild with new sane & gimp

* Fri Oct 19 2001 Yves Duret <yduret@mandrakesoft.com> 0.80-2mdk
- rebuild with last gimp

* Tue Oct 09 2001 Yves Duret <yduret@mandrakesoft.com> 0.80-1mdk
- version 0.80
- remove buggy jap po

* Wed Sep 12 2001 Frederic Lepied <flepied@mandrakesoft.com> 0.79-5mdk
- added dynamic desktop entry

* Thu Aug 23 2001 Yves Duret <yduret@mandrakesoft.com> 0.79-4mdk
- final (i hope this time!) russian translation by John Profic <profic@lrn.ru>

* Thu Aug 16 2001 Yves Duret <yduret@mandrakesoft.com> 0.79-3mdk
- complete russian translation by John Profic <profic@lrn.ru>

* Tue Aug 14 2001 Yves Duret <yduret@mandrakesoft.com> 0.79-2mdk
- added ru translation from John Profic <profic@lrn.ru>

* Tue Jul 24 2001 Yves Duret <yduret@mandrakesoft.com> 0.79-1mdk
- version 0.79

* Mon Jul 23 2001 Stefan van der Eijk <stefan@eijk.nu> 0.78-3mdk
- BuildRequires:	libjpeg-devel libpng-devel libusb-devel
- Remove BuildRequires: gtk+

* Thu Jul 19 2001 Yves Duret <yduret@mandrakesoft.com> 0.78-2mdk
- corrected gimp dependencies
- removed rpath

* Sun Jun 10 2001 Yves Duret <yduret@mandrakesoft.com> 0.78-1mdk
- version 0.78 : some new features and bug fixes
   * scan & mail
   * function (pirate icon) to delete preview image cache
   * ...
   
* Sun Jun  3 2001 Yves Duret <yduret@mandrakesoft.com> 0.77-3mdk
- added xsane-gimp package. registerd itself as a gimp plug-in
- added menu & icons entries

* Mon May 28 2001 Yves Duret <yduret@mandrakesoft.com> 0.77-2mdk
- corrected BuildRequires tag

* Fri May 25 2001 Yves Duret <yduret@mandrakesoft.com> 0.77-1mdk
- version 0.77 : mainly  bug fixes

* Tue May  1 2001 Yves Duret <yduret@mandrakesoft.com> 0.76-1mdk
- version 0.76

* Tue Apr 24 2001 Yves Duret <yduret@mandrakesoft.com> 0.75-1mdk
- updated to version 0.75
- put back gimp plug-in

* Tue Mar 13 2001 Yves Duret <yduret@mandrakesoft.com> 0.72-1mdk
- use spec file from cvs since SRPMS disappear
- updated to version 0.72
- spec clean up
- fix buildRequires
- URL: tag updated
- added the local l10n files

* Sun Jan 07 2001 David BAUDENS <baudens@mandrakesoft.com> 0.69-2mdk
- Fix buildRequires
- Fix Requires
- Clean %%files section
- Spec clean up

* Mon Jan 01 2001 Daouda Lo <daouda@mandrakesoft.com> 0.69-1mdk
- release 

* Mon Dec 18 2000 Lenny Cartier <lenny@mandrakesoft.com> 0.68-1mdk
- updated to 0.68

* Fri Dec 08 2000 Lenny Cartier <lenny@mandrakesoft.com> 0.65-1mdk
- updated to 0.65

* Mon Nov 13 2000 Geoffrey Lee <snailtalk@mandrakesoft.com> 0.64-1mdk
- new and shiny version.

* Fri Nov 03 2000 Geoffrey Lee <snailtalk@mandrakesoft.com> 0.63-1mdk
- new and shiny version.

* Sat Jul 15 2000 Geoffrey Lee <snailtalk@linux-mandrake.com> 0.60-1mdk
- new version
- macrosifications

* Thu May 04 2000 Lenny Cartier <lenny@mandrakesoft.com> 0.57-2mdk
- fix group

* Thu Mar 16 2000 Geoffrey Lee <snailtalk@linux-mandrake.com>
- first release for mandrake
