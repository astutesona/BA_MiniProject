import pytest
from decimal import Decimal
from app.models.product import Product
from app.models.customer import Customer
from app.models.order import Order
from app.services.sales_service import SalesService
from app.extensions import db

def test_order_creation_with_multiple_items(sales_client, app):
    with app.app_context():
        cust = Customer.query.first()
        prod1 = Product.query.filter_by(SKU='TST-HW-001').first()
        prod2 = Product.query.filter_by(SKU='TST-SW-002').first()
        initial_stock = prod1.stock_quantity

        order = SalesService.create_order(
            customer_id=cust.customer_id,
            items_data=[
                {'product_id': prod1.product_id, 'quantity': 2, 'discount': Decimal('50.00')},
                {'product_id': prod2.product_id, 'quantity': 1, 'discount': Decimal('0.00')}
            ],
            order_status='Completed',
            payment_status='Paid'
        )

        assert order.order_id is not None
        assert len(order.items) == 2
        # Gross: (2 * 2000) - 50 + (1 * 500) = 3950 + 500 = 4450
        assert order.total_revenue == Decimal('4450.00')
        # Inventory deducted on Completed status
        assert prod1.stock_quantity == initial_stock - 2

def test_reject_invalid_quantity(app):
    with app.app_context():
        cust = Customer.query.first()
        prod = Product.query.first()
        with pytest.raises(ValueError) as excinfo:
            SalesService.create_order(
                customer_id=cust.customer_id,
                items_data=[{'product_id': prod.product_id, 'quantity': 0, 'discount': 0}]
            )
        assert 'must be positive' in str(excinfo.value)

def test_transaction_rollback_on_insufficient_stock(app):
    with app.app_context():
        cust = Customer.query.first()
        prod = Product.query.first()
        initial_order_count = Order.query.count()

        with pytest.raises(ValueError) as excinfo:
            SalesService.create_order(
                customer_id=cust.customer_id,
                items_data=[{'product_id': prod.product_id, 'quantity': 99999, 'discount': 0}],
                order_status='Completed'
            )
        assert 'Insufficient stock' in str(excinfo.value)
        # Verify no orphan order header was committed
        assert Order.query.count() == initial_order_count

def test_preserve_historical_sale_prices_when_product_price_changes(app):
    with app.app_context():
        cust = Customer.query.first()
        prod = Product.query.filter_by(SKU='TST-HW-001').first()

        # Create historical order at initial price (2000.00)
        order = SalesService.create_order(
            customer_id=cust.customer_id,
            items_data=[{'product_id': prod.product_id, 'quantity': 1, 'discount': 0}],
            order_status='Completed',
            payment_status='Paid'
        )
        saved_sale_price = order.items[0].unit_price_at_sale
        assert saved_sale_price == Decimal('2000.00')

        # Now change catalog price of the product
        prod.unit_price = Decimal('3500.00')
        db.session.commit()

        # The historical line item MUST retain original price 2000.00
        reloaded_order = db.session.get(Order, order.order_id)
        assert reloaded_order.items[0].unit_price_at_sale == Decimal('2000.00')
        assert reloaded_order.total_revenue == Decimal('2000.00')
