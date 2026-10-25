from app.models.customer import Customer
from app.extensions import db

def test_create_customer(sales_client):
    response = sales_client.post('/customers/create', data={
        'customer_name': 'Vertex Solutions LLC',
        'email': 'contact@vertex.com',
        'phone': '555-9876',
        'city': 'Austin',
        'state': 'TX',
        'customer_segment': 'SMB'
    }, follow_redirects=True)
    assert response.status_code == 200
    cust = Customer.query.filter_by(customer_name='Vertex Solutions LLC').first()
    assert cust is not None
    assert cust.city == 'Austin'
    assert cust.customer_segment == 'SMB'

def test_update_customer(sales_client):
    cust = Customer.query.filter_by(customer_name='Acme Enterprise').first()
    assert cust is not None
    response = sales_client.post(f'/customers/{cust.customer_id}/edit', data={
        'customer_name': 'Acme Enterprise Global',
        'email': 'procure@acmeglobal.com',
        'phone': '+1 555-0100',
        'city': 'Cambridge',
        'state': 'MA',
        'customer_segment': 'Enterprise'
    }, follow_redirects=True)
    assert response.status_code == 200
    updated = db.session.get(Customer, cust.customer_id)
    assert updated.customer_name == 'Acme Enterprise Global'
    assert updated.city == 'Cambridge'

def test_customer_deletion_prevented_with_existing_orders(auth_client):
    cust = Customer.query.filter_by(customer_name='Acme Enterprise').first()
    # Has existing order, deletion should be blocked by business rule
    response = auth_client.post(f'/customers/{cust.customer_id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'Cannot delete customer' in response.data
    assert db.session.get(Customer, cust.customer_id) is not None
