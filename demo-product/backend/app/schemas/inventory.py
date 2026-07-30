"""Pydantic schemas for products and stock counts."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ProductOut(BaseModel):
    id: int
    product_code: str
    name: str
    current_quantity: int

    model_config = {'from_attributes': True}


class StockCountCreate(BaseModel):
    product_id: int
    counted_quantity: int = Field(..., ge=0)
    notes: Optional[str] = Field(None, max_length=500)


class StockCountOut(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    previous_quantity: int
    counted_quantity: int
    difference: int
    notes: Optional[str]
    created_by: str
    created_at: datetime

    model_config = {'from_attributes': True}
