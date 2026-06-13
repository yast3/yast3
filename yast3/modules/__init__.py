"""Module packages for YaST3 settings sections."""

from .hosts import HostsModule
from .packages import PackagesModule

__all__ = [
	'HostsModule',
	'PackagesModule',
]
