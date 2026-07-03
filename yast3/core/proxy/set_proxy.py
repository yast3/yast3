#!/usr/bin/env python3
"""Write /etc/sysconfig/proxy values with elevated privileges."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys

try:
    from yast3.core.proxy.proxy import PROXY_CONFIG_FILE, ProxyConfig, _write_proxy_config
except Exception:
    # Fallback for direct script execution when package import path is unavailable.
    proxy_module_path = Path(__file__).with_name("proxy.py")
    spec = importlib.util.spec_from_file_location("_yast3_proxy_core", proxy_module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load proxy core module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    PROXY_CONFIG_FILE = module.PROXY_CONFIG_FILE
    ProxyConfig = module.ProxyConfig
    _write_proxy_config = module._write_proxy_config


def main() -> int:
    parser = argparse.ArgumentParser(description="Set /etc/sysconfig/proxy values")
    parser.add_argument("--enabled", required=True, choices=["yes", "no"])
    parser.add_argument("--http", default="")
    parser.add_argument("--https", default="")
    parser.add_argument("--ftp", default="")
    parser.add_argument("--no-proxy", default="")
    args = parser.parse_args()

    config = ProxyConfig(
        enabled=args.enabled == "yes",
        http_proxy=args.http,
        https_proxy=args.https,
        ftp_proxy=args.ftp,
        no_proxy=args.no_proxy,
    )

    try:
        _write_proxy_config(config, PROXY_CONFIG_FILE)
    except PermissionError:
        return 6
    except Exception as e:
        print(f"Error writing {PROXY_CONFIG_FILE}: {e}", file=sys.stderr)
        return 7

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
