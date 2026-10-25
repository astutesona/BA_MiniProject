import pytest
from decimal import Decimal
from datetime import datetime, date
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.sales_target import SalesTarget

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()

        # Seed minimal test fixtures
        admin = User(full_name='Test Admin', username='admin_test', email='admin@test.com', role='Admin')
        admin.set_password('AdminPass123')

        manager = User(full_name='Test Manager', username='manager_test', email='manager@test.com', role='Manager')
        manager.set_password('ManagerPass123')

        sales = User(full_name='Test Sales', username='sales_test', email='sales@test.com', role='Sales Employee')
        sales.set_password('SalesPass123')

        db.session.add_all([admin, manager, sales])

        cat1 = Category(category_name='Hardware', description='Hardware products')
        cat2 = Category(category_name='Software', description='Software products')
        db.session.add_all([cat1, cat2])
        db.session.flush()

        prod1 = Product(
            product_name='Workstation Pro',
            category_id=cat1.category_id,
            SKU='TST-HW-001',
            unit_price=Decimal('2000.00'),
            unit_cost=Decimal('1200.00'),
            stock_quantity=20,
            reorder_level=5,
            product_status='Active'
        )
        prod2 = Product(
            product_name='Security Suite License',
            category_id=cat2.category_id,
            SKU='TST-SW-002',
            unit_price=Decimal('500.00'),
            unit_cost=Decimal('200.00'),
            stock_quantity=50,
            reorder_level=10,
            product_status='Active'
        )
        db.session.add_all([prod1, prod2])
        db.session.flush()

        cust = Customer(
            customer_name='Acme Enterprise',
            email='procure@acme.com',
            phone='+1 555-0100',
            city='Boston',
            state='MA',
            customer_segment='Enterprise',
            registration_date=date(2025, 1, 15)
        )
        db.session.add(cust)
        db.session.flush()

        # Seed Completed Order (Recognized Sale)
        order1 = Order(
            customer_id=cust.customer_id,
            order_date=datetime(2026, 2, 10, 14, 30),
            order_status='Completed',
            payment_status='Paid',
            payment_method='Credit Card',
            created_by=sales.user_id
        )
        db.session.add(order1)
        db.session.flush()

        item1 = OrderItem(
            order_id=order1.order_id,
            product_id=prod1.product_id,
            quantity=2,
            unit_price_at_sale=Decimal('2000.00'),
            unit_cost_at_sale=Decimal('1200.00'),
            discount_amount=Decimal('100.00') # Net rev: (2*2000)-100 = 3900. Cost: 2*1200 = 2400. Profit: 1500
        )
        db.session.add(item1)

        # Seed Cancelled Order (Excluded from recognized sales)
        order2 = Order(
            customer_id=cust.customer_id,
            order_date=datetime(2026, 2, 12, 11, 0),
            order_status='Cancelled',
            payment_status='Refunded',
            payment_method='Credit Card',
            created_by=sales.user_id
        )
        db.session.add(order2)
        db.session.flush()

        item2 = OrderItem(
            order_id=order2.order_id,
            product_id=prod2.product_id,
            quantity=5,
            unit_price_at_sale=Decimal('500.00'),
            unit_cost_at_sale=Decimal('200.00'),
            discount_amount=Decimal('0.00')
        )
        db.session.add(item2)

        # Sales Target for 2026-02
        target = SalesTarget(
            target_period='2026-02',
            target_type='Monthly Revenue',
            category_id=None,
            target_amount=Decimal('5000.00'),
            created_by=manager.user_id
        )
        db.session.add(target)

        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """Client authenticated as Admin."""
    client.post('/auth/login', data={'username': 'admin_test', 'password': 'AdminPass123'}, follow_redirects=True)
    return client

@pytest.fixture
def sales_client(client):
    """Client authenticated as Sales Employee."""
    client.post('/auth/login', data={'username': 'sales_test', 'password': 'SalesPass123'}, follow_redirects=True)
    return client

@pytest.fixture
def manager_client(client):
    """Client authenticated as Manager."""
    client.post('/auth/login', data={'username': 'manager_test', 'password': 'ManagerPass123'}, follow_redirects=True)
    return client
