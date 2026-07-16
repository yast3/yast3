# MaST

MaST (**M**aybe **a**nthoer **S**etup **T**ool) is continuous development of YaST with Python & Qt6 / GTK4 / TUI.

## Install

### openSUSE & SLE

```bash
# for KDE/LXQt users
opi mast-qt6
# for GNOME users
opi mast-gtk4
# for server users
opi mast-tui
```

## Modules

| Name         | Core | Qt6 | GTK4 | TUI |
|--------------|:----:|:---:|:----:|:---:|
| Cron         | 🚧   | 🚧  | 🚧   | 🚧  |
| DateTime     | ✅   | ✅  | ✅   | ✅  |
| Flatpak      | ✅   | ✅  | ✅   | ❌  |
| Git          | ✅   | ✅  | ✅   | ✅  |
| Hostname     | ✅   | ✅  | ✅   | ✅  |
| Hosts        | ✅   | ✅  | ✅   | ✅  |
| Languages    | ✅   | ✅  | ✅   | ✅  |
| Packages     | 🚧   | 🚧  | 🚧   | 🚧  |
| Proxy        | ✅   | ✅  | ✅   | ✅  |
| Repositories | ✅   | ✅  | ✅   | ✅  |
| Services     | ✅   | ✅  | ✅   | ✅  |
| Snapshots    | ✅   | ✅  | ✅   | ✅  |
| SSH Client   | ✅   | ✅  | ✅   | ✅  |

**Planned:** SSH Server (system)

## Requirements

- Python 3.12+
- Qt6 bindings for Python via PySide6
- GTK4 bindings for Python via PyGObject

## Run

```bash
sudo zypper install python3-pyside6 python3-gobject gtk4-devel python3-Babel python3-crontab python3-configobj python3-python-dotenv python3-pytest
python3 -m mast
```

## Install on Linux

Install the app for the current user and register the desktop launcher:

```bash
make install
```

This follows the usual `prefix`-based Makefile pattern and installs under
`$HOME/.local` by default. Install it system-wide instead:

```bash
sudo make prefix=/usr/local install
```

After installation, you can start the app from the application menu or by running:

```bash
mast
```

## Package

Build standard Python distribution artifacts for Linux packaging workflows:

```bash
make dist
```

This creates source and wheel packages in `dist/`.

To stage a package into a temporary root, use `DESTDIR`:

```bash
make DESTDIR=/tmp/package-root prefix=/usr install
```
