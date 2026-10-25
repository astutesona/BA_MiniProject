import io
import csv
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import func, text
from app.extensions import db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.category import Category
from app.models.customer import Customer
from app.models.sales_target import SalesTarget

class ReportService:
    @staticmethod
    def sanitize_csv_field(val):
        """
        Guards against CSV / Formula Injection (CWE-1236).
        Prepends single quote if string begins with =, +, -, @, tab, or carriage return.
        """
        if val is None:
            return ""
        s = str(val)
        if s and s[0] in ('=', '+', '-', '@', '\t', '\r'):
            return f"'{s}"
        return s

    @classmethod
    def generate_csv(cls, headers, rows):
        """Generates RFC 4180-compliant CSV string in memory with formula sanitation."""
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        writer.writerow([cls.sanitize_csv_field(h) for h in headers])
        for row in rows:
            writer.writerow([cls.sanitize_csv_field(col) for col in row])
        return output.getvalue()

    @staticmethod
    def get_monthly_sales_report(start_date=None, end_date=None):
        month_col = func.date_format(Order.order_date, '%Y-%m').label('month')
        query = db.session.query(
            month_col,
            func.count(func.distinct(Order.order_id)).label('total_orders'),
            func.coalesce(func.sum(OrderItem.quantity), 0).label('total_units'),
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0).label('revenue'),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_cost_at_sale), 0).label('cogs')
        ).select_from(Order).join(OrderItem)\
         .filter(Order.order_status == 'Completed', Order.payment_status == 'Paid')

        if start_date:
            query = query.filter(Order.order_date >= start_date)
        if end_date:
            query = query.filter(Order.order_date <= end_date)

        results = query.group_by(month_col).order_by(month_col.desc()).all()
        data = []
        for r in results:
            rev = float(r.revenue)
            cogs = float(r.cogs)
            profit = rev - cogs
            margin = round((profit / rev * 100), 2) if rev > 0 else 0.0
            data.append({
                'month': r.month,
                'total_orders': int(r.total_orders),
                'total_units': int(r.total_units),
                'revenue': rev,
                'cogs': cogs,
                'gross_profit': profit,
                'margin_pct': margin
            })
        return data

    @staticmethod
    def get_product_performance_report(category_id=None):
        query = db.session.query(
            Product.product_id,
            Product.product_name,
            Product.SKU,
            Category.category_name,
            Product.unit_price,
            Product.unit_cost,
            Product.stock_quantity,
            func.coalesce(func.sum(OrderItem.quantity), 0).label('units_sold'),
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0).label('revenue'),
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount - (OrderItem.quantity * OrderItem.unit_cost_at_sale)), 0).label('profit')
        ).join(Category, Product.category_id == Category.category_id)\
         .outerjoin(OrderItem, Product.product_id == OrderItem.product_id)\
         .outerjoin(Order, (OrderItem.order_id == Order.order_id) & (Order.order_status == 'Completed') & (Order.payment_status == 'Paid'))

        if category_id:
            query = query.filter(Product.category_id == category_id)

        results = query.group_by(Product.product_id, Product.product_name, Product.SKU, Category.category_name, Product.unit_price, Product.unit_cost, Product.stock_quantity)\
                       .order_by(text('revenue DESC')).all()

        return [{
            'product_id': r.product_id,
            'product_name': r.product_name,
            'sku': r.SKU,
            'category_name': r.category_name,
            'unit_price': float(r.unit_price),
            'unit_cost': float(r.unit_cost),
            'stock': r.stock_quantity,
            'units_sold': int(r.units_sold),
            'revenue': float(r.revenue),
            'profit': float(r.profit)
        } for r in results]

    @staticmethod
    def get_category_revenue_report():
        results = db.session.query(
            Category.category_name,
            func.count(func.distinct(Product.product_id)).label('total_products'),
            func.coalesce(func.sum(OrderItem.quantity), 0).label('units_sold'),
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0).label('revenue'),
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount - (OrderItem.quantity * OrderItem.unit_cost_at_sale)), 0).label('profit')
        ).join(Product, Category.category_id == Product.category_id)\
         .outerjoin(OrderItem, Product.product_id == OrderItem.product_id)\
         .outerjoin(Order, (OrderItem.order_id == Order.order_id) & (Order.order_status == 'Completed') & (Order.payment_status == 'Paid'))\
         .group_by(Category.category_id, Category.category_name)\
         .order_by(text('revenue DESC')).all()

        return [{
            'category_name': r.category_name,
            'total_products': int(r.total_products),
            'units_sold': int(r.units_sold),
            'revenue': float(r.revenue),
            'profit': float(r.profit)
        } for r in results]

    @staticmethod
    def get_customer_sales_report(segment=None):
        query = db.session.query(
            Customer.customer_id,
            Customer.customer_name,
            Customer.customer_segment,
            Customer.city,
            Customer.state,
            func.count(func.distinct(Order.order_id)).label('order_count'),
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0).label('total_spent')
        ).outerjoin(Order, (Customer.customer_id == Order.customer_id) & (Order.order_status == 'Completed') & (Order.payment_status == 'Paid'))\
         .outerjoin(OrderItem, Order.order_id == OrderItem.order_id)

        if segment:
            query = query.filter(Customer.customer_segment == segment)

        results = query.group_by(Customer.customer_id, Customer.customer_name, Customer.customer_segment, Customer.city, Customer.state)\
                       .order_by(text('total_spent DESC')).all()

        return [{
            'customer_id': r.customer_id,
            'customer_name': r.customer_name,
            'segment': r.customer_segment,
            'city': r.city,
            'state': r.state,
            'orders': int(r.order_count),
            'total_spent': float(r.total_spent)
        } for r in results]

    @staticmethod
    def get_profitability_report():
        results = db.session.query(
            Category.category_name,
            Product.product_name,
            Product.SKU,
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0).label('revenue'),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_cost_at_sale), 0).label('cogs'),
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount - (OrderItem.quantity * OrderItem.unit_cost_at_sale)), 0).label('profit')
        ).join(Product, Category.category_id == Product.category_id)\
         .join(OrderItem, Product.product_id == OrderItem.product_id)\
         .join(Order, (OrderItem.order_id == Order.order_id) & (Order.order_status == 'Completed') & (Order.payment_status == 'Paid'))\
         .group_by(Category.category_id, Category.category_name, Product.product_id, Product.product_name, Product.SKU)\
         .order_by(text('profit DESC')).all()

        return [{
            'category': r.category_name,
            'product': r.product_name,
            'sku': r.SKU,
            'revenue': float(r.revenue),
            'cogs': float(r.cogs),
            'profit': float(r.profit),
            'margin_pct': round((float(r.profit) / float(r.revenue) * 100), 2) if r.revenue > 0 else 0.0
        } for r in results]

    @staticmethod
    def get_inventory_report():
        results = db.session.query(
            Product.product_id,
            Product.product_name,
            Product.SKU,
            Category.category_name,
            Product.unit_cost,
            Product.unit_price,
            Product.stock_quantity,
            Product.reorder_level,
            Product.product_status,
            (Product.stock_quantity * Product.unit_cost).label('valuation')
        ).join(Category, Product.category_id == Category.category_id)\
         .order_by(Product.stock_quantity.asc()).all()

        return [{
            'product_id': r.product_id,
            'product_name': r.product_name,
            'sku': r.SKU,
            'category': r.category_name,
            'unit_cost': float(r.unit_cost),
            'unit_price': float(r.unit_price),
            'stock': r.stock_quantity,
            'reorder_level': r.reorder_level,
            'status': r.product_status,
            'valuation': float(r.valuation)
        } for r in results]

    @staticmethod
    def get_sales_target_report(year=None):
        if not year:
            year = datetime.now().year

        results = db.session.query(
            SalesTarget.target_id,
            SalesTarget.target_period,
            SalesTarget.target_type,
            Category.category_name,
            SalesTarget.target_amount
        ).outerjoin(Category, SalesTarget.category_id == Category.category_id)\
         .filter(SalesTarget.target_period.like(f"{year}-%"))\
         .order_by(SalesTarget.target_period.desc(), SalesTarget.target_type).all()

        data = []
        for r in results:
            # Query actual revenue for period and category
            q = db.session.query(
                func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0)
            ).select_from(Order).join(OrderItem).join(Product)\
             .filter(Order.order_status == 'Completed', Order.payment_status == 'Paid')\
             .filter(func.date_format(Order.order_date, '%Y-%m') == r.target_period)

            if r.category_name:
                q = q.filter(Product.category_id == SalesTarget.category_id)

            actual_rev = float(q.scalar() or 0.0)
            target_amt = float(r.target_amount)
            pct = round((actual_rev / target_amt * 100), 1) if target_amt > 0 else 0.0

            data.append({
                'target_id': r.target_id,
                'period': r.target_period,
                'type': r.target_type,
                'category': r.category_name or 'Overall',
                'target_amount': target_amt,
                'actual_revenue': actual_rev,
                'achievement_pct': pct,
                'status': 'Achieved' if pct >= 100 else ('Near Target' if pct >= 80 else 'Underperforming')
            })
        return data
