from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='Sales Employee', index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    orders_created = db.relationship('Order', backref='creator', lazy='dynamic')
    targets_created = db.relationship('SalesTarget', backref='creator', lazy='dynamic')

    def get_id(self):
        return str(self.user_id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'Admin'

    @property
    def is_manager(self):
        return self.role == 'Manager'

    @property
    def is_sales(self):
        return self.role == 'Sales Employee'

    def can_access_query_lab(self):
        return self.role in ['Admin', 'Manager']

    def can_modify_catalog(self):
        return self.role == 'Admin'

    def can_manage_users(self):
        return self.role == 'Admin'

    def can_create_orders(self):
        return self.role in ['Admin', 'Sales Employee']

    def can_configure_targets(self):
        return self.role in ['Admin', 'Manager']

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
