from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models.user import User
from app.utils.decorators import admin_required

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/')
@login_required
@admin_required
def index():
    users = User.query.order_by(User.role, User.username).all()
    return render_template('users/index.html', users=users)

@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'Sales Employee')

        if not full_name or not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('users/form.html', user=None, action='Create')

        if User.query.filter_by(username=username).first():
            flash(f'Username "{username}" is already taken.', 'danger')
            return render_template('users/form.html', user=None, action='Create')

        if User.query.filter_by(email=email).first():
            flash(f'Email "{email}" is already registered.', 'danger')
            return render_template('users/form.html', user=None, action='Create')

        user = User(
            full_name=full_name,
            username=username,
            email=email,
            role=role,
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(f'User "{username}" ({role}) created successfully.', 'success')
        return redirect(url_for('users.index'))

    return render_template('users/form.html', user=None, action='Create')

@users_bp.route('/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_status(user_id):
    if user_id == current_user.user_id:
        flash('You cannot deactivate your own account.', 'warning')
        return redirect(url_for('users.index'))

    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status_str = "activated" if user.is_active else "deactivated"
    flash(f'Account for "{user.username}" has been {status_str}.', 'info')
    return redirect(url_for('users.index'))
