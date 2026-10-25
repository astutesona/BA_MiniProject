from datetime import datetime
from decimal import Decimal
from app.extensions import db

class SalesTarget(db.Model):
    __tablename__ = 'sales_targets'

    target_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    target_period = db.Column(db.String(7), nullable=False, index=True) # Format YYYY-MM
    target_type = db.Column(db.String(40), default='Monthly Revenue', nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='SET NULL'), nullable=True, index=True)
    target_amount = db.Column(db.Numeric(12, 2), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('target_period', 'target_type', 'category_id', name='uq_period_type_category'),
    )

    def __repr__(self):
        cat_info = f"Cat #{self.category_id}" if self.category_id else "Overall"
        return f"<SalesTarget {self.target_period} ({cat_info}): ${self.target_amount}>"
