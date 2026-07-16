"""Unit tests for systemd service helpers."""

import json
import subprocess
import unittest
from unittest.mock import MagicMock, patch

from mast.core.services import (
    ServiceEntry,
    build_service_action_command,
    build_service_logs_command,
    list_services,
)


class TestServices(unittest.TestCase):
    @patch("mast.core.services.services.subprocess.run")
    def test_list_services_sorts_active_first(self, mock_run: MagicMock) -> None:
        responses = [
            [
                {
                    "unit": "beta.service",
                    "active": "inactive",
                    "sub": "dead",
                    "description": "Beta service",
                },
                {
                    "unit": "alpha.service",
                    "active": "active",
                    "sub": "running",
                    "description": "Alpha service",
                },
            ],
            [
                {"unit_file": "alpha.service", "state": "enabled"},
                {"unit_file": "beta.service", "state": "disabled"},
            ],
            [
                {
                    "unit": "gamma.service",
                    "active": "failed",
                    "sub": "failed",
                    "description": "Gamma service",
                }
            ],
            [{"unit_file": "gamma.service", "state": "enabled"}],
        ]

        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(payload))
            for payload in responses
        ]

        services = list_services()

        self.assertEqual([service.name for service in services], ["alpha.service", "gamma.service", "beta.service"])
        self.assertEqual(services[0].enabled_state, "enabled")
        self.assertEqual(services[2].scope, "system")

    @patch("mast.core.services.services.subprocess.run")
    def test_list_services_skips_failing_scope(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = [
            subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps([
                    {
                        "unit": "alpha.service",
                        "active": "active",
                        "sub": "running",
                        "description": "Alpha service",
                    }
                ]),
            ),
            subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps([
                    {"unit_file": "alpha.service", "state": "enabled"}
                ]),
            ),
            subprocess.CalledProcessError(returncode=1, cmd=["systemctl", "--user"]),
        ]

        services = list_services()

        self.assertEqual(len(services), 1)
        self.assertEqual(services[0].name, "alpha.service")

    def test_build_action_command_uses_pkexec_for_system_scope(self) -> None:
        service = ServiceEntry(
            name="sshd.service",
            scope="system",
            active_state="active",
            sub_state="running",
            enabled_state="enabled",
            description="OpenSSH server daemon",
        )

        command = build_service_action_command(service, "stop")

        self.assertEqual(command, ["pkexec", "systemctl", "stop", "sshd.service"])

    def test_build_logs_command_uses_user_journal_when_needed(self) -> None:
        service = ServiceEntry(
            name="pipewire.service",
            scope="user",
            active_state="active",
            sub_state="running",
            enabled_state="enabled",
            description="PipeWire Multimedia Service",
        )

        command = build_service_logs_command(service, lines=50)

        self.assertEqual(
            command,
            ["journalctl", "--user", "-u", "pipewire.service", "-n", "50", "--no-pager"],
        )


if __name__ == "__main__":
    unittest.main()