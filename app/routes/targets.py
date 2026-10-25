from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.sales_target import SalesTarget
from app.models.category import Category
from app.services.report_service import ReportService
from app.utils.decorators import manager_or_admin_required

targets_bp = Blueprint('targets', __name__, url_prefix='/targets')

@targets_bp.route('/', methods=['GET', 'POST'])
@login_required
@manager_or_admin_required
def index():
    categories = Category.query.order_by(Category.category_name).all()

    if request.method == 'POST':
        period = request.form.get('target_period', '').strip() # YYYY-MM
        t_type = request.form.get('target_type', 'Monthly Revenue')
        cat_id = request.form.get('category_id', type=int) or None
        amount_str = request.form.get('target_amount', '0')

        try:
            amount = Decimal(amount_str)
        except Exception:
            flash('Target amount must be a valid positive number.', 'danger')
            return redirect(url_for('targets.index'))

        if amount <= Decimal('0.00'):
            flash('Target amount must be greater than zero.', 'danger')
            return redirect(url_for('targets.index'))

        existing = SalesTarget.query.filter_by(
            target_period=period, target_type=t_type, category_id=cat_id
        ).first()

        if existing:
            existing.target_amount = amount
            db.session.commit()
            flash(f'Updated target for {period} to ${amount:,.2f}.', 'success')
        else:
            new_target = SalesTarget(
                target_period=period,
                target_type=t_type,
                category_id=cat_id,
                target_amount=amount,
                created_by=current_user.user_id
            )
            db.session.add(new_target)
            db.session.commit()
            flash(f'Sales target created for {period} (${amount:,.2f}).', 'success')

        return redirect(url_for('targets.index'))

    # Load targets performance report
    target_data = ReportService.get_sales_target_report()
    return render_template('targets/index.html', targets=target_data, categories=categories)

@targets_bp.route('/<int:target_id>/delete', methods=['POST'])
@login_required
@manager_or_admin_required
def delete(target_id):
    target = SalesTarget.query.get_or_404(target_id)
    db.session.delete(target)
    db.session.commit()
    flash('Target deleted.', 'info')
    return redirect(url_for('targets.index'))
