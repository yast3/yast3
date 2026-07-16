"""Unit tests for the languages module."""

import os
import unittest
from unittest.mock import MagicMock, patch

from mast.core.languages import (
    DEFAULT_FALLBACK_LANGUAGE,
    LanguageInfo,
    LanguageSettings,
    remove_suffix,
    is_cjk_language,
    main_language,
    get_language_country,
    is_supported_by_fbiterm,
    is_fbiterm,
    is_supported_language,
    get_locale_string,
)


class TestLanguageConstants(unittest.TestCase):
    """Tests for language constants."""

    def test_default_fallback_language(self) -> None:
        """DEFAULT_FALLBACK_LANGUAGE should be 'en_US'."""
        self.assertEqual(DEFAULT_FALLBACK_LANGUAGE, "en_US")


class TestLanguageInfo(unittest.TestCase):
    """Tests for LanguageInfo dataclass."""

    def test_language_info_creation(self) -> None:
        """LanguageInfo should be created with correct attributes."""
        info = LanguageInfo(
            code="en_US",
            name="English (US)",
            name_ascii="English (US)",
            name_english="English (US)",
            timezone="America/New_York",
            keyboard="us",
            encoding_utf8=".UTF-8",
            encoding_non_utf8="",
        )
        self.assertEqual(info.code, "en_US")
        self.assertEqual(info.name, "English (US)")
        self.assertEqual(info.timezone, "America/New_York")
        self.assertEqual(info.keyboard, "us")


class TestLanguageSettings(unittest.TestCase):
    """Tests for LanguageSettings dataclass."""

    def test_language_settings_defaults(self) -> None:
        """LanguageSettings should have correct defaults."""
        settings = LanguageSettings()
        self.assertEqual(settings.language, DEFAULT_FALLBACK_LANGUAGE)
        self.assertEqual(settings.use_utf8, True)
        self.assertEqual(settings.locales, {})


class TestRemoveSuffix(unittest.TestCase):
    """Tests for remove_suffix function."""

    def test_remove_utf8_suffix(self) -> None:
        """Should remove .UTF-8 suffix."""
        self.assertEqual(remove_suffix("en_US.UTF-8"), "en_US")

    def test_remove_at_suffix(self) -> None:
        """Should remove @euro suffix."""
        self.assertEqual(remove_suffix("de_DE@euro"), "de_DE")

    def test_no_suffix(self) -> None:
        """Should return unchanged when no suffix."""
        self.assertEqual(remove_suffix("en_US"), "en_US")

    def test_empty_string(self) -> None:
        """Should handle empty string."""
        self.assertEqual(remove_suffix(""), "")


class TestIsCJKLanguage(unittest.TestCase):
    """Tests for is_cjk_language function."""

    def test_chinese_is_cjk(self) -> None:
        """Chinese should be CJK."""
        self.assertTrue(is_cjk_language("zh_CN"))
        self.assertTrue(is_cjk_language("zh_TW"))

    def test_japanese_is_cjk(self) -> None:
        """Japanese should be CJK."""
        self.assertTrue(is_cjk_language("ja_JP"))

    def test_korean_is_cjk(self) -> None:
        """Korean should be CJK."""
        self.assertTrue(is_cjk_language("ko_KR"))

    def test_english_is_not_cjk(self) -> None:
        """English should not be CJK."""
        self.assertFalse(is_cjk_language("en_US"))

    def test_german_is_not_cjk(self) -> None:
        """German should not be CJK."""
        self.assertFalse(is_cjk_language("de_DE"))


class TestMainLanguage(unittest.TestCase):
    """Tests for main_language function."""

    def test_extract_main_language(self) -> None:
        """Should extract main language code."""
        self.assertEqual(main_language("en_US.UTF-8"), "en")
        self.assertEqual(main_language("de_DE@euro"), "de")
        self.assertEqual(main_language("zh_CN"), "zh")

    def test_empty_string(self) -> None:
        """Should return empty for empty input."""
        self.assertEqual(main_language(""), "")

    def test_none_input(self) -> None:
        """Should return empty for None input."""
        self.assertEqual(main_language(None), "")


class TestGetLanguageCountry(unittest.TestCase):
    """Tests for get_language_country function."""

    def test_extract_country(self) -> None:
        """Should extract country code."""
        self.assertEqual(get_language_country("de_DE@UTF-8"), "DE")
        self.assertEqual(get_language_country("en_US.UTF-8"), "US")
        self.assertEqual(get_language_country("zh_CN"), "CN")

    def test_language_only_no_country(self) -> None:
        """Should return language code uppercase when no country."""
        self.assertEqual(get_language_country("en"), "EN")
        self.assertEqual(get_language_country("de"), "DE")


class TestIsSupportedByFbiterm(unittest.TestCase):
    """Tests for is_supported_by_fbiterm function."""

    def test_english_supported(self) -> None:
        """English should be supported by fbiterm."""
        self.assertTrue(is_supported_by_fbiterm("en_US"))

    def test_german_supported(self) -> None:
        """German should be supported by fbiterm."""
        self.assertTrue(is_supported_by_fbiterm("de_DE"))

    def test_arabic_not_supported(self) -> None:
        """Arabic should not be supported by fbiterm."""
        self.assertFalse(is_supported_by_fbiterm("ar_SA"))

    def test_hindi_not_supported(self) -> None:
        """Hindi should not be supported by fbiterm."""
        self.assertFalse(is_supported_by_fbiterm("hi_IN"))


class TestIsFbiterm(unittest.TestCase):
    """Tests for is_fbiterm function."""

    @patch.dict(os.environ, {"TERM": "iterm"}, clear=False)
    def test_is_fbiterm_true(self) -> None:
        """Should return True when TERM is iterm."""
        self.assertTrue(is_fbiterm())

    @patch.dict(os.environ, {"TERM": "xterm"}, clear=False)
    def test_is_fbiterm_false(self) -> None:
        """Should return False when TERM is not iterm."""
        self.assertFalse(is_fbiterm())

    @patch.dict(os.environ, {}, clear=True)
    def test_is_fbiterm_no_term(self) -> None:
        """Should return False when TERM is not set."""
        self.assertFalse(is_fbiterm())


class TestIsSupportedLanguage(unittest.TestCase):
    """Tests for is_supported_language function."""

    @patch("mast.core.languages.languages._is_text_mode", return_value=False)
    def test_gui_mode_all_supported(self, mock_text_mode: MagicMock) -> None:
        """In GUI mode, all languages should be supported."""
        self.assertTrue(is_supported_language("zh_CN"))
        self.assertTrue(is_supported_language("en_US"))

    @patch("mast.core.languages.languages._is_text_mode", return_value=True)
    @patch("mast.core.languages.languages.is_fbiterm", return_value=True)
    @patch("mast.core.languages.languages.is_supported_by_fbiterm", return_value=True)
    def test_fbiterm_supported(self, mock_supported: MagicMock, mock_fbiterm: MagicMock, mock_text: MagicMock) -> None:
        """In fbiterm mode, supported languages should be supported."""
        self.assertTrue(is_supported_language("en_US"))

    @patch("mast.core.languages.languages._is_text_mode", return_value=True)
    @patch("mast.core.languages.languages.is_fbiterm", return_value=True)
    @patch("mast.core.languages.languages.is_supported_by_fbiterm", return_value=False)
    def test_fbiterm_not_supported(self, mock_supported: MagicMock, mock_fbiterm: MagicMock, mock_text: MagicMock) -> None:
        """In fbiterm mode, unsupported languages should not be supported."""
        self.assertFalse(is_supported_language("ar_SA"))

    @patch("mast.core.languages.languages._is_text_mode", return_value=True)
    @patch("mast.core.languages.languages.is_fbiterm", return_value=False)
    @patch("mast.core.languages.languages.is_cjk_language", return_value=True)
    def test_non_fbiterm_cjk_not_supported(self, mock_cjk: MagicMock, mock_fbiterm: MagicMock, mock_text: MagicMock) -> None:
        """In non-fbiterm text mode, CJK languages should not be supported."""
        self.assertFalse(is_supported_language("zh_CN"))

    @patch("mast.core.languages.languages._is_text_mode", return_value=True)
    @patch("mast.core.languages.languages.is_fbiterm", return_value=False)
    @patch("mast.core.languages.languages.is_cjk_language", return_value=False)
    def test_non_fbiterm_non_cjk_supported(self, mock_cjk: MagicMock, mock_fbiterm: MagicMock, mock_text: MagicMock) -> None:
        """In non-fbiterm text mode, non-CJK languages should be supported."""
        self.assertTrue(is_supported_language("en_US"))


class TestGetLocaleString(unittest.TestCase):
    """Tests for get_locale_string function."""

    def test_utf8_locale(self) -> None:
        """Should append .UTF-8 suffix when use_utf8 is True."""
        self.assertEqual(get_locale_string("en_US", use_utf8=True), "en_US.UTF-8")
        self.assertEqual(get_locale_string("de_DE", use_utf8=True), "de_DE.UTF-8")

    def test_non_utf8_locale(self) -> None:
        """Should not append suffix when use_utf8 is False."""
        self.assertEqual(get_locale_string("en_US", use_utf8=False), "en_US")

    def test_already_has_suffix(self) -> None:
        """Should return unchanged when suffix already present."""
        self.assertEqual(get_locale_string("en_US.UTF-8"), "en_US.UTF-8")
        self.assertEqual(get_locale_string("de_DE@euro"), "de_DE@euro")


if __name__ == "__main__":
    unittest.main()