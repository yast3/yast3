"""Module packages for YaST3 settings sections."""

from yast3.modules.cron import CronModule
from yast3.modules.git import GitModule
from yast3.modules.hostname import HostnameModule
from yast3.modules.hosts import HostsModule
from yast3.modules.packages import PackagesModule
from yast3.modules.repositories import RepositoriesModule
from yast3.modules.ssh import SSHClientModule

__all__ = [
    "CronModule",
    "GitModule",
    "HostnameModule",
    "HostsModule",
    "PackagesModule",
    "RepositoriesModule",
    "SSHClientModule",
]
