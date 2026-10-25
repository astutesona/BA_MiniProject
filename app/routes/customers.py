from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models.customer import Customer
from app.models.order import Order
from app.utils.decorators import sales_or_admin_required, admin_required

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')

@customers_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '').strip()
    segment = request.args.get('segment', '').strip()
    city = request.args.get('city', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Customer.query

    if search:
        query = query.filter(Customer.customer_name.ilike(f"%{search}%") | Customer.email.ilike(f"%{search}%"))
    if segment:
        query = query.filter_by(customer_segment=segment)
    if city:
        query = query.filter(Customer.city.ilike(f"%{city}%"))

    customers = query.order_by(Customer.customer_name).paginate(page=page, per_page=15, error_out=False)
    
    # Unique segments & cities for filtering
    segments = ['Enterprise', 'SMB', 'Retail', 'Wholesale']
    cities = [r[0] for r in db.session.query(Customer.city).distinct().order_by(Customer.city).all()]

    return render_template(
        'customers/index.html',
        customers=customers,
        segments=segments,
        cities=cities,
        search=search,
        selected_segment=segment,
        selected_city=city
    )

@customers_bp.route('/create', methods=['GET', 'POST'])
@login_required
@sales_or_admin_required
def create():
    if request.method == 'POST':
        name = request.form.get('customer_name', '').strip()
        email = request.form.get('email', '').strip() or None
        phone = request.form.get('phone', '').strip() or None
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        segment = request.form.get('customer_segment', 'Retail')

        if not name or not city or not state:
            flash('Customer name, city, and state are required fields.', 'danger')
            return render_template('customers/form.html', customer=None, action='Create')

        customer = Customer(
            customer_name=name,
            email=email,
            phone=phone,
            city=city,
            state=state,
            customer_segment=segment
        )
        db.session.add(customer)
        db.session.commit()
        flash(f'Customer "{customer.customer_name}" registered successfully.', 'success')
        return redirect(url_for('customers.index'))

    return render_template('customers/form.html', customer=None, action='Create')

@customers_bp.route('/<int:customer_id>')
@login_required
def detail(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.order_date.desc()).all()
    return render_template('customers/detail.html', customer=customer, orders=orders)

@customers_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
@sales_or_admin_required
def edit(customer_id):
    customer = Customer.query.get_or_404(customer_id)

    if request.method == 'POST':
        name = request.form.get('customer_name', '').strip()
        email = request.form.get('email', '').strip() or None
        phone = request.form.get('phone', '').strip() or None
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        segment = request.form.get('customer_segment', 'Retail')

        if not name or not city or not state:
            flash('Customer name, city, and state are required.', 'danger')
            return render_template('customers/form.html', customer=customer, action='Edit')

        customer.customer_name = name
        customer.email = email
        customer.phone = phone
        customer.city = city
        customer.state = state
        customer.customer_segment = segment

        db.session.commit()
        flash(f'Customer profile for "{customer.customer_name}" updated.', 'success')
        return redirect(url_for('customers.detail', customer_id=customer.customer_id))

    return render_template('customers/form.html', customer=customer, action='Edit')

@customers_bp.route('/<int:customer_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    # Check business rule: prevent deletion if customer has existing orders
    if customer.orders.count() > 0:
        flash(f'Cannot delete customer "{customer.customer_name}" because {customer.orders.count()} existing order record(s) reference this customer. Referential integrity enforced.', 'danger')
        return redirect(url_for('customers.detail', customer_id=customer.customer_id))

    name = customer.customer_name
    db.session.delete(customer)
    db.session.commit()
    flash(f'Customer "{name}" has been deleted.', 'info')
    return redirect(url_for('customers.index'))
