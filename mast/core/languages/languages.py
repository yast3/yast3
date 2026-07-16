"""Language management logic."""

from __future__ import annotations

import dotenv
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

DEFAULT_FALLBACK_LANGUAGE = "en_US"
LOCALE_CONF_FILE = "/etc/locale.conf"
SYSCONFIG_LANGUAGE_FILE = "/etc/sysconfig/language"

CJK_LANGUAGES = [
    "ja",
    "ko",
    "zh",
    "hi",
    "km",
    "pa",
    "bn",
    "gu",
    "mr",
    "si",
    "ta",
    "vi",
]

UNSUPPORTED_FBITERM_LANGS = ["ar", "bn", "gu", "hi", "km", "mr", "pa", "ta", "th"]


@dataclass
class LanguageInfo:
    """Represents language information."""

    code: str
    name: str
    name_ascii: str
    name_english: str
    timezone: str = "US/Eastern"
    keyboard: str = DEFAULT_FALLBACK_LANGUAGE
    encoding_utf8: str = ".UTF-8"
    encoding_non_utf8: str = ""


@dataclass
class LanguageSettings:
    """Represents current language settings."""

    language: str = DEFAULT_FALLBACK_LANGUAGE
    language_on_entry: str = DEFAULT_FALLBACK_LANGUAGE
    preselected: str = DEFAULT_FALLBACK_LANGUAGE
    name: str = "English (US)"
    languages: str = ""
    languages_on_entry: str = ""
    use_utf8: bool = True
    locales: dict[str, int] = field(default_factory=dict)
    languages_map: dict[str, LanguageInfo] = field(default_factory=dict)
    lang2timezone: dict[str, str] = field(default_factory=dict)
    lang2keyboard: dict[str, str] = field(default_factory=dict)
    english_names: dict[str, str] = field(default_factory=dict)


def _parse_locale_code(locale: str) -> tuple[str, str]:
    """Parse locale code into language and country parts."""
    locale = locale.strip()

    suffix_pos = locale.find(".")
    if suffix_pos == -1:
        suffix_pos = locale.find("@")
    if suffix_pos != -1:
        locale = locale[:suffix_pos]

    if "_" in locale:
        parts = locale.split("_", 1)
        return parts[0], parts[1]
    return locale, ""


def _get_language_name(locale: str) -> str:
    """Get human-readable name for a locale."""
    lang_code, country_code = _parse_locale_code(locale)

    language_names = {
        "aa": "Afar",
        "af": "Afrikaans",
        "ak": "Akan",
        "am": "Amharic",
        "an": "Aragonese",
        "ar": "Arabic",
        "as": "Assamese",
        "ast": "Asturian",
        "ay": "Aymara",
        "az": "Azerbaijani",
        "ba": "Bashkir",
        "be": "Belarusian",
        "bg": "Bulgarian",
        "bh": "Bihari",
        "bhb": "Bhojpuri",
        "bn": "Bengali",
        "bo": "Tibetan",
        "br": "Breton",
        "bs": "Bosnian",
        "ca": "Catalan",
        "ce": "Chechen",
        "ch": "Chamorro",
        "co": "Corsican",
        "cr": "Cree",
        "cs": "Czech",
        "cy": "Welsh",
        "da": "Danish",
        "de": "German",
        "dz": "Dzongkha",
        "el": "Greek",
        "en": "English",
        "eo": "Esperanto",
        "es": "Spanish",
        "et": "Estonian",
        "eu": "Basque",
        "fa": "Persian",
        "ff": "Fulah",
        "fi": "Finnish",
        "fj": "Fijian",
        "fo": "Faroese",
        "fr": "French",
        "fy": "Frisian",
        "ga": "Irish",
        "gd": "Scottish Gaelic",
        "gl": "Galician",
        "gn": "Guarani",
        "gu": "Gujarati",
        "gv": "Manx",
        "ha": "Hausa",
        "he": "Hebrew",
        "hi": "Hindi",
        "ho": "Hiri Motu",
        "hr": "Croatian",
        "hsb": "Upper Sorbian",
        "ht": "Haitian",
        "hu": "Hungarian",
        "hy": "Armenian",
        "ia": "Interlingua",
        "id": "Indonesian",
        "ie": "Interlingue",
        "ig": "Igbo",
        "ii": "Sichuan Yi",
        "ik": "Inupiaq",
        "is": "Icelandic",
        "it": "Italian",
        "iu": "Inuktitut",
        "ja": "Japanese",
        "jv": "Javanese",
        "ka": "Georgian",
        "kk": "Kazakh",
        "kl": "Kalaallisut",
        "km": "Khmer",
        "kn": "Kannada",
        "ko": "Korean",
        "ks": "Kashmiri",
        "ku": "Kurdish",
        "kw": "Cornish",
        "ky": "Kyrgyz",
        "la": "Latin",
        "lb": "Luxembourgish",
        "lg": "Ganda",
        "li": "Limburgish",
        "ln": "Lingala",
        "lo": "Lao",
        "ltg": "Latgalian",
        "lt": "Lithuanian",
        "lu": "Luba-Katanga",
        "lv": "Latvian",
        "mg": "Malagasy",
        "mh": "Marshallese",
        "mi": "Maori",
        "mk": "Macedonian",
        "ml": "Malayalam",
        "mn": "Mongolian",
        "mr": "Marathi",
        "ms": "Malay",
        "mt": "Maltese",
        "my": "Burmese",
        "na": "Nauru",
        "nb": "Norwegian Bokmal",
        "nd": "North Ndebele",
        "ne": "Nepali",
        "ng": "Ndonga",
        "nl": "Dutch",
        "nn": "Norwegian Nynorsk",
        "no": "Norwegian",
        "nr": "South Ndebele",
        "nso": "Northern Sotho",
        "ny": "Chichewa",
        "oc": "Occitan",
        "oj": "Ojibwa",
        "om": "Oromo",
        "or": "Oriya",
        "pa": "Panjabi",
        "pi": "Pali",
        "pl": "Polish",
        "ps": "Pashto",
        "pt": "Portuguese",
        "qu": "Quechua",
        "rm": "Romansh",
        "rn": "Rundi",
        "ro": "Romanian",
        "ru": "Russian",
        "rw": "Kinyarwanda",
        "sa": "Sanskrit",
        "sc": "Sardinian",
        "sd": "Sindhi",
        "se": "Northern Sami",
        "sg": "Sango",
        "si": "Sinhala",
        "sk": "Slovak",
        "sl": "Slovenian",
        "sm": "Samoan",
        "sn": "Shona",
        "so": "Somali",
        "sq": "Albanian",
        "sr": "Serbian",
        "ss": "Swati",
        "st": "Southern Sotho",
        "su": "Sundanese",
        "sv": "Swedish",
        "sw": "Swahili",
        "ta": "Tamil",
        "te": "Telugu",
        "tg": "Tajik",
        "th": "Thai",
        "ti": "Tigrinya",
        "tcy": "Tulu",
        "tk": "Turkmen",
        "tl": "Tagalog",
        "tn": "Tswana",
        "to": "Tonga",
        "tr": "Turkish",
        "ts": "Tsonga",
        "tt": "Tatar",
        "tw": "Twi",
        "ty": "Tahitian",
        "ug": "Uyghur",
        "uk": "Ukrainian",
        "ur": "Urdu",
        "uz": "Uzbek",
        "ve": "Venda",
        "vi": "Vietnamese",
        "vo": "Volapuk",
        "wa": "Walloon",
        "wo": "Wolof",
        "xh": "Xhosa",
        "yi": "Yiddish",
        "yo": "Yoruba",
        "za": "Zhuang",
        "zh": "Chinese",
        "zu": "Zulu",
    }

    country_names = {
        "AE": "UAE",
        "AF": "Afghanistan",
        "AG": "Antigua and Barbuda",
        "AI": "Anguilla",
        "AL": "Albania",
        "AM": "Armenia",
        "AO": "Angola",
        "AR": "Argentina",
        "AT": "Austria",
        "AU": "Australia",
        "AW": "Aruba",
        "AZ": "Azerbaijan",
        "BA": "Bosnia and Herzegovina",
        "BB": "Barbados",
        "BD": "Bangladesh",
        "BE": "Belgium",
        "BF": "Burkina Faso",
        "BG": "Bulgaria",
        "BH": "Bahrain",
        "BI": "Burundi",
        "BJ": "Benin",
        "BM": "Bermuda",
        "BN": "Brunei",
        "BO": "Bolivia",
        "BR": "Brazil",
        "BS": "Bahamas",
        "BT": "Bhutan",
        "BW": "Botswana",
        "BY": "Belarus",
        "BZ": "Belize",
        "CA": "Canada",
        "CC": "Cocos Islands",
        "CD": "Congo (DRC)",
        "CF": "Central African Republic",
        "CG": "Congo",
        "CH": "Switzerland",
        "CI": "Cote d'Ivoire",
        "CK": "Cook Islands",
        "CL": "Chile",
        "CM": "Cameroon",
        "CN": "China",
        "CO": "Colombia",
        "CR": "Costa Rica",
        "CU": "Cuba",
        "CV": "Cape Verde",
        "CW": "Curacao",
        "CY": "Cyprus",
        "CZ": "Czech Republic",
        "DE": "Germany",
        "DJ": "Djibouti",
        "DK": "Denmark",
        "DM": "Dominica",
        "DO": "Dominican Republic",
        "DZ": "Algeria",
        "EC": "Ecuador",
        "EE": "Estonia",
        "EG": "Egypt",
        "ER": "Eritrea",
        "ES": "Spain",
        "ET": "Ethiopia",
        "FI": "Finland",
        "FJ": "Fiji",
        "FK": "Falkland Islands",
        "FM": "Micronesia",
        "FO": "Faroe Islands",
        "FR": "France",
        "GA": "Gabon",
        "GB": "United Kingdom",
        "GD": "Grenada",
        "GE": "Georgia",
        "GF": "French Guiana",
        "GH": "Ghana",
        "GI": "Gibraltar",
        "GL": "Greenland",
        "GM": "Gambia",
        "GN": "Guinea",
        "GP": "Guadeloupe",
        "GQ": "Equatorial Guinea",
        "GR": "Greece",
        "GT": "Guatemala",
        "GU": "Guam",
        "GW": "Guinea-Bissau",
        "GY": "Guyana",
        "HK": "Hong Kong",
        "HM": "Heard Island",
        "HN": "Honduras",
        "HR": "Croatia",
        "HT": "Haiti",
        "HU": "Hungary",
        "ID": "Indonesia",
        "IE": "Ireland",
        "IL": "Israel",
        "IN": "India",
        "IO": "British Indian Ocean",
        "IQ": "Iraq",
        "IR": "Iran",
        "IS": "Iceland",
        "IT": "Italy",
        "JM": "Jamaica",
        "JO": "Jordan",
        "JP": "Japan",
        "KE": "Kenya",
        "KG": "Kyrgyzstan",
        "KH": "Cambodia",
        "KI": "Kiribati",
        "KM": "Comoros",
        "KN": "Saint Kitts and Nevis",
        "KP": "North Korea",
        "KR": "South Korea",
        "KW": "Kuwait",
        "KY": "Cayman Islands",
        "KZ": "Kazakhstan",
        "LA": "Laos",
        "LB": "Lebanon",
        "LC": "Saint Lucia",
        "LI": "Liechtenstein",
        "LK": "Sri Lanka",
        "LR": "Liberia",
        "LS": "Lesotho",
        "LT": "Lithuania",
        "LU": "Luxembourg",
        "LV": "Latvia",
        "LY": "Libya",
        "MA": "Morocco",
        "MC": "Monaco",
        "MD": "Moldova",
        "ME": "Montenegro",
        "MG": "Madagascar",
        "MH": "Marshall Islands",
        "MK": "Macedonia",
        "ML": "Mali",
        "MM": "Myanmar",
        "MN": "Mongolia",
        "MO": "Macau",
        "MP": "Northern Mariana Islands",
        "MQ": "Martinique",
        "MR": "Mauritania",
        "MS": "Montserrat",
        "MT": "Malta",
        "MU": "Mauritius",
        "MV": "Maldives",
        "MW": "Malawi",
        "MX": "Mexico",
        "MY": "Malaysia",
        "MZ": "Mozambique",
        "NA": "Namibia",
        "NC": "New Caledonia",
        "NE": "Niger",
        "NF": "Norfolk Island",
        "NG": "Nigeria",
        "NI": "Nicaragua",
        "NL": "Netherlands",
        "NO": "Norway",
        "NP": "Nepal",
        "NR": "Nauru",
        "NU": "Niue",
        "NZ": "New Zealand",
        "OM": "Oman",
        "PA": "Panama",
        "PE": "Peru",
        "PF": "French Polynesia",
        "PG": "Papua New Guinea",
        "PH": "Philippines",
        "PK": "Pakistan",
        "PL": "Poland",
        "PM": "Saint Pierre and Miquelon",
        "PN": "Pitcairn",
        "PR": "Puerto Rico",
        "PS": "Palestine",
        "PT": "Portugal",
        "PW": "Palau",
        "PY": "Paraguay",
        "QA": "Qatar",
        "RE": "Reunion",
        "RO": "Romania",
        "RS": "Serbia",
        "RU": "Russia",
        "RW": "Rwanda",
        "SA": "Saudi Arabia",
        "SB": "Solomon Islands",
        "SC": "Seychelles",
        "SD": "Sudan",
        "SE": "Sweden",
        "SG": "Singapore",
        "SH": "Saint Helena",
        "SI": "Slovenia",
        "SJ": "Svalbard and Jan Mayen",
        "SK": "Slovakia",
        "SL": "Sierra Leone",
        "SM": "San Marino",
        "SN": "Senegal",
        "SO": "Somalia",
        "SR": "Suriname",
        "SS": "South Sudan",
        "ST": "Sao Tome and Principe",
        "SU": "Soviet Union",
        "SV": "El Salvador",
        "SX": "Sint Maarten",
        "SY": "Syria",
        "SZ": "Swaziland",
        "TC": "Turks and Caicos Islands",
        "TD": "Chad",
        "TF": "French Southern Territories",
        "TG": "Togo",
        "TH": "Thailand",
        "TJ": "Tajikistan",
        "TK": "Tokelau",
        "TL": "East Timor",
        "TM": "Turkmenistan",
        "TN": "Tunisia",
        "TO": "Tonga",
        "TR": "Turkey",
        "TT": "Trinidad and Tobago",
        "TV": "Tuvalu",
        "TW": "Taiwan",
        "TZ": "Tanzania",
        "UA": "Ukraine",
        "UG": "Uganda",
        "UK": "United Kingdom",
        "US": "United States",
        "UY": "Uruguay",
        "UZ": "Uzbekistan",
        "VA": "Vatican City",
        "VC": "Saint Vincent and the Grenadines",
        "VE": "Venezuela",
        "VG": "British Virgin Islands",
        "VI": "U.S. Virgin Islands",
        "VN": "Vietnam",
        "VU": "Vanuatu",
        "WF": "Wallis and Futuna",
        "WS": "Samoa",
        "YE": "Yemen",
        "YT": "Mayotte",
        "ZA": "South Africa",
        "ZM": "Zambia",
        "ZW": "Zimbabwe",
    }

    lang_name = language_names.get(lang_code, lang_code)
    if country_code:
        country_name = country_names.get(country_code, country_code)
        return f"{lang_name} ({country_name})"
    return lang_name


def remove_suffix(lang: str) -> str:
    """Remove suffix from language code (e.g., en_US.UTF-8 -> en_US)."""
    match = re.match(r"^[a-zA-Z_]+", lang)
    return match.group(0) if match else lang


def is_cjk_language(lang: str) -> bool:
    """Check if the language is CJK (Chinese, Japanese, Korean, etc.)."""
    l = lang[:2].lower()
    return l in CJK_LANGUAGES


def main_language(lang: str) -> str:
    """Returns main language from full locale (e.g., en_US.UTF-8 -> en)."""
    if not lang:
        return ""
    match = re.match(r"^[a-z]+", lang, re.IGNORECASE)
    return match.group(0).lower() if match else ""


def get_locales() -> dict[str, int]:
    """Get all available locales from system."""
    locales: dict[str, int] = {}

    try:
        result = subprocess.run(
            ["locale", "-a"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                l = line.strip()
                if not l:
                    continue
                pos = l.find(".")
                if pos == -1:
                    pos = l.find("@")
                if pos != -1:
                    l = l[:pos]
                if l:
                    locales[l] = 1
    except (subprocess.CalledProcessError, FileNotFoundError, TimeoutError):
        pass

    return locales


def read_locale_conf() -> dict[str, str]:
    """Read locale configuration from /etc/locale.conf."""
    if Path(LOCALE_CONF_FILE).exists():
        try:
            return dotenv.dotenv_values(LOCALE_CONF_FILE) or {}
        except (PermissionError, IOError):
            pass
    return {}


def read_sysconfig_language() -> str:
    """Read INSTALLED_LANGUAGES from /etc/sysconfig/language."""
    if Path(SYSCONFIG_LANGUAGE_FILE).exists():
        try:
            config = dotenv.dotenv_values(SYSCONFIG_LANGUAGE_FILE)
            return config.get("INSTALLED_LANGUAGES", "") or ""
        except (PermissionError, IOError):
            pass
    return ""


def get_current_language() -> str:
    """Get current language from locale.conf."""
    config = read_locale_conf()
    local_lang = config.get("LANG", DEFAULT_FALLBACK_LANGUAGE)
    if local_lang:
        local_lang = re.sub(r"[.@].*$", "", local_lang)
    return local_lang or DEFAULT_FALLBACK_LANGUAGE


def get_use_utf8() -> bool:
    """Check if UTF-8 is used."""
    config = read_locale_conf()
    local_lang = config.get("LANG", "")
    if local_lang and local_lang.strip():
        return ".UTF-8" in local_lang
    return True


def build_languages_map(locales: dict[str, int] | None = None) -> dict[str, LanguageInfo]:
    """Build a map of language codes to LanguageInfo objects."""
    if locales is None:
        locales = get_locales()

    languages_map: dict[str, LanguageInfo] = {}

    lang_timezone_map = {
        "af_ZA": "Africa/Johannesburg",
        "am_ET": "Africa/Addis_Ababa",
        "ar_AE": "Asia/Dubai",
        "ar_BH": "Asia/Bahrain",
        "ar_DZ": "Africa/Algiers",
        "ar_EG": "Africa/Cairo",
        "ar_IN": "Asia/Kolkata",
        "ar_IQ": "Asia/Baghdad",
        "ar_JO": "Asia/Amman",
        "ar_KW": "Asia/Kuwait",
        "ar_LB": "Asia/Beirut",
        "ar_LY": "Africa/Tripoli",
        "ar_MA": "Africa/Casablanca",
        "ar_OM": "Asia/Muscat",
        "ar_QA": "Asia/Qatar",
        "ar_SA": "Asia/Riyadh",
        "ar_SY": "Asia/Damascus",
        "ar_TN": "Africa/Tunis",
        "ar_YE": "Asia/Aden",
        "ast_ES": "Europe/Madrid",
        "be_BY": "Europe/Minsk",
        "bg_BG": "Europe/Sofia",
        "bn_IN": "Asia/Kolkata",
        "br_FR": "Europe/Paris",
        "bs_BA": "Europe/Sarajevo",
        "ca_ES": "Europe/Madrid",
        "cs_CZ": "Europe/Prague",
        "cy_GB": "Europe/London",
        "da_DK": "Europe/Copenhagen",
        "de_AT": "Europe/Vienna",
        "de_BE": "Europe/Brussels",
        "de_CH": "Europe/Zurich",
        "de_DE": "Europe/Berlin",
        "de_LU": "Europe/Luxembourg",
        "el_GR": "Europe/Athens",
        "en_AU": "Australia/Sydney",
        "en_CA": "America/Toronto",
        "en_GB": "Europe/London",
        "en_HK": "Asia/Hong_Kong",
        "en_IE": "Europe/Dublin",
        "en_IN": "Asia/Kolkata",
        "en_NZ": "Pacific/Auckland",
        "en_PH": "Asia/Manila",
        "en_SG": "Asia/Singapore",
        "en_US": "America/New_York",
        "en_ZA": "Africa/Johannesburg",
        "eo": "Europe/Paris",
        "es_AR": "America/Argentina/Buenos_Aires",
        "es_BO": "America/La_Paz",
        "es_CL": "America/Santiago",
        "es_CO": "America/Bogota",
        "es_CR": "America/Costa_Rica",
        "es_DO": "America/Santo_Domingo",
        "es_EC": "America/Guayaquil",
        "es_ES": "Europe/Madrid",
        "es_GT": "America/Guatemala",
        "es_HN": "America/Tegucigalpa",
        "es_MX": "America/Mexico_City",
        "es_NI": "America/Managua",
        "es_PA": "America/Panama",
        "es_PE": "America/Lima",
        "es_PR": "America/Puerto_Rico",
        "es_PY": "America/Asuncion",
        "es_SV": "America/El_Salvador",
        "es_US": "America/New_York",
        "es_UY": "America/Montevideo",
        "es_VE": "America/Caracas",
        "et_EE": "Europe/Tallinn",
        "eu_ES": "Europe/Madrid",
        "fa_IR": "Asia/Tehran",
        "fi_FI": "Europe/Helsinki",
        "fil_PH": "Asia/Manila",
        "fr_BE": "Europe/Brussels",
        "fr_CA": "America/Montreal",
        "fr_CH": "Europe/Zurich",
        "fr_FR": "Europe/Paris",
        "fr_LU": "Europe/Luxembourg",
        "fr_MC": "Europe/Monaco",
        "fr_SG": "Asia/Singapore",
        "ga_IE": "Europe/Dublin",
        "gl_ES": "Europe/Madrid",
        "gu_IN": "Asia/Kolkata",
        "he_IL": "Asia/Jerusalem",
        "hi_IN": "Asia/Kolkata",
        "hr_HR": "Europe/Zagreb",
        "hu_HU": "Europe/Budapest",
        "hy_AM": "Asia/Yerevan",
        "id_ID": "Asia/Jakarta",
        "is_IS": "Atlantic/Reykjavik",
        "it_CH": "Europe/Zurich",
        "it_IT": "Europe/Rome",
        "ja_JP": "Asia/Tokyo",
        "ka_GE": "Asia/Tbilisi",
        "kk_KZ": "Asia/Almaty",
        "km_KH": "Asia/Phnom_Penh",
        "kn_IN": "Asia/Kolkata",
        "ko_KR": "Asia/Seoul",
        "ku_TR": "Asia/Istanbul",
        "ky_KG": "Asia/Bishkek",
        "lo_LA": "Asia/Vientiane",
        "lt_LT": "Europe/Vilnius",
        "lv_LV": "Europe/Riga",
        "mk_MK": "Europe/Skopje",
        "ml_IN": "Asia/Kolkata",
        "mn_MN": "Asia/Ulaanbaatar",
        "mr_IN": "Asia/Kolkata",
        "ms_MY": "Asia/Kuala_Lumpur",
        "mt_MT": "Europe/Malta",
        "nb_NO": "Europe/Oslo",
        "ne_NP": "Asia/Kathmandu",
        "nl_BE": "Europe/Brussels",
        "nl_NL": "Europe/Amsterdam",
        "nn_NO": "Europe/Oslo",
        "pl_PL": "Europe/Warsaw",
        "pt_BR": "America/Sao_Paulo",
        "pt_PT": "Europe/Lisbon",
        "ro_RO": "Europe/Bucharest",
        "ru_RU": "Europe/Moscow",
        "si_LK": "Asia/Colombo",
        "sk_SK": "Europe/Bratislava",
        "sl_SI": "Europe/Ljubljana",
        "sr_RS": "Europe/Belgrade",
        "sv_FI": "Europe/Helsinki",
        "sv_SE": "Europe/Stockholm",
        "ta_IN": "Asia/Kolkata",
        "te_IN": "Asia/Kolkata",
        "th_TH": "Asia/Bangkok",
        "tr_TR": "Asia/Istanbul",
        "uk_UA": "Europe/Kiev",
        "ur_PK": "Asia/Karachi",
        "uz_UZ": "Asia/Tashkent",
        "vi_VN": "Asia/Ho_Chi_Minh",
        "zh_CN": "Asia/Shanghai",
        "zh_HK": "Asia/Hong_Kong",
        "zh_TW": "Asia/Taipei",
    }

    lang_keyboard_map = {
        "af_ZA": "us",
        "ar_AE": "ara",
        "ar_BH": "ara",
        "ar_DZ": "ara",
        "ar_EG": "ara",
        "ar_IQ": "ara",
        "ar_JO": "ara",
        "ar_KW": "ara",
        "ar_LB": "ara",
        "ar_LY": "ara",
        "ar_MA": "ara",
        "ar_OM": "ara",
        "ar_QA": "ara",
        "ar_SA": "ara",
        "ar_SY": "ara",
        "ar_TN": "ara",
        "ar_YE": "ara",
        "bg_BG": "bg",
        "bn_IN": "in",
        "ca_ES": "es",
        "cs_CZ": "cz",
        "da_DK": "dk",
        "de_AT": "at",
        "de_CH": "ch",
        "de_DE": "de",
        "el_GR": "gr",
        "en_AU": "us",
        "en_CA": "us",
        "en_GB": "gb",
        "en_HK": "us",
        "en_IE": "gb",
        "en_IN": "in",
        "en_NZ": "us",
        "en_US": "us",
        "en_ZA": "us",
        "es_AR": "latam",
        "es_BO": "latam",
        "es_CL": "latam",
        "es_CO": "latam",
        "es_CR": "latam",
        "es_DO": "latam",
        "es_EC": "latam",
        "es_ES": "es",
        "es_GT": "latam",
        "es_HN": "latam",
        "es_MX": "latam",
        "es_NI": "latam",
        "es_PA": "latam",
        "es_PE": "latam",
        "es_PR": "latam",
        "es_PY": "latam",
        "es_SV": "latam",
        "es_US": "us",
        "es_UY": "latam",
        "es_VE": "latam",
        "et_EE": "ee",
        "eu_ES": "es",
        "fi_FI": "fi",
        "fr_BE": "be",
        "fr_CA": "ca",
        "fr_CH": "ch",
        "fr_FR": "fr",
        "ga_IE": "ie",
        "gl_ES": "es",
        "gu_IN": "in",
        "he_IL": "il",
        "hi_IN": "in",
        "hr_HR": "hr",
        "hu_HU": "hu",
        "hy_AM": "am",
        "id_ID": "us",
        "is_IS": "is",
        "it_CH": "ch",
        "it_IT": "it",
        "ja_JP": "jp",
        "ka_GE": "ge",
        "kk_KZ": "kz",
        "km_KH": "kh",
        "kn_IN": "in",
        "ko_KR": "kr",
        "ky_KG": "kg",
        "lt_LT": "lt",
        "lv_LV": "lv",
        "mk_MK": "mk",
        "ml_IN": "in",
        "mn_MN": "mn",
        "mr_IN": "in",
        "ms_MY": "my",
        "mt_MT": "mt",
        "nb_NO": "no",
        "ne_NP": "np",
        "nl_BE": "be",
        "nl_NL": "nl",
        "nn_NO": "no",
        "pl_PL": "pl",
        "pt_BR": "br",
        "pt_PT": "pt",
        "ro_RO": "ro",
        "ru_RU": "ru",
        "si_LK": "lk",
        "sk_SK": "sk",
        "sl_SI": "si",
        "sr_RS": "rs",
        "sv_FI": "fi",
        "sv_SE": "se",
        "ta_IN": "in",
        "te_IN": "in",
        "th_TH": "th",
        "tr_TR": "tr",
        "uk_UA": "ua",
        "ur_PK": "pk",
        "uz_UZ": "uz",
        "vi_VN": "vn",
        "zh_CN": "cn",
        "zh_HK": "hk",
        "zh_TW": "tw",
    }

    for locale in locales:
        name = _get_language_name(locale)
        ascii_name = name
        english_name = name

        timezone = lang_timezone_map.get(locale, "US/Eastern")
        keyboard = lang_keyboard_map.get(locale, "us")

        languages_map[locale] = LanguageInfo(
            code=locale,
            name=name,
            name_ascii=ascii_name,
            name_english=english_name,
            timezone=timezone,
            keyboard=keyboard,
            encoding_utf8=".UTF-8",
            encoding_non_utf8="",
        )

    return languages_map


def get_locale_string(lang: str, use_utf8: bool = True) -> str:
    """Generate full locale string for given language (e.g., de_DE -> de_DE.UTF-8)."""
    if "." in lang or "@" in lang:
        return lang

    languages_map = build_languages_map()
    language_info = languages_map.get(lang)

    if not language_info:
        suffix = ".UTF-8" if use_utf8 else ""
        return lang + suffix

    idx = 0 if use_utf8 else 1
    suffix = language_info.encoding_utf8 if use_utf8 else language_info.encoding_non_utf8
    return lang + suffix


def get_language_country(lang: str) -> str:
    """Get country part from language code (e.g., de_DE@UTF-8 -> DE)."""
    country = lang or DEFAULT_FALLBACK_LANGUAGE

    if "@" in country:
        country = country.split("@")[0]
    if "." in country:
        country = country.split(".")[0]

    if "_" in country:
        country = country.split("_")[1]
    else:
        country = country.upper()

    return country


def is_supported_by_fbiterm(lang: str) -> bool:
    """Check if language is supported by fbiterm."""
    code = main_language(lang)
    return code not in UNSUPPORTED_FBITERM_LANGS


def is_fbiterm() -> bool:
    """Check if running on fbiterm."""
    return os.environ.get("TERM") == "iterm"


def _is_text_mode() -> bool:
    """Check if running in text mode (ncurses/TUI)."""
    term = os.environ.get("TERM", "")
    if term.startswith("linux") or term == "vt100" or term == "dumb":
        return True
    if "DISPLAY" not in os.environ:
        return True
    return False


def is_supported_language(lang: str) -> bool:
    """Check if language is supported in current mode."""
    if not _is_text_mode():
        return True

    fbiterm = is_fbiterm()
    cjk = is_cjk_language(lang)
    supported_by_fbi = is_supported_by_fbiterm(lang)

    return (fbiterm and supported_by_fbi) or (not fbiterm and not cjk)


def save_language_settings(
    language: str,
    languages: str = "",
    use_utf8: bool = True,
    use_pkexec: bool = True,
) -> tuple[Literal["ok", "permission_denied", "pkexec_failed", "error"], str]:
    """Save language settings to system files.

    Args:
        language: Primary language code (e.g., "en_US").
        languages: Comma-separated list of additional languages.
        use_utf8: Whether to use UTF-8 encoding.
        use_pkexec: If True, use pkexec for privilege escalation.

    Returns:
        Tuple of (status, message).
    """
    locale_str = get_locale_string(language, use_utf8)
    script_path = Path(__file__).parent / "set_language.py"

    if not use_pkexec:
        result = subprocess.run(
            [sys.executable, str(script_path), locale_str, languages],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip() == "OK":
            return ("ok", "Language settings saved successfully")
        elif result.returncode == 6:
            return ("permission_denied", "Permission denied")
        else:
            return ("error", result.stderr.strip() or "Failed to set language")

    result = subprocess.run(
        ["pkexec", sys.executable, str(script_path), locale_str, languages],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0 and result.stdout.strip() == "OK":
        return ("ok", "Language settings saved successfully")
    elif result.returncode == 126 or result.returncode == 127:
        return ("pkexec_failed", "Authentication failed")
    elif result.returncode == 6:
        return ("permission_denied", "Permission denied")
    else:
        return ("error", result.stderr.strip() or "Failed to set language")