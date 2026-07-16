"""SSH Keys manager - handles SSH key operations."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass

SSH_DIR = os.path.expanduser("~/.ssh")


@dataclass
class KeyInfo:
    """Represents information about an SSH key."""

    name: str
    algorithm: str
    size: str
    fingerprint: str | None
    comment: str | None
    has_passphrase: bool
    has_public: bool
    has_private: bool
    path: str


class KeyManager:
    """Manages SSH key operations."""

    @staticmethod
    def list_keys() -> list[KeyInfo]:
        """List all SSH keys in ~/.ssh directory."""
        keys: list[KeyInfo] = []

        if not os.path.isdir(SSH_DIR):
            return keys

        try:
            files = os.listdir(SSH_DIR)
        except PermissionError:
            return keys

        # Find private key files (no extension or .pub)
        private_key_files = []
        for filename in files:
            filepath = os.path.join(SSH_DIR, filename)
            if os.path.isdir(filepath):
                continue
            # Skip .pub files - they're public keys
            if filename.endswith(".pub"):
                continue
            # Skip known_hosts, authorized_keys, config, etc.
            if filename in ("known_hosts", "authorized_keys", "config", "known_hosts2", "authorized_keys2"):
                continue
            # This might be a private key
            private_key_files.append(filename)

        for filename in private_key_files:
            filepath = os.path.join(SSH_DIR, filename)
            public_filepath = os.path.join(SSH_DIR, filename + ".pub")

            has_private = os.path.isfile(filepath)
            has_public = os.path.isfile(public_filepath)

            # Try to get key info from public key
            algorithm = "-"
            size = "-"
            fingerprint = None
            comment = None
            has_passphrase = False

            if has_public:
                try:
                    with open(public_filepath, "r") as f:
                        content = f.read().strip()
                    parts = content.split()
                    if len(parts) >= 1:
                        algorithm = parts[0]
                    if len(parts) >= 2:
                        # For RSA keys, the second part is the base64 data
                        # Size is embedded in the key type for newer keys
                        if algorithm.startswith("ssh-rsa"):
                            # Estimate size from key length
                            size = "2048"  # Default, actual size needs ssh-keygen
                        elif algorithm.startswith("ssh-ed25519"):
                            size = "256"
                        elif algorithm.startswith("ecdsa"):
                            size = algorithm.split("-")[-1] if "-" in algorithm else "256"
                    if len(parts) >= 3:
                        comment = parts[2]

                    # Get fingerprint using ssh-keygen
                    result = subprocess.run(
                        ["ssh-keygen", "-lf", public_filepath],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        fp_parts = result.stdout.strip().split()
                        if fp_parts:
                            fingerprint = fp_parts[0]
                        # Size is in the output too
                        if len(fp_parts) >= 1 and fp_parts[1].isdigit():
                            size = fp_parts[1]
                except Exception:
                    pass

            # Check if private key has passphrase
            if has_private:
                result = subprocess.run(
                    ["ssh-keygen", "-yf", filepath],
                    input="",
                    capture_output=True,
                    text=True,
                )
                # If it returns without error, no passphrase
                # If it asks for passphrase (returns error), has passphrase
                has_passphrase = result.returncode != 0

            keys.append(KeyInfo(
                name=filename,
                algorithm=algorithm,
                size=size,
                fingerprint=fingerprint,
                comment=comment,
                has_passphrase=has_passphrase,
                has_public=has_public,
                has_private=has_private,
                path=filepath,
            ))

        return keys

    @staticmethod
    def get_public_key(key_info: KeyInfo) -> str | None:
        """Get the public key content."""
        public_filepath = os.path.join(SSH_DIR, key_info.name + ".pub")
        if not os.path.isfile(public_filepath):
            return None

        try:
            with open(public_filepath, "r") as f:
                return f.read().strip()
        except Exception:
            return None

    @staticmethod
    def delete_key(key_info: KeyInfo) -> tuple[bool, list[str]]:
        """Delete a key pair.

        Returns:
            Tuple of (success, list of errors).
        """
        errors: list[str] = []

        # Delete private key
        if key_info.has_private:
            try:
                os.remove(key_info.path)
            except Exception as e:
                errors.append(f"{key_info.name}: {str(e)}")

        # Delete public key
        if key_info.has_public:
            public_path = os.path.join(SSH_DIR, key_info.name + ".pub")
            try:
                os.remove(public_path)
            except Exception as e:
                errors.append(f"{key_info.name}.pub: {str(e)}")

        return len(errors) == 0, errors

    @staticmethod
    def generate_key(algorithm: str, size: str, comment: str, passphrase: str) -> tuple[bool, str]:
        """Generate a new SSH key.

        Returns:
            Tuple of (success, error_message).
        """
        # Determine key filename
        key_name = f"id_{algorithm}"
        key_path = os.path.join(SSH_DIR, key_name)

        # Build ssh-keygen command
        cmd = ["ssh-keygen", "-t", algorithm]

        # Add size for RSA/ECDSA
        if algorithm in ("rsa", "ecdsa"):
            cmd.extend(["-b", size])

        # Add comment
        if comment:
            cmd.extend(["-C", comment])

        # Add output file
        cmd.extend(["-f", key_path])

        # Add passphrase (empty means no passphrase)
        cmd.extend(["-N", passphrase])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return True, ""
            else:
                return False, result.stderr.strip() or "Unknown error"
        except Exception as e:
            return False, str(e)