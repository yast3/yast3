"""Unit tests for Flatpak runtime management core logic."""

import unittest
from subprocess import CompletedProcess
from unittest.mock import patch

from yast3.core.flatpak.runtime import list_flatpak_runtimes, uninstall_flatpak_runtime


class TestListFlatpakRuntimes(unittest.TestCase):
    """Tests for list_flatpak_runtimes function."""

    @patch("yast3.core.flatpak.runtime.shutil.which")
    def test_returns_empty_when_flatpak_missing(self, mock_which) -> None:
        mock_which.return_value = None

        runtimes = list_flatpak_runtimes()

        self.assertEqual(runtimes, [])

    @patch("yast3.core.flatpak.runtime.subprocess.run")
    @patch("yast3.core.flatpak.runtime.shutil.which")
    def test_parses_runtime_list_output(self, mock_which, mock_run) -> None:
        mock_which.return_value = "/usr/bin/flatpak"
        mock_run.return_value = CompletedProcess(
            args=["flatpak", "list"],
            returncode=0,
            stdout=(
                "org.freedesktop.Platform\tFreedesktop Platform\tBase runtime\t24.08\t24.08\tflathub\t977.5 MB\tsystem\n"
                "org.gnome.Platform\tGNOME Platform\tGNOME runtime\t47\t47\tflathub\t1.2 GB\tuser\n"
            ),
            stderr="",
        )

        runtimes = list_flatpak_runtimes()

        self.assertEqual(len(runtimes), 2)
        self.assertEqual(runtimes[0].runtime_id, "org.freedesktop.Platform")
        self.assertEqual(runtimes[0].remote, "flathub")
        self.assertEqual(runtimes[0].installed_size, "977.5 MB")
        self.assertEqual(runtimes[0].scope, "system")
        self.assertEqual(runtimes[1].runtime_id, "org.gnome.Platform")
        self.assertEqual(runtimes[1].installed_size, "1.2 GB")
        self.assertEqual(runtimes[1].scope, "user")


class TestUninstallFlatpakRuntime(unittest.TestCase):
    """Tests for uninstall_flatpak_runtime function."""

    @patch("yast3.core.flatpak.runtime.subprocess.run")
    def test_uninstall_uses_pkexec_for_system_scope(self, mock_run) -> None:
        mock_run.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

        uninstall_flatpak_runtime("org.freedesktop.Platform", "system")

        mock_run.assert_called_once_with(
            ["pkexec", "flatpak", "uninstall", "-y", "--system", "org.freedesktop.Platform"],
            capture_output=True,
            text=True,
        )

    @patch("yast3.core.flatpak.runtime.subprocess.run")
    def test_uninstall_without_pkexec_for_user_scope(self, mock_run) -> None:
        mock_run.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

        uninstall_flatpak_runtime("org.gnome.Platform", "user")

        mock_run.assert_called_once_with(
            ["flatpak", "uninstall", "-y", "--user", "org.gnome.Platform"],
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
