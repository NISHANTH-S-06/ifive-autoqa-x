"""Service for Inventory management (Products and Stock Counts)."""
from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.models.inventory import Product, StockCount
from app.schemas.inventory import ProductOut, StockCountCreate, StockCountOut
from app.services.demo_setting_service import is_bug_enabled


def list_products(db: DBSession) -> List[ProductOut]:
    products = db.query(Product).order_by(Product.id.asc()).all()
    return [ProductOut.model_validate(p) for p in products]


def list_stock_counts(db: DBSession) -> List[StockCountOut]:
    records = db.query(StockCount).order_by(StockCount.id.desc()).all()
    prod_map = {p.id: p.name for p in db.query(Product).all()}
    res = []
    for r in records:
        out = StockCountOut.model_validate(r)
        out.product_name = prod_map.get(r.product_id, 'Unknown Product')
        res.append(out)
    return res


def create_stock_count(db: DBSession, payload: StockCountCreate, created_by: str) -> StockCountOut:
    product = db.get(Product, payload.product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Product {payload.product_id} not found')

    if payload.counted_quantity < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Counted quantity cannot be negative')

    prev_qty = product.current_quantity
    counted_qty = payload.counted_quantity

    # Standard difference: counted - previous
    diff = counted_qty - prev_qty

    # Bug toggle check: stock_difference_error
    if is_bug_enabled(db, 'stock_difference_error'):
        # Deliberately incorrect difference formula (adds 10 incorrectly)
        diff = (counted_qty - prev_qty) + 10

    stock_record = StockCount(
        product_id=product.id,
        previous_quantity=prev_qty,
        counted_quantity=counted_qty,
        difference=diff,
        notes=payload.notes,
        created_by=created_by,
        created_at=datetime.utcnow(),
    )
    db.add(stock_record)

    # Update current quantity on product
    product.current_quantity = counted_qty

    db.commit()
    db.refresh(stock_record)

    out = StockCountOut.model_validate(stock_record)
    out.product_name = product.name
    return out
