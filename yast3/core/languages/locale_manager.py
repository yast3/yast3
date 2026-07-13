"""Locale management using zypper commands."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import dotenv

from yast3.core.languages import read_sysconfig_language


SYSCONFIG_LANGUAGE_FILE = "/etc/sysconfig/language"


@dataclass
class LocaleItem:
    code: str
    name: str
    installed: bool


ALL_LOCALES = [
    ("af_ZA", "Afrikaans (South Africa)"),
    ("am_ET", "Amharic (Ethiopia)"),
    ("ar_AE", "Arabic (UAE)"),
    ("ar_BH", "Arabic (Bahrain)"),
    ("ar_DZ", "Arabic (Algeria)"),
    ("ar_EG", "Arabic (Egypt)"),
    ("ar_IN", "Arabic (India)"),
    ("ar_IQ", "Arabic (Iraq)"),
    ("ar_JO", "Arabic (Jordan)"),
    ("ar_KW", "Arabic (Kuwait)"),
    ("ar_LB", "Arabic (Lebanon)"),
    ("ar_LY", "Arabic (Libya)"),
    ("ar_MA", "Arabic (Morocco)"),
    ("ar_OM", "Arabic (Oman)"),
    ("ar_QA", "Arabic (Qatar)"),
    ("ar_SA", "Arabic (Saudi Arabia)"),
    ("ar_SY", "Arabic (Syria)"),
    ("ar_TN", "Arabic (Tunisia)"),
    ("ar_YE", "Arabic (Yemen)"),
    ("ast_ES", "Asturian (Spain)"),
    ("be_BY", "Belarusian (Belarus)"),
    ("bg_BG", "Bulgarian (Bulgaria)"),
    ("bn_IN", "Bengali (India)"),
    ("br_FR", "Breton (France)"),
    ("bs_BA", "Bosnian (Bosnia and Herzegovina)"),
    ("ca_ES", "Catalan (Spain)"),
    ("cs_CZ", "Czech (Czech Republic)"),
    ("cy_GB", "Welsh (United Kingdom)"),
    ("da_DK", "Danish (Denmark)"),
    ("de_AT", "German (Austria)"),
    ("de_BE", "German (Belgium)"),
    ("de_CH", "German (Switzerland)"),
    ("de_DE", "German (Germany)"),
    ("de_LU", "German (Luxembourg)"),
    ("el_GR", "Greek (Greece)"),
    ("en_AU", "English (Australia)"),
    ("en_CA", "English (Canada)"),
    ("en_GB", "English (United Kingdom)"),
    ("en_HK", "English (Hong Kong)"),
    ("en_IE", "English (Ireland)"),
    ("en_IN", "English (India)"),
    ("en_NZ", "English (New Zealand)"),
    ("en_PH", "English (Philippines)"),
    ("en_SG", "English (Singapore)"),
    ("en_US", "English (United States)"),
    ("en_ZA", "English (South Africa)"),
    ("eo", "Esperanto"),
    ("es_AR", "Spanish (Argentina)"),
    ("es_BO", "Spanish (Bolivia)"),
    ("es_CL", "Spanish (Chile)"),
    ("es_CO", "Spanish (Colombia)"),
    ("es_CR", "Spanish (Costa Rica)"),
    ("es_DO", "Spanish (Dominican Republic)"),
    ("es_EC", "Spanish (Ecuador)"),
    ("es_ES", "Spanish (Spain)"),
    ("es_GT", "Spanish (Guatemala)"),
    ("es_HN", "Spanish (Honduras)"),
    ("es_MX", "Spanish (Mexico)"),
    ("es_NI", "Spanish (Nicaragua)"),
    ("es_PA", "Spanish (Panama)"),
    ("es_PE", "Spanish (Peru)"),
    ("es_PR", "Spanish (Puerto Rico)"),
    ("es_PY", "Spanish (Paraguay)"),
    ("es_SV", "Spanish (El Salvador)"),
    ("es_US", "Spanish (United States)"),
    ("es_UY", "Spanish (Uruguay)"),
    ("es_VE", "Spanish (Venezuela)"),
    ("et_EE", "Estonian (Estonia)"),
    ("eu_ES", "Basque (Spain)"),
    ("fa_IR", "Persian (Iran)"),
    ("fi_FI", "Finnish (Finland)"),
    ("fil_PH", "Filipino (Philippines)"),
    ("fr_BE", "French (Belgium)"),
    ("fr_CA", "French (Canada)"),
    ("fr_CH", "French (Switzerland)"),
    ("fr_FR", "French (France)"),
    ("fr_LU", "French (Luxembourg)"),
    ("fr_MC", "French (Monaco)"),
    ("fr_SG", "French (Singapore)"),
    ("ga_IE", "Irish (Ireland)"),
    ("gl_ES", "Galician (Spain)"),
    ("gu_IN", "Gujarati (India)"),
    ("he_IL", "Hebrew (Israel)"),
    ("hi_IN", "Hindi (India)"),
    ("hr_HR", "Croatian (Croatia)"),
    ("hu_HU", "Hungarian (Hungary)"),
    ("hy_AM", "Armenian (Armenia)"),
    ("id_ID", "Indonesian (Indonesia)"),
    ("is_IS", "Icelandic (Iceland)"),
    ("it_CH", "Italian (Switzerland)"),
    ("it_IT", "Italian (Italy)"),
    ("ja_JP", "Japanese (Japan)"),
    ("ka_GE", "Georgian (Georgia)"),
    ("kk_KZ", "Kazakh (Kazakhstan)"),
    ("km_KH", "Khmer (Cambodia)"),
    ("kn_IN", "Kannada (India)"),
    ("ko_KR", "Korean (South Korea)"),
    ("ku_TR", "Kurdish (Turkey)"),
    ("ky_KG", "Kyrgyz (Kyrgyzstan)"),
    ("lo_LA", "Lao (Laos)"),
    ("lt_LT", "Lithuanian (Lithuania)"),
    ("lv_LV", "Latvian (Latvia)"),
    ("mk_MK", "Macedonian (North Macedonia)"),
    ("ml_IN", "Malayalam (India)"),
    ("mn_MN", "Mongolian (Mongolia)"),
    ("mr_IN", "Marathi (India)"),
    ("ms_MY", "Malay (Malaysia)"),
    ("mt_MT", "Maltese (Malta)"),
    ("nb_NO", "Norwegian Bokmal (Norway)"),
    ("ne_NP", "Nepali (Nepal)"),
    ("nl_BE", "Dutch (Belgium)"),
    ("nl_NL", "Dutch (Netherlands)"),
    ("nn_NO", "Norwegian Nynorsk (Norway)"),
    ("pl_PL", "Polish (Poland)"),
    ("pt_BR", "Portuguese (Brazil)"),
    ("pt_PT", "Portuguese (Portugal)"),
    ("ro_RO", "Romanian (Romania)"),
    ("ru_RU", "Russian (Russia)"),
    ("si_LK", "Sinhala (Sri Lanka)"),
    ("sk_SK", "Slovak (Slovakia)"),
    ("sl_SI", "Slovenian (Slovenia)"),
    ("sr_RS", "Serbian (Serbia)"),
    ("sv_FI", "Swedish (Finland)"),
    ("sv_SE", "Swedish (Sweden)"),
    ("ta_IN", "Tamil (India)"),
    ("te_IN", "Telugu (India)"),
    ("th_TH", "Thai (Thailand)"),
    ("tr_TR", "Turkish (Turkey)"),
    ("uk_UA", "Ukrainian (Ukraine)"),
    ("ur_PK", "Urdu (Pakistan)"),
    ("uz_UZ", "Uzbek (Uzbekistan)"),
    ("vi_VN", "Vietnamese (Vietnam)"),
    ("zh_CN", "Chinese (China)"),
    ("zh_HK", "Chinese (Hong Kong)"),
    ("zh_TW", "Chinese (Taiwan)"),
]


def _read_installed_languages() -> set[str]:
    """Read INSTALLED_LANGUAGES from /etc/sysconfig/language."""
    installed = set()
    languages_str = read_sysconfig_language()
    for lang in languages_str.replace(",", " ").split():
        lang = lang.strip()
        if lang:
            installed.add(lang)
    return installed


def _update_installed_languages(locale_code: str, add: bool) -> None:
    """Update INSTALLED_LANGUAGES in /etc/sysconfig/language."""
    installed = _read_installed_languages()
    if add:
        installed.add(locale_code)
    else:
        installed.discard(locale_code)
    languages_str = " ".join(sorted(installed))
    if Path(SYSCONFIG_LANGUAGE_FILE).exists():
        try:
            dotenv.set_key(SYSCONFIG_LANGUAGE_FILE, "INSTALLED_LANGUAGES", languages_str, quote_mode="always")
        except (PermissionError, IOError):
            pass


def get_all_locales() -> list[LocaleItem]:
    """Get all available locales from the predefined list."""
    installed_codes = _read_installed_languages()
    locales = [
        LocaleItem(code=code, name=name, installed=code in installed_codes)
        for code, name in ALL_LOCALES
    ]
    return sorted(locales, key=lambda x: (not x.installed, x.name))


def get_installed_locales() -> list[LocaleItem]:
    """Get installed locales."""
    installed_codes = _read_installed_languages()
    return [
        LocaleItem(code=code, name=name, installed=True)
        for code, name in ALL_LOCALES
        if code in installed_codes
    ]


def get_locales_with_status() -> list[LocaleItem]:
    """Get all locales with installation status."""
    return get_all_locales()


def build_locale_install_command(locale_code: str) -> list[str]:
    """Build command for installing a locale."""
    return ["pkexec", "zypper", "--no-refresh", "--non-interactive", "addlocale", locale_code]


def build_locale_remove_command(locale_code: str) -> list[str]:
    """Build command for removing a locale."""
    return ["pkexec", "zypper", "--no-refresh", "--non-interactive", "removelocale", locale_code]


def install_locale(locale_code: str) -> tuple[Literal["ok", "permission_denied", "pkexec_failed", "error"], str]:
    """Install a locale using 'pkexec zypper addlocale'."""
    try:
        result = subprocess.run(
            build_locale_install_command(locale_code),
            capture_output=True,
            text=True,
            timeout=120,
        )
        
        if result.returncode == 0:
            _update_installed_languages(locale_code, add=True)
            return ("ok", f"Locale '{locale_code}' installed successfully")
        elif result.returncode == 126 or result.returncode == 127:
            return ("pkexec_failed", "Authentication failed")
        else:
            stderr = result.stderr.strip()
            return ("error", stderr if stderr else f"Failed to install locale '{locale_code}'")
    except FileNotFoundError:
        return ("error", "pkexec or zypper not found")
    except TimeoutError:
        return ("error", "Operation timed out")


def uninstall_locale(locale_code: str) -> tuple[Literal["ok", "permission_denied", "pkexec_failed", "error"], str]:
    """Uninstall a locale using 'pkexec zypper removelocale'."""
    try:
        result = subprocess.run(
            build_locale_remove_command(locale_code),
            capture_output=True,
            text=True,
            timeout=120,
        )
        
        if result.returncode == 0:
            _update_installed_languages(locale_code, add=False)
            return ("ok", f"Locale '{locale_code}' uninstalled successfully")
        elif result.returncode == 126 or result.returncode == 127:
            return ("pkexec_failed", "Authentication failed")
        else:
            stderr = result.stderr.strip()
            return ("error", stderr if stderr else f"Failed to uninstall locale '{locale_code}'")
    except FileNotFoundError:
        return ("error", "pkexec or zypper not found")
    except TimeoutError:
        return ("error", "Operation timed out")