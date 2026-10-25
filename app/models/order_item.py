from datetime import datetime
from decimal import Decimal
from app.extensions import db

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    order_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id', ondelete='RESTRICT'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price_at_sale = db.Column(db.Numeric(10, 2), nullable=False)
    unit_cost_at_sale = db.Column(db.Numeric(10, 2), nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def line_gross_amount(self):
        """Undiscounted gross amount: quantity * unit_price_at_sale."""
        return (self.unit_price_at_sale or Decimal('0.00')) * self.quantity

    @property
    def line_revenue(self):
        """Recognized Net Revenue after line-item discount."""
        gross = self.line_gross_amount
        discount = self.discount_amount or Decimal('0.00')
        net = gross - discount
        return max(net, Decimal('0.00'))

    @property
    def line_cost(self):
        """Cost of Goods Sold (COGS)."""
        return (self.unit_cost_at_sale or Decimal('0.00')) * self.quantity

    @property
    def line_profit(self):
        """Gross Profit = Line Revenue - Line COGS."""
        return self.line_revenue - self.line_cost

    def __repr__(self):
        return f"<OrderItem #{self.order_item_id} (Prod #{self.product_id} x{self.quantity})>"
