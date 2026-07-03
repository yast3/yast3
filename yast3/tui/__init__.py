"""TUI module packages for YaST3 settings sections."""

from yast3.tui.cron import CronModule
from yast3.tui.git import GitModule
from yast3.tui.hostname import HostnameModule
from yast3.tui.hosts import HostsModule
from yast3.tui.packages import PackagesModule
from yast3.tui.proxy import ProxyModule
from yast3.tui.repositories import RepositoriesModule
from yast3.tui.ssh import SSHClientModule

__all__ = [
    "CronModule",
    "GitModule",
    "HostnameModule",
    "HostsModule",
    "PackagesModule",
    "ProxyModule",
    "RepositoriesModule",
    "SSHClientModule",
]