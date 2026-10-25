from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models.product import Product
from app.models.category import Category
from app.utils.decorators import admin_required

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status', '').strip()
    low_stock = request.args.get('low_stock', type=int)
    page = request.args.get('page', 1, type=int)

    query = Product.query

    if search:
        query = query.filter(Product.product_name.ilike(f"%{search}%") | Product.SKU.ilike(f"%{search}%"))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if status:
        query = query.filter_by(product_status=status)
    if low_stock == 1:
        query = query.filter(Product.stock_quantity <= Product.reorder_level)

    products = query.order_by(Product.product_name).paginate(page=page, per_page=15, error_out=False)
    categories = Category.query.order_by(Category.category_name).all()

    return render_template(
        'products/index.html',
        products=products,
        categories=categories,
        search=search,
        selected_category=category_id,
        selected_status=status,
        low_stock_only=(low_stock == 1)
    )

@products_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    categories = Category.query.order_by(Category.category_name).all()

    if request.method == 'POST':
        name = request.form.get('product_name', '').strip()
        cat_id = request.form.get('category_id', type=int)
        sku = request.form.get('SKU', '').strip().upper()
        price_str = request.form.get('unit_price', '0')
        cost_str = request.form.get('unit_cost', '0')
        stock = request.form.get('stock_quantity', 0, type=int)
        reorder = request.form.get('reorder_level', 10, type=int)
        status = request.form.get('product_status', 'Active')

        try:
            price = Decimal(price_str)
            cost = Decimal(cost_str)
        except Exception:
            flash('Unit price and cost must be valid numerical amounts.', 'danger')
            return render_template('products/form.html', product=None, categories=categories, action='Create')

        if price < Decimal('0.00') or cost < Decimal('0.00'):
            flash('Price and cost cannot be negative.', 'danger')
            return render_template('products/form.html', product=None, categories=categories, action='Create')

        if stock < 0 or reorder < 0:
            flash('Stock quantity and reorder level must not be negative.', 'danger')
            return render_template('products/form.html', product=None, categories=categories, action='Create')

        if Product.query.filter_by(SKU=sku).first():
            flash(f'A product with SKU "{sku}" already exists.', 'danger')
            return render_template('products/form.html', product=None, categories=categories, action='Create')

        product = Product(
            product_name=name,
            category_id=cat_id,
            SKU=sku,
            unit_price=price,
            unit_cost=cost,
            stock_quantity=stock,
            reorder_level=reorder,
            product_status=status
        )
        db.session.add(product)
        db.session.commit()
        flash(f'Product "{product.product_name}" added to catalog.', 'success')
        return redirect(url_for('products.index'))

    return render_template('products/form.html', product=None, categories=categories, action='Create')

@products_bp.route('/<int:product_id>')
@login_required
def detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('products/detail.html', product=product)

@products_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.order_by(Category.category_name).all()

    if request.method == 'POST':
        name = request.form.get('product_name', '').strip()
        cat_id = request.form.get('category_id', type=int)
        sku = request.form.get('SKU', '').strip().upper()
        price_str = request.form.get('unit_price', '0')
        cost_str = request.form.get('unit_cost', '0')
        stock = request.form.get('stock_quantity', 0, type=int)
        reorder = request.form.get('reorder_level', 10, type=int)
        status = request.form.get('product_status', 'Active')

        try:
            price = Decimal(price_str)
            cost = Decimal(cost_str)
        except Exception:
            flash('Price and cost must be valid numeric amounts.', 'danger')
            return render_template('products/form.html', product=product, categories=categories, action='Edit')

        if price < Decimal('0.00') or cost < Decimal('0.00'):
            flash('Price and cost cannot be negative.', 'danger')
            return render_template('products/form.html', product=product, categories=categories, action='Edit')

        # Check SKU uniqueness if changed
        existing_sku = Product.query.filter(Product.SKU == sku, Product.product_id != product_id).first()
        if existing_sku:
            flash(f'SKU "{sku}" is already allocated to another product.', 'danger')
            return render_template('products/form.html', product=product, categories=categories, action='Edit')

        product.product_name = name
        product.category_id = cat_id
        product.SKU = sku
        product.unit_price = price
        product.unit_cost = cost
        product.stock_quantity = stock
        product.reorder_level = reorder
        product.product_status = status

        db.session.commit()
        flash(f'Product "{product.product_name}" updated successfully.', 'success')
        return redirect(url_for('products.detail', product_id=product.product_id))

    return render_template('products/form.html', product=product, categories=categories, action='Edit')

@products_bp.route('/<int:product_id>/quick-stock', methods=['POST'])
@login_required
@admin_required
def quick_stock(product_id):
    product = Product.query.get_or_404(product_id)
    add_qty = request.form.get('add_quantity', 0, type=int)
    if add_qty > 0:
        product.stock_quantity += add_qty
        db.session.commit()
        flash(f'Restocked {add_qty} units for "{product.product_name}". New balance: {product.stock_quantity}.', 'success')
    else:
        flash('Quantity to restock must be greater than zero.', 'warning')
    return redirect(request.referrer or url_for('products.detail', product_id=product_id))
