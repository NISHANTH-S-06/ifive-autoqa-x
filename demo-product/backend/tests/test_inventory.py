"""Backend tests for Inventory & Stock Counts."""
from __future__ import annotations

from app.models import Product
from app.services.demo_setting_service import update_setting


def test_list_products(inventory_client):
    client, _ = inventory_client
    resp = client.get('/api/products')
    assert resp.status_code == 200
    prods = resp.json()
    assert len(prods) >= 3


def test_stock_count_success(inventory_client, db):
    client, _ = inventory_client
    prod = db.query(Product).first()
    prev_qty = prod.current_quantity

    resp = client.post('/api/stock-counts', json={
        'product_id': prod.id,
        'counted_quantity': prev_qty + 15,
        'notes': 'Inventory audit recount',
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data['product_id'] == prod.id
    assert data['previous_quantity'] == prev_qty
    assert data['counted_quantity'] == prev_qty + 15
    assert data['difference'] == 15

    # Verify product updated quantity
    db.refresh(prod)
    assert prod.current_quantity == prev_qty + 15


def test_stock_count_negative_quantity_rejected(inventory_client, db):
    client, _ = inventory_client
    prod = db.query(Product).first()
    resp = client.post('/api/stock-counts', json={
        'product_id': prod.id,
        'counted_quantity': -5,
    })
    assert resp.status_code in {400, 422}


def test_stock_difference_error_bug_toggle(inventory_client, db):
    client, _ = inventory_client
    prod = db.query(Product).first()
    prev_qty = prod.current_quantity

    # Enable bug toggle
    update_setting(db, 'stock_difference_error', enabled=True)

    resp = client.post('/api/stock-counts', json={
        'product_id': prod.id,
        'counted_quantity': prev_qty + 10,
    })
    assert resp.status_code == 201
    data = resp.json()
    # Bug toggle adds 10 to standard difference (10 + 10 = 20)
    assert data['difference'] == 20


def test_stock_count_role_restriction(hr_client, db):
    client, _ = hr_client
    prod = db.query(Product).first()
    resp = client.post('/api/stock-counts', json={
        'product_id': prod.id,
        'counted_quantity': 50,
    })
    assert resp.status_code == 403
