"""YaST3 Qt6 GUI application."""

from yast3.qt6.cron import CronModule
from yast3.qt6.datetime import DateTimeModule
from yast3.qt6.flatpak import FlatpakModule
from yast3.qt6.git import GitModule
from yast3.qt6.hostname import HostnameModule
from yast3.qt6.hosts import HostsModule
from yast3.qt6.packages import PackagesModule
from yast3.qt6.proxy import ProxyModule
from yast3.qt6.repositories import RepositoriesModule
from yast3.qt6.services import ServicesModule
from yast3.qt6.snapshots import SnapshotsModule
from yast3.qt6.ssh import SSHClientModule

__all__ = [
    "CronModule",
    "DateTimeModule",
    "FlatpakModule",
    "GitModule",
    "HostnameModule",
    "HostsModule",
    "PackagesModule",
    "ProxyModule",
    "RepositoriesModule",
    "ServicesModule",
    "SnapshotsModule",
    "SSHClientModule",
]