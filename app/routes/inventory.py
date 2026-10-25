from flask import Blueprint, render_template, request
from flask_login import login_required
from app.services.inventory_service import InventoryService
from app.models.category import Category

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('/')
@login_required
def index():
    days = request.args.get('days', 90, type=int)
    summary = InventoryService.get_inventory_summary()
    cat_valuation = InventoryService.get_category_inventory_valuation()
    velocity = InventoryService.get_velocity_analysis(days=days)

    return render_template(
        'inventory/index.html',
        summary=summary,
        category_valuation=cat_valuation,
        velocity=velocity,
        selected_days=days
    )
