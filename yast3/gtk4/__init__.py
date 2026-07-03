"""YaST3 GTK4 GUI application."""

from yast3.gtk4.cron import CronModule
from yast3.gtk4.git import GitModule
from yast3.gtk4.hostname import HostnameModule
from yast3.gtk4.hosts import HostsModule
from yast3.gtk4.packages import PackagesModule
from yast3.gtk4.proxy import ProxyModule
from yast3.gtk4.repositories import RepositoriesModule
from yast3.gtk4.ssh import SSHClientModule

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