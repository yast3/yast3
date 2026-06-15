"""SSH Keys manager - handles key operations and logic."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from typing import List, Tuple, Optional

from yast3.modules.ssh.ssh import SSH_CONFIG_DIR


@dataclass
class KeyInfo:
    """Represents SSH key information."""
    name: str
    algorithm: str
    size: str
    fingerprint: str
    comment: str
    has_passphrase: bool
    has_public: bool
    has_private: bool
    private_path: str
    public_path: str


class KeyManager:
    """Manages SSH key operations."""

    @staticmethod
    def _get_key_info(name: str) -> Tuple[str, str, str, str]:
        """Get key size, algorithm, fingerprint and comment using ssh-keygen."""
        size = "N/A"
        algorithm = "Unknown"
        fingerprint = ""
        comment = ""
        
        private_path = os.path.join(SSH_CONFIG_DIR, name)
        public_path = os.path.join(SSH_CONFIG_DIR, name + '.pub')
        has_public = os.path.exists(public_path)
        
        # Use public key file if available
        filepath = public_path if has_public else private_path
        
        if os.path.exists(filepath):
            try:
                result = subprocess.run(
                    ['ssh-keygen', '-l', '-f', filepath],
                    capture_output=True,
                    text=True,
                    check=True
                )
                output = result.stdout.strip()
                if output:
                    # Output format: "256 SHA256:xxx user@hostname (ED25519)"
                    parts = output.split()
                    if len(parts) >= 3:
                        size = parts[0]
                        fingerprint = parts[1]
                        # Algorithm is in parentheses at the end
                        if len(parts) > 3:
                            last_part = parts[-1]
                            if last_part.startswith('(') and last_part.endswith(')'):
                                algorithm = last_part[1:-1]
                            # Comment is everything between fingerprint and algorithm
                            comment = ' '.join(parts[2:-1])
            except Exception:
                # Fallback to file-based detection if ssh-keygen fails
                size, algorithm, comment = KeyManager._fallback_key_info(name)
        
        return (size, algorithm, fingerprint, comment)

    @staticmethod
    def _fallback_key_info(name: str) -> Tuple[str, str, str]:
        """Fallback key detection using file content."""
        size = "N/A"
        algorithm = "Unknown"
        comment = ""
        
        private_path = os.path.join(SSH_CONFIG_DIR, name)
        public_path = os.path.join(SSH_CONFIG_DIR, name + '.pub')
        has_public = os.path.exists(public_path)
        
        filepath = public_path if has_public else private_path
        
        try:
            with open(filepath, 'r') as f:
                first_line = f.readline().strip()
            
            if first_line.startswith('-----BEGIN RSA PRIVATE KEY-----'):
                algorithm = 'RSA'
            elif first_line.startswith('-----BEGIN DSA PRIVATE KEY-----'):
                algorithm = 'DSA'
            elif first_line.startswith('-----BEGIN EC PRIVATE KEY-----'):
                algorithm = 'EC'
            elif first_line.startswith('-----BEGIN OPENSSH PRIVATE KEY-----'):
                algorithm = 'OpenSSH'
            elif first_line.startswith('ssh-rsa '):
                algorithm = 'RSA'
            elif first_line.startswith('ssh-dss '):
                algorithm = 'DSA'
            elif first_line.startswith('ecdsa-sha2-'):
                algorithm = 'EC'
            elif first_line.startswith('ssh-ed25519 '):
                algorithm = 'ED25519'
            
            # Get comment from public key
            if has_public:
                with open(public_path, 'r') as f:
                    content = f.read().strip()
                    parts = content.split()
                    if len(parts) >= 3:
                        comment = ' '.join(parts[2:])
        except Exception:
            pass
        
        return (size, algorithm, comment)

    @staticmethod
    def _has_passphrase(private_path: str) -> bool:
        """Check if the private key is encrypted (has passphrase)."""
        if os.path.exists(private_path):
            try:
                with open(private_path, 'r') as f:
                    first_line = f.readline().strip()
                    # Check for encrypted private key markers
                    if first_line.startswith('-----BEGIN') and 'ENCRYPTED' in first_line:
                        return True
                    # OpenSSH format
                    if first_line.startswith('-----BEGIN OPENSSH PRIVATE KEY-----'):
                        # Read second line for encryption info
                        lines = f.readlines()
                        for line in lines[:5]:  # Check first few lines
                            if line.startswith('Proc-Type: 4,ENCRYPTED'):
                                return True
            except Exception:
                pass
        return False

    @staticmethod
    def _get_public_key_content(public_path: str) -> Optional[str]:
        """Get the content of the public key file."""
        if os.path.exists(public_path):
            try:
                with open(public_path, 'r') as f:
                    return f.read().strip()
            except Exception:
                return None
        return None

    @staticmethod
    def list_keys() -> List[KeyInfo]:
        """List all SSH keys in ~/.ssh/ directory."""
        keys: List[KeyInfo] = []
        
        try:
            files = os.listdir(SSH_CONFIG_DIR)
        except (FileNotFoundError, PermissionError):
            return keys

        # Find private key files (without .pub extension)
        private_keys = set()
        for filename in files:
            filepath = os.path.join(SSH_CONFIG_DIR, filename)
            if os.path.isdir(filepath) or filename in ('known_hosts', 'config', 'authorized_keys'):
                continue
            
            # Skip public key files - we'll match them with their private keys
            if filename.endswith('.pub'):
                continue
            
            # Check if it looks like a key file
            if filename.endswith(('_rsa', '_dsa', '_ecdsa', '_ed25519')) or \
               filename.startswith('id_'):
                private_keys.add(filename)

        # Also check for .pub files that might not have corresponding private keys
        public_keys = set()
        for filename in files:
            if filename.endswith('.pub'):
                base_name = filename[:-4]  # Remove .pub
                filepath = os.path.join(SSH_CONFIG_DIR, filename)
                if os.path.isfile(filepath) and base_name not in private_keys:
                    public_keys.add(base_name)

        # Combine and create key info objects
        all_keys = sorted(private_keys.union(public_keys))
        for name in all_keys:
            private_path = os.path.join(SSH_CONFIG_DIR, name)
            public_path = os.path.join(SSH_CONFIG_DIR, name + '.pub')
            has_private = os.path.exists(private_path)
            has_public = os.path.exists(public_path)
            
            size, algorithm, fingerprint, comment = KeyManager._get_key_info(name)
            has_passphrase = KeyManager._has_passphrase(private_path) if has_private else False
            
            keys.append(KeyInfo(
                name=name,
                algorithm=algorithm,
                size=size,
                fingerprint=fingerprint,
                comment=comment,
                has_passphrase=has_passphrase,
                has_public=has_public,
                has_private=has_private,
                private_path=private_path,
                public_path=public_path
            ))
        
        return keys

    @staticmethod
    def get_public_key(key_info: KeyInfo) -> Optional[str]:
        """Get the public key content."""
        return KeyManager._get_public_key_content(key_info.public_path)

    @staticmethod
    def delete_key(key_info: KeyInfo) -> Tuple[bool, List[str]]:
        """Delete the key pair. Returns (success, error_list)."""
        errors: List[str] = []
        
        if key_info.has_private:
            try:
                os.remove(key_info.private_path)
            except Exception as e:
                errors.append(f"{key_info.name}: {str(e)}")
        
        if key_info.has_public:
            try:
                os.remove(key_info.public_path)
            except Exception as e:
                errors.append(f"{key_info.name}.pub: {str(e)}")
        
        return (len(errors) == 0, errors)
