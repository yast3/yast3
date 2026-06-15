"""Module packages for YaST3 settings sections."""

from .git import GitModule
from .hostname import HostnameModule
from .hosts import HostsModule
from .packages import PackagesModule
from .repositories import RepositoriesModule
from .ssh import SSHClientModule

__all__ = [
	'GitModule',
	'HostnameModule',
	'HostsModule',
	'PackagesModule',
	'RepositoriesModule',
	'SSHClientModule',
]
