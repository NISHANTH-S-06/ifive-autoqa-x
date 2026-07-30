"""Service for checking and managing Demo Settings (bug toggles)."""
from __future__ import annotations

from typing import Dict, List
from sqlalchemy.orm import Session as DBSession

from app.models.demo_setting import DemoSetting


KNOWN_BUG_KEYS = [
    'employee_save_failure',
    'employee_success_message_missing',
    'employee_table_refresh_failure',
    'stock_difference_error',
    'api_delay',
    'login_failure_mode',
]


def is_bug_enabled(db: DBSession, key: str) -> bool:
    setting = db.get(DemoSetting, key)
    return bool(setting and setting.enabled)


def get_all_settings(db: DBSession) -> List[DemoSetting]:
    return db.query(DemoSetting).order_by(DemoSetting.key).all()


def update_setting(db: DBSession, key: str, enabled: bool, value: str | None = None) -> DemoSetting:
    setting = db.get(DemoSetting, key)
    if setting is None:
        setting = DemoSetting(key=key, enabled=enabled, value=value)
        db.add(setting)
    else:
        setting.enabled = enabled
        setting.value = value
    db.commit()
    db.refresh(setting)
    return setting
