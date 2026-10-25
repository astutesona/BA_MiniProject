from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models.category import Category
from app.services.analytics_service import AnalyticsService
from app.routes.dashboard import parse_filter_args

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
@login_required
def index():
    filters = parse_filter_args(request.args)
    categories = Category.query.order_by(Category.category_name).all()
    segments = ['Enterprise', 'SMB', 'Retail', 'Wholesale']

    kpis = AnalyticsService.get_kpis(filters)
    insights = AnalyticsService.get_business_insights(filters)

    return render_template(
        'analytics/index.html',
        kpis=kpis,
        insights=insights,
        categories=categories,
        segments=segments,
        filters=request.args
    )
