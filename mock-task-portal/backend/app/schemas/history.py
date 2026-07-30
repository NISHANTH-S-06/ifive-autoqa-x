"""Pydantic schemas for task history."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class HistoryOut(BaseModel):
    id: int
    task_id: int
    previous_status: Optional[str]
    new_status: str
    changed_by: str
    reason: Optional[str]
    timestamp: datetime

    model_config = {'from_attributes': True}
