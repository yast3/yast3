"""Proxy management core logic."""

from yast3.core.proxy.proxy import (
    PROXY_CONFIG_FILE,
    ProxyConfig,
    ensure_proxy_config_options,
    load_proxy_config,
    save_proxy_config,
)

__all__ = [
    "PROXY_CONFIG_FILE",
    "ProxyConfig",
    "ensure_proxy_config_options",
    "load_proxy_config",
    "save_proxy_config",
]
