from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models.category import Category
from app.utils.decorators import admin_required

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')

@categories_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        # Admin can create
        name = request.form.get('category_name', '').strip()
        desc = request.form.get('description', '').strip() or None

        if not name:
            flash('Category name is required.', 'danger')
        elif Category.query.filter_by(category_name=name).first():
            flash(f'Category "{name}" already exists.', 'danger')
        else:
            cat = Category(category_name=name, description=desc)
            db.session.add(cat)
            db.session.commit()
            flash(f'Category "{name}" created.', 'success')
            return redirect(url_for('categories.index'))

    categories = Category.query.order_by(Category.category_name).all()
    return render_template('categories/index.html', categories=categories)

@categories_bp.route('/<int:category_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit(category_id):
    category = Category.query.get_or_404(category_id)
    name = request.form.get('category_name', '').strip()
    desc = request.form.get('description', '').strip() or None

    if not name:
        flash('Category name is required.', 'danger')
        return redirect(url_for('categories.index'))

    existing = Category.query.filter(Category.category_name == name, Category.category_id != category_id).first()
    if existing:
        flash(f'Category name "{name}" is already taken.', 'danger')
        return redirect(url_for('categories.index'))

    category.category_name = name
    category.description = desc
    db.session.commit()
    flash(f'Category "{name}" updated.', 'success')
    return redirect(url_for('categories.index'))

@categories_bp.route('/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(category_id):
    category = Category.query.get_or_404(category_id)
    if category.products.count() > 0:
        flash(f'Cannot delete category "{category.category_name}" because {category.products.count()} product(s) are assigned to it. Foreign key RESTRICT enforced.', 'danger')
        return redirect(url_for('categories.index'))

    name = category.category_name
    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{name}" deleted.', 'info')
    return redirect(url_for('categories.index'))
