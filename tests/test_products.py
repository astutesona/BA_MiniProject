from decimal import Decimal
from app.models.product import Product
from app.models.category import Category
from app.extensions import db

def test_create_product(auth_client):
    cat = Category.query.first()
    response = auth_client.post('/products/create', data={
        'product_name': 'Ultra High Capacity NVMe',
        'SKU': 'NVME-TEST-99',
        'category_id': cat.category_id,
        'unit_price': '450.00',
        'unit_cost': '250.00',
        'stock_quantity': '30',
        'reorder_level': '8',
        'product_status': 'Active'
    }, follow_redirects=True)
    assert response.status_code == 200
    prod = Product.query.filter_by(SKU='NVME-TEST-99').first()
    assert prod is not None
    assert prod.unit_price == Decimal('450.00')
    assert prod.unit_cost == Decimal('250.00')

def test_reject_negative_product_price(auth_client):
    cat = Category.query.first()
    response = auth_client.post('/products/create', data={
        'product_name': 'Negative Price Invalid',
        'SKU': 'BAD-PRICE-01',
        'category_id': cat.category_id,
        'unit_price': '-50.00',
        'unit_cost': '10.00',
        'stock_quantity': '10',
        'reorder_level': '5',
        'product_status': 'Active'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'cannot be negative' in response.data
    assert Product.query.filter_by(SKU='BAD-PRICE-01').first() is None

def test_quick_stock_restock(auth_client):
    prod = Product.query.filter_by(SKU='TST-HW-001').first()
    old_stock = prod.stock_quantity
    response = auth_client.post(f'/products/{prod.product_id}/quick-stock', data={
        'add_quantity': '15'
    }, follow_redirects=True)
    assert response.status_code == 200
    updated = db.session.get(Product, prod.product_id)
    assert updated.stock_quantity == old_stock + 15
