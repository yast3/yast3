#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_SCOPE="${1:---user}"

case "${INSTALL_SCOPE}" in
  --user)
    python3 -m pip install --upgrade --user "${ROOT_DIR}"
    APPLICATIONS_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
    ;;
  --system)
    if [ "${EUID}" -ne 0 ]; then
      echo "Error: --system requires root privileges." >&2
      exit 1
    fi
    python3 -m pip install --upgrade "${ROOT_DIR}"
    APPLICATIONS_DIR="/usr/local/share/applications"
    ;;
  *)
    echo "Usage: $0 [--user|--system]" >&2
    exit 1
    ;;
esac

if command -v update-desktop-database >/dev/null 2>&1 && [ -d "${APPLICATIONS_DIR}" ]; then
  update-desktop-database "${APPLICATIONS_DIR}" >/dev/null 2>&1 || true
fi

echo "YaST3 installed successfully."
