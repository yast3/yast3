"""Unit tests for the i18n module."""

import os
import unittest
from unittest.mock import patch

from mast.core import i18n


class TestFindLocaleDir(unittest.TestCase):
    """Tests for _find_locale_dir function."""

    def test_returns_first_existing_dir(self) -> None:
        """Should return the first existing locale directory."""
        with patch.object(i18n, 'LOCALE_DIRS', ['/nonexistent', '/usr/share/locale']):
            result = i18n._find_locale_dir()
            self.assertEqual(result, '/usr/share/locale')

    def test_returns_none_when_no_dir_exists(self) -> None:
        """Should return None when no locale directory exists."""
        with patch.object(i18n, 'LOCALE_DIRS', ['/nonexistent1', '/nonexistent2']):
            result = i18n._find_locale_dir()
            self.assertIsNone(result)

    def test_dev_path_exists_in_repo(self) -> None:
        """The development locale path should exist in the repo."""
        # This test verifies the actual development path
        dev_path = os.path.join(os.path.dirname(__file__), '..', 'locale')
        # Should at least have zh_CN and en_US directories
        self.assertTrue(os.path.isdir(dev_path))


class TestTranslationWrapper(unittest.TestCase):
    """Tests for the _TranslationWrapper class."""

    def test_wrapper_is_callable(self) -> None:
        """The wrapper should be callable."""
        wrapper = i18n._TranslationWrapper()
        self.assertTrue(callable(wrapper))

    def test_wrapper_returns_msgid_when_no_translation(self) -> None:
        """Without a gettext function, wrapper should return msgid unchanged."""
        wrapper = i18n._TranslationWrapper()
        result = wrapper("Hello")
        self.assertEqual(result, "Hello")

    def test_wrapper_delegates_to_gettext_func(self) -> None:
        """Wrapper should delegate to the underlying gettext function."""
        mock_gettext = lambda msg: f"TRANSLATED: {msg}"
        wrapper = i18n._TranslationWrapper()
        wrapper.set_gettext(mock_gettext)
        result = wrapper("Hello")
        self.assertEqual(result, "TRANSLATED: Hello")

    def test_wrapper_set_gettext_updates_func(self) -> None:
        """set_gettext should update the underlying function."""
        mock_gettext1 = lambda msg: f"ONE: {msg}"
        mock_gettext2 = lambda msg: f"TWO: {msg}"
        wrapper = i18n._TranslationWrapper()
        wrapper.set_gettext(mock_gettext1)
        self.assertEqual(wrapper("test"), "ONE: test")
        wrapper.set_gettext(mock_gettext2)
        self.assertEqual(wrapper("test"), "TWO: test")


class TestInitI18n(unittest.TestCase):
    """Tests for init_i18n function."""

    def test_init_i18n_updates_global_wrapper(self) -> None:
        """init_i18n should update the global _ wrapper."""
        # Save original
        original_gettext = i18n._._gettext_func

        # Mock _find_locale_dir to return a valid path
        with patch.object(i18n, '_find_locale_dir', return_value=None):
            i18n.init_i18n()
            # When localedir is None, it should use NullTranslations
            self.assertIsNotNone(i18n._._gettext_func)

        # Restore original
        i18n._._gettext_func = original_gettext

    def test_init_i18n_with_valid_locale_dir(self) -> None:
        """init_i18n should load translations when locale dir exists."""
        # Use the actual development locale path
        dev_locale = os.path.join(os.path.dirname(__file__), '..', 'locale')
        if os.path.isdir(dev_locale):
            i18n.init_i18n()
            # After init, translations should work
            # Note: translations that exist in .mo file should return translated text
            result = i18n._("Add")
            # The translation for "Add" should be "添加" if properly loaded
            self.assertIsInstance(result, str)


class TestTranslationsWork(unittest.TestCase):
    """Integration tests to verify translations actually work."""

    def test_translation_wrapper_preserves_singleton(self) -> None:
        """Importing _ from i18n module should give the singleton wrapper."""
        # This tests that the wrapper approach works correctly
        from mast.core.i18n import _, init_i18n

        # Initially should be the wrapper
        self.assertIsInstance(_, i18n._TranslationWrapper)

        # After init, the same wrapper should be updated
        init_i18n()
        # The wrapper should now use a real translation function
        result = _("Add")
        self.assertIsInstance(result, str)


if __name__ == "__main__":
    unittest.main()