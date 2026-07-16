
OS_RELEASE_PATH = "/etc/os-release"

cached = None

def read_os_release() -> dict[str, str]:
    """Read the /etc/os-release file and return a dictionary of key-value pairs."""
    global cached
    if cached is not None:
        return cached

    os_release_info: dict[str, str] = {}

    try:
        with open(OS_RELEASE_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, _, value = line.partition("=")
                    os_release_info[key] = value.strip('"')
    except Exception:
        pass

    cached = os_release_info
    return os_release_info
