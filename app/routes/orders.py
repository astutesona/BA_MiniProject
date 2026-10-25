from datetime import datetime
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.order import Order
from app.models.customer import Customer
from app.models.product import Product
from app.services.sales_service import SalesService
from app.utils.decorators import sales_or_admin_required

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

@orders_bp.route('/')
@login_required
def index():
    status = request.args.get('status', '').strip()
    payment = request.args.get('payment', '').strip()
    search = request.args.get('search', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Order.query.join(Customer)

    if search:
        query = query.filter(Customer.customer_name.ilike(f"%{search}%") | Order.order_id.like(f"%{search}%"))
    if status:
        query = query.filter(Order.order_status == status)
    if payment:
        query = query.filter(Order.payment_status == payment)
    if start_date:
        query = query.filter(Order.order_date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Order.order_date <= datetime.strptime(end_date, '%Y-%m-%d'))

    orders = query.order_by(Order.order_date.desc()).paginate(page=page, per_page=15, error_out=False)

    return render_template(
        'orders/index.html',
        orders=orders,
        status_filter=status,
        payment_filter=payment,
        search=search,
        start_date=start_date,
        end_date=end_date
    )

@orders_bp.route('/create', methods=['GET', 'POST'])
@login_required
@sales_or_admin_required
def create():
    customers = Customer.query.order_by(Customer.customer_name).all()
    products = Product.query.filter_by(product_status='Active').order_by(Product.product_name).all()

    if request.method == 'POST':
        customer_id = request.form.get('customer_id', type=int)
        payment_method = request.form.get('payment_method', 'Credit Card')
        order_status = request.form.get('order_status', 'Completed')
        payment_status = request.form.get('payment_status', 'Paid')

        # Extract dynamic line items from form lists
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        discounts = request.form.getlist('discount[]')

        items_data = []
        for i in range(len(product_ids)):
            if product_ids[i]:
                try:
                    p_id = int(product_ids[i])
                    qty = int(quantities[i]) if i < len(quantities) and quantities[i] else 1
                    disc = Decimal(discounts[i]) if i < len(discounts) and discounts[i] else Decimal('0.00')
                    items_data.append({
                        'product_id': p_id,
                        'quantity': qty,
                        'discount': disc
                    })
                except Exception as ex:
                    flash(f'Invalid item data entered: {ex}', 'danger')
                    return render_template('orders/create.html', customers=customers, products=products)

        if not items_data:
            flash('Please add at least one product item to the order.', 'danger')
            return render_template('orders/create.html', customers=customers, products=products)

        try:
            order = SalesService.create_order(
                customer_id=customer_id,
                items_data=items_data,
                user_id=current_user.user_id,
                payment_method=payment_method,
                order_status=order_status,
                payment_status=payment_status
            )
            flash(f'Order #{order.order_id} recorded successfully (Total: ${order.total_revenue:,.2f}).', 'success')
            return redirect(url_for('orders.detail', order_id=order.order_id))
        except Exception as e:
            flash(f'Failed to create order: {str(e)}', 'danger')
            return render_template('orders/create.html', customers=customers, products=products)

    return render_template('orders/create.html', customers=customers, products=products)

@orders_bp.route('/<int:order_id>')
@login_required
def detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('orders/detail.html', order=order)

@orders_bp.route('/<int:order_id>/status', methods=['POST'])
@login_required
@sales_or_admin_required
def update_status(order_id):
    new_status = request.form.get('order_status')
    new_payment = request.form.get('payment_status')

    try:
        SalesService.update_order_status(order_id, new_status, new_payment)
        flash(f'Order #{order_id} status updated to {new_status} / {new_payment}.', 'success')
    except Exception as e:
        flash(f'Error updating order status: {str(e)}', 'danger')

    return redirect(url_for('orders.detail', order_id=order_id))
