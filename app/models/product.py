from datetime import datetime
from decimal import Decimal
from app.extensions import db

class Product(db.Model):
    __tablename__ = 'products'

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(120), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='RESTRICT'), nullable=False, index=True)
    SKU = db.Column(db.String(50), unique=True, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0, nullable=False)
    reorder_level = db.Column(db.Integer, default=10, nullable=False)
    product_status = db.Column(db.String(30), default='Active', nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')

    @property
    def unit_profit(self):
        return (self.unit_price or Decimal('0.00')) - (self.unit_cost or Decimal('0.00'))

    @property
    def margin_percentage(self):
        if self.unit_price and self.unit_price > 0:
            return round((self.unit_profit / self.unit_price) * 100, 2)
        return Decimal('0.00')

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.reorder_level

    @property
    def stock_valuation(self):
        return (self.unit_cost or Decimal('0.00')) * self.stock_quantity

    def __repr__(self):
        return f"<Product {self.product_name} ({self.SKU})>"
