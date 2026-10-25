from datetime import datetime
from flask import Blueprint, render_template, request, Response
from flask_login import login_required
from app.services.report_service import ReportService
from app.models.category import Category
from app.utils.decorators import manager_or_admin_required

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
@manager_or_admin_required
def index():
    report_type = request.args.get('report_type', 'monthly_sales')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category_id = request.args.get('category_id', type=int)
    segment = request.args.get('segment')
    export_csv = request.args.get('export', type=int) == 1

    categories = Category.query.order_by(Category.category_name).all()
    segments = ['Enterprise', 'SMB', 'Retail', 'Wholesale']

    data = []
    headers = []
    csv_rows = []

    if report_type == 'monthly_sales':
        data = ReportService.get_monthly_sales_report(start_date=start_date, end_date=end_date)
        headers = ['Month', 'Total Orders', 'Total Units Sold', 'Gross Revenue ($)', 'COGS ($)', 'Gross Profit ($)', 'Profit Margin (%)']
        for r in data:
            csv_rows.append([r['month'], r['total_orders'], r['total_units'], f"{r['revenue']:.2f}", f"{r['cogs']:.2f}", f"{r['gross_profit']:.2f}", f"{r['margin_pct']:.2f}%"])

    elif report_type == 'product_performance':
        data = ReportService.get_product_performance_report(category_id=category_id)
        headers = ['Product ID', 'Product Name', 'SKU', 'Category', 'Unit Price ($)', 'Unit Cost ($)', 'Stock', 'Units Sold', 'Revenue ($)', 'Profit ($)']
        for r in data:
            csv_rows.append([r['product_id'], r['product_name'], r['sku'], r['category_name'], f"{r['unit_price']:.2f}", f"{r['unit_cost']:.2f}", r['stock'], r['units_sold'], f"{r['revenue']:.2f}", f"{r['profit']:.2f}"])

    elif report_type == 'category_revenue':
        data = ReportService.get_category_revenue_report()
        headers = ['Category Name', 'Active Products', 'Units Sold', 'Total Revenue ($)', 'Total Profit ($)']
        for r in data:
            csv_rows.append([r['category_name'], r['total_products'], r['units_sold'], f"{r['revenue']:.2f}", f"{r['profit']:.2f}"])

    elif report_type == 'customer_sales':
        data = ReportService.get_customer_sales_report(segment=segment)
        headers = ['Customer ID', 'Customer Name', 'Segment', 'City', 'State', 'Orders Placed', 'Total Spent ($)']
        for r in data:
            csv_rows.append([r['customer_id'], r['customer_name'], r['segment'], r['city'], r['state'], r['orders'], f"{r['total_spent']:.2f}"])

    elif report_type == 'profitability':
        data = ReportService.get_profitability_report()
        headers = ['Category', 'Product Name', 'SKU', 'Recognized Revenue ($)', 'COGS ($)', 'Gross Profit ($)', 'Margin (%)']
        for r in data:
            csv_rows.append([r['category'], r['product'], r['sku'], f"{r['revenue']:.2f}", f"{r['cogs']:.2f}", f"{r['profit']:.2f}", f"{r['margin_pct']:.2f}%"])

    elif report_type == 'inventory':
        data = ReportService.get_inventory_report()
        headers = ['Product ID', 'Product Name', 'SKU', 'Category', 'Unit Cost ($)', 'Unit Price ($)', 'Stock Qty', 'Reorder Lvl', 'Status', 'Valuation ($)']
        for r in data:
            csv_rows.append([r['product_id'], r['product_name'], r['sku'], r['category'], f"{r['unit_cost']:.2f}", f"{r['unit_price']:.2f}", r['stock'], r['reorder_level'], r['status'], f"{r['valuation']:.2f}"])

    elif report_type == 'sales_targets':
        data = ReportService.get_sales_target_report()
        headers = ['Target ID', 'Period', 'Type', 'Category Scope', 'Target Amount ($)', 'Actual Revenue ($)', 'Achievement (%)', 'Status']
        for r in data:
            csv_rows.append([r['target_id'], r['period'], r['type'], r['category'], f"{r['target_amount']:.2f}", f"{r['actual_revenue']:.2f}", f"{r['achievement_pct']:.1f}%", r['status']])

    # CSV Download Handler
    if export_csv:
        csv_content = ReportService.generate_csv(headers, csv_rows)
        filename = f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )

    return render_template(
        'reports/index.html',
        report_type=report_type,
        data=data,
        headers=headers,
        categories=categories,
        segments=segments,
        start_date=start_date,
        end_date=end_date,
        selected_category=category_id,
        selected_segment=segment
    )
