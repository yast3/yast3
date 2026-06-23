# YaST3

Save YaST ♥️ with Python 3 & Qt6 Widgets.

## Modules

| Name | Core | Qt6 | GTK4 | TUI |
|------|:----:|:---:|:----:|:---:|
| Git | ✅ | ✅ | ✅ | ✅ |
| Hostname | ✅ | ✅ | ✅ | ✅ |
| Hosts | ✅ | ✅ | ✅ | ✅ |
| Repositories | ✅ | ✅ | ✅ | ✅ |
| SSH Client | ✅ | ✅ | ✅ | ✅ |
| Cron | ✅ | ✅ | ✅ | ✅ |
| Packages | ✅ | ✅ | ✅ | ❌ |

**Planned:** SSH Server (system)

## Requirements

- Python 3.12+
- Qt6 bindings for Python via PySide6
- GTK4 bindings for Python via PyGObject

## Run

```bash
sudo zypper install python3-pyside6 python3-gobject python3-Babel python3-crontab
python3 -m yast3
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
yast3
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
