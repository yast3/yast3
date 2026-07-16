"""Snapper configuration file handling."""

from __future__ import annotations

import dotenv

DEFAULT_CONFIG_PATH = "/etc/snapper/configs/root"


class SnapperConfig:
    SUBVOLUME: str
    FSTYPE: str
    QGROUP: str
    SPACE_LIMIT: str
    FREE_LIMIT: str
    ALLOW_USERS: str
    ALLOW_GROUPS: str
    SYNC_ACL: str
    BACKGROUND_COMPARISON: str
    NUMBER_CLEANUP: str
    NUMBER_MIN_AGE: str
    NUMBER_LIMIT: str
    NUMBER_LIMIT_IMPORTANT: str
    TIMELINE_CREATE: str
    TIMELINE_CLEANUP: str
    TIMELINE_MIN_AGE: str
    TIMELINE_LIMIT_HOURLY: str
    TIMELINE_LIMIT_DAILY: str
    TIMELINE_LIMIT_WEEKLY: str
    TIMELINE_LIMIT_MONTHLY: str
    TIMELINE_LIMIT_YEARLY: str
    EMPTY_PRE_POST_CLEANUP: str
    EMPTY_PRE_POST_MIN_AGE: str

    def __init__(self) -> None:
        self.reload()

    def reload(self) -> None:
        config = dotenv.dotenv_values(DEFAULT_CONFIG_PATH)
        self.SUBVOLUME = config.get("SUBVOLUME") or "/"
        self.FSTYPE = config.get("FSTYPE") or "btrfs"
        self.QGROUP = config.get("QGROUP") or ""
        self.SPACE_LIMIT = config.get("SPACE_LIMIT") or "0.5"
        self.FREE_LIMIT = config.get("FREE_LIMIT") or "0.2"
        self.ALLOW_USERS = config.get("ALLOW_USERS") or ""
        self.ALLOW_GROUPS = config.get("ALLOW_GROUPS") or ""
        self.SYNC_ACL = config.get("SYNC_ACL") or "no"
        self.BACKGROUND_COMPARISON = config.get("BACKGROUND_COMPARISON") or "yes"
        self.NUMBER_CLEANUP = config.get("NUMBER_CLEANUP") or "yes"
        self.NUMBER_MIN_AGE = config.get("NUMBER_MIN_AGE") or "1800"
        self.NUMBER_LIMIT = config.get("NUMBER_LIMIT") or "2-10"
        self.NUMBER_LIMIT_IMPORTANT = config.get("NUMBER_LIMIT_IMPORTANT") or "4-10"
        self.TIMELINE_CREATE = config.get("TIMELINE_CREATE") or "no"
        self.TIMELINE_CLEANUP = config.get("TIMELINE_CLEANUP") or "yes"
        self.TIMELINE_MIN_AGE = config.get("TIMELINE_MIN_AGE") or "1800"
        self.TIMELINE_LIMIT_HOURLY = config.get("TIMELINE_LIMIT_HOURLY") or "10"
        self.TIMELINE_LIMIT_DAILY = config.get("TIMELINE_LIMIT_DAILY") or "10"
        self.TIMELINE_LIMIT_WEEKLY = config.get("TIMELINE_LIMIT_WEEKLY") or "0"
        self.TIMELINE_LIMIT_MONTHLY = config.get("TIMELINE_LIMIT_MONTHLY") or "10"
        self.TIMELINE_LIMIT_YEARLY = config.get("TIMELINE_LIMIT_YEARLY") or "10"
        self.EMPTY_PRE_POST_CLEANUP = config.get("EMPTY_PRE_POST_CLEANUP") or "yes"
        self.EMPTY_PRE_POST_MIN_AGE = config.get("EMPTY_PRE_POST_MIN_AGE") or "1800"

    def write(self) -> None:
        dotenv.set_key(DEFAULT_CONFIG_PATH, "SUBVOLUME", self.SUBVOLUME, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "FSTYPE", self.FSTYPE, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "QGROUP", self.QGROUP, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "SPACE_LIMIT", self.SPACE_LIMIT, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "FREE_LIMIT", self.FREE_LIMIT, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "ALLOW_USERS", self.ALLOW_USERS, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "ALLOW_GROUPS", self.ALLOW_GROUPS, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "SYNC_ACL", self.SYNC_ACL, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "BACKGROUND_COMPARISON", self.BACKGROUND_COMPARISON, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "NUMBER_CLEANUP", self.NUMBER_CLEANUP, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "NUMBER_MIN_AGE", self.NUMBER_MIN_AGE, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "NUMBER_LIMIT", self.NUMBER_LIMIT, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "NUMBER_LIMIT_IMPORTANT", self.NUMBER_LIMIT_IMPORTANT, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "TIMELINE_CREATE", self.TIMELINE_CREATE, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "TIMELINE_CLEANUP", self.TIMELINE_CLEANUP, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "TIMELINE_MIN_AGE", self.TIMELINE_MIN_AGE, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "TIMELINE_LIMIT_HOURLY", self.TIMELINE_LIMIT_HOURLY, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "TIMELINE_LIMIT_DAILY", self.TIMELINE_LIMIT_DAILY, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "TIMELINE_LIMIT_WEEKLY", self.TIMELINE_LIMIT_WEEKLY, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "TIMELINE_LIMIT_MONTHLY", self.TIMELINE_LIMIT_MONTHLY, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "TIMELINE_LIMIT_YEARLY", self.TIMELINE_LIMIT_YEARLY, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "EMPTY_PRE_POST_CLEANUP", self.EMPTY_PRE_POST_CLEANUP, quote_mode='always')
        dotenv.set_key(DEFAULT_CONFIG_PATH, "EMPTY_PRE_POST_MIN_AGE", self.EMPTY_PRE_POST_MIN_AGE, quote_mode='always')


def read_config() -> SnapperConfig:
    return SnapperConfig()


def write_config(config: SnapperConfig) -> None:
    config.write()