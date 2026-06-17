"""Module packages for YaST3 settings sections."""

from .cron import CronModule
from .git import GitModule
from .hostname import HostnameModule
from .hosts import HostsModule
from .packages import PackagesModule
from .repositories import RepositoriesModule
from .ssh import SSHClientModule

__all__ = [
    "CronModule",
    "GitModule",
    "HostnameModule",
    "HostsModule",
    "PackagesModule",
    "RepositoriesModule",
    "SSHClientModule",
]
