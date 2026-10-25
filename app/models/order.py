from datetime import datetime
from decimal import Decimal
from app.extensions import db

class Order(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id', ondelete='RESTRICT'), nullable=False, index=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    order_status = db.Column(db.String(30), default='Completed', nullable=False, index=True)
    payment_status = db.Column(db.String(30), default='Paid', nullable=False, index=True)
    payment_method = db.Column(db.String(40), default='Credit Card', nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy='joined', cascade='all, delete-orphan')

    @property
    def is_recognized_sale(self):
        """Recognized sale business rule: Completed status AND Paid payment."""
        return self.order_status == 'Completed' and self.payment_status == 'Paid'

    @property
    def total_revenue(self):
        """Sum of recognized line-item revenues after line-item discounts."""
        return sum((item.line_revenue for item in self.items), Decimal('0.00'))

    @property
    def total_cost(self):
        """Sum of recognized line-item COGS."""
        return sum((item.line_cost for item in self.items), Decimal('0.00'))

    @property
    def total_profit(self):
        """Gross profit = Net Revenue - COGS."""
        return self.total_revenue - self.total_cost

    @property
    def total_units(self):
        return sum((item.quantity for item in self.items), 0)

    def __repr__(self):
        return f"<Order #{self.order_id} - {self.order_status} - {self.payment_status}>"
