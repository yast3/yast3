# MaST

MaST (**M**aybe **a**nthoer **S**etup **T**ool) is continuous development of YaST with Python & Qt6 / GTK4 / TUI.

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

## Installation

### openSUSE & SLE

```bash
# for KDE/LXQt users
opi mast-qt6
# for GNOME users
opi mast-gtk4
# for server users
opi mast-tui
```

## Development

```bash
# install dependencies
sudo zypper install make python3-pyside6 python3-gobject gtk4-devel python3-Babel python3-python-crontab python3-configobj python3-python-dotenv python3-pytest python3-systemd

# compile translations
make

# start apps
python3 -m mast.qt6
python3 -m mast.gtk4
python3 -m mast.tui
```
