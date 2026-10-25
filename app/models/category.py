from datetime import datetime
from app.extensions import db

class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(60), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    products = db.relationship('Product', backref='category', lazy='dynamic')
    targets = db.relationship('SalesTarget', backref='category', lazy='dynamic')

    @property
    def product_count(self):
        return self.products.count()

    def __repr__(self):
        return f"<Category {self.category_name}>"
