"""SSH Hosts module."""

from yast3.modules.ssh.hosts.manager import HostManager
from yast3.modules.ssh.hosts.tab import HostsTab

__all__ = ["HostsTab", "HostManager"]
