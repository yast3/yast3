"""Module packages for YaST3 settings sections."""

from .hosts import HostsModule
from .packages import PackagesModule
from .repositories import RepositoriesModule

__all__ = [
	'HostsModule',
	'PackagesModule',
	'RepositoriesModule',
]
