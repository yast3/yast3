"""TUI module packages for YaST3 settings sections."""

from yast3.tui.cron import CronModule
from yast3.tui.datetime import DateTimeModule
from yast3.tui.git import GitModule
from yast3.tui.hostname import HostnameModule
from yast3.tui.hosts import HostsModule
from yast3.tui.languages import LanguagesModule
from yast3.tui.packages import PackagesModule
from yast3.tui.proxy import ProxyModule
from yast3.tui.repositories import RepositoriesModule
from yast3.tui.services import ServicesModule
from yast3.tui.snapshots import SnapshotsModule
from yast3.tui.ssh import SSHClientModule

__all__ = [
    "CronModule",
    "DateTimeModule",
    "GitModule",
    "HostnameModule",
    "HostsModule",
    "LanguagesModule",
    "PackagesModule",
    "ProxyModule",
    "RepositoriesModule",
    "ServicesModule",
    "SnapshotsModule",
    "SSHClientModule",
]