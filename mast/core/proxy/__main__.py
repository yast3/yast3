import argparse
import sys

from mast.core.proxy import ProxyConfig

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Switch mirrors for openSUSE and Packman repositories.")
    parser.add_argument('--enabled', type=str, required=True, help="Enable or disable the proxy (yes/no).")
    parser.add_argument('--http', type=str, required=True, help="New HTTP proxy URL (with protocol).")
    parser.add_argument('--https', type=str, required=True, help="New HTTPS proxy URL (with protocol).")
    parser.add_argument('--ftp', type=str, required=True, help="New FTP proxy URL (with protocol).")
    parser.add_argument('--socks', type=str, required=True, help="New SOCKS proxy URL (with protocol).")
    parser.add_argument('--noproxy', type=str, required=True, help="New NO_PROXY value (comma-separated list of hosts).")
    args = parser.parse_args()

    config = ProxyConfig()

    config.PROXY_ENABLED = args.enabled
    config.HTTP_PROXY = args.http
    config.HTTPS_PROXY = args.https
    config.FTP_PROXY = args.ftp
    config.SOCKS_PROXY = args.socks
    config.NO_PROXY = args.noproxy

    config.write()

    sys.exit(0)
