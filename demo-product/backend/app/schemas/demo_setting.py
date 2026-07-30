"""Pydantic schemas for demo setting bug toggles."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DemoSettingOut(BaseModel):
    key: str
    enabled: bool
    value: Optional[str] = None
    updated_at: datetime

    model_config = {'from_attributes': True}


class DemoSettingUpdate(BaseModel):
    enabled: bool
    value: Optional[str] = None
