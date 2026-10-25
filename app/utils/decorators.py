from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def role_required(*allowed_roles):
    """
    Decorator for server-side role-based authorization check.
    Ensures current_user is authenticated and has one of the required roles.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this feature.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return role_required('Admin')(f)

def manager_or_admin_required(f):
    return role_required('Admin', 'Manager')(f)

def sales_or_admin_required(f):
    return role_required('Admin', 'Sales Employee')(f)
