"""Qt6 module packages for YaST3 settings sections."""

from yast3.qt6.cron import CronModule
from yast3.qt6.git import GitModule
from yast3.qt6.hostname import HostnameModule
from yast3.qt6.hosts import HostsModule
from yast3.qt6.packages import PackagesModule
from yast3.qt6.repositories import RepositoriesModule
from yast3.qt6.ssh import SSHClientModule

__all__ = [
    "CronModule",
    "GitModule",
    "HostnameModule",
    "HostsModule",
    "PackagesModule",
    "RepositoriesModule",
    "SSHClientModule",
]