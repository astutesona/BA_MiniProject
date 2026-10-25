from datetime import datetime, date
from app.extensions import db

class Customer(db.Model):
    __tablename__ = 'customers'

    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(25), nullable=True)
    city = db.Column(db.String(60), nullable=False)
    state = db.Column(db.String(60), nullable=False)
    customer_segment = db.Column(db.String(40), default='Retail', nullable=False, index=True)
    registration_date = db.Column(db.Date, default=date.today, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    orders = db.relationship('Order', backref='customer', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def total_orders_count(self):
        return self.orders.count()

    def __repr__(self):
        return f"<Customer {self.customer_name} ({self.customer_segment})>"
