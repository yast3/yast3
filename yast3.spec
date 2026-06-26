Name:           yast3
Version:        0.1.0
Release:        0
Summary:        GUI & TUI system settings tool

License:        GPL-3.0-or-later
URL:            https://github.com/yast3/yast3
Source0:        https://github.com/yast3/yast3/archive/v%{version}.tar.gz

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-Babel
BuildRequires:  make

Recommends:     %{name}-qt6

%description
YaST3 is a modern desktop settings shell built with Python 3,
providing Qt6, GTK4 GUI and Textual TUI interfaces for system
configuration management.

This is a metapackage that recommends the Qt6 GUI interface.
Install %{name}-qt6, %{name}-gtk4, or %{name}-tui for specific interfaces.

%package qt6
Summary:        YaST3 Qt6 GUI interface
Requires:       %{name}-core = %{version}-%{release}
Requires:       python3-PySide6

%description qt6
Qt6 GUI interface for YaST3 desktop settings shell.

%package tui
Summary:        YaST3 Textual TUI interface
Requires:       %{name}-core = %{version}-%{release}
Requires:       python3-textual

%description tui
Textual TUI interface for YaST3 desktop settings shell.

%package gtk4
Summary:        YaST3 GTK4 GUI interface
Requires:       %{name}-core = %{version}-%{release}
Requires:       python3-gobject

%description gtk4
GTK4 GUI interface for YaST3 desktop settings shell.

%package core
Summary:        YaST3 core functionality shared by all interfaces
Requires:       python3-crontab

%description core
Core modules and utilities shared by YaST3 Qt6, GTK4 and TUI interfaces.

%prep
%autosetup

%build
%make_build mo
%pyproject_wheel

%install
%pyproject_install

%files core
%license LICENSE
%doc README.md
%{python3_sitelib}/yast3/core/
%{python3_sitelib}/yast3-%{version}*.dist-info/
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/64x64/apps/%{name}.svg
%{_datadir}/locale/

%files qt6
%{python3_sitelib}/yast3/qt6/
%{_bindir}/yast3-qt6

%files tui
%{python3_sitelib}/yast3/tui/
%{_bindir}/yast3-tui

%files gtk4
%{python3_sitelib}/yast3/gtk4/
%{_bindir}/yast3-gtk4

%changelog
* Fri Jun 26 2026 YaST3 Team <yast3@opensuse.org> - 0.1.0-1
- Initial package release
