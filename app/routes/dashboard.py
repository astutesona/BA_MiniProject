from datetime import datetime, date
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.models.category import Category
from app.models.customer import Customer
from app.services.analytics_service import AnalyticsService

dashboard_bp = Blueprint('dashboard', __name__)

def parse_filter_args(args):
    filters = {}
    if args.get('start_date'):
        try:
            filters['start_date'] = datetime.strptime(args['start_date'], '%Y-%m-%d').date()
        except ValueError:
            pass
    if args.get('end_date'):
        try:
            filters['end_date'] = datetime.strptime(args['end_date'], '%Y-%m-%d').date()
        except ValueError:
            pass
    if args.get('category_id'):
        try:
            filters['category_id'] = int(args['category_id'])
        except ValueError:
            pass
    if args.get('customer_segment'):
        filters['customer_segment'] = args['customer_segment']
    if args.get('order_status'):
        filters['order_status'] = args['order_status']
    return filters

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    filters = parse_filter_args(request.args)
    categories = Category.query.order_by(Category.category_name).all()
    segments = ['Enterprise', 'SMB', 'Retail', 'Wholesale']
    
    kpis = AnalyticsService.get_kpis(filters)
    insights = AnalyticsService.get_business_insights(filters)

    return render_template(
        'dashboard/index.html',
        kpis=kpis,
        insights=insights,
        categories=categories,
        segments=segments,
        filters=request.args
    )

@dashboard_bp.route('/api/dashboard-charts')
@login_required
def chart_data():
    filters = parse_filter_args(request.args)
    
    monthly_trend = AnalyticsService.get_monthly_revenue_trend(filters)
    category_rev = AnalyticsService.get_category_revenue(filters)
    top_products = AnalyticsService.get_top_products(limit=8, filters=filters)
    profitability = AnalyticsService.get_product_profitability(limit=6, filters=filters)
    order_status = AnalyticsService.get_order_status_distribution(filters)
    target_vs_actual = AnalyticsService.get_target_vs_actual()
    customer_contrib = AnalyticsService.get_customer_revenue_contribution(limit=6, filters=filters)
    growth_series = AnalyticsService.get_revenue_growth_series()

    return jsonify({
        'monthly_trend': monthly_trend,
        'category_revenue': category_rev,
        'top_products': top_products,
        'profitability': profitability,
        'order_status': order_status,
        'target_vs_actual': target_vs_actual,
        'customer_contribution': customer_contrib,
        'growth_series': growth_series
    })
