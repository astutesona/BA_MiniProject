from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import func, distinct, case, text
from app.extensions import db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.category import Category
from app.models.customer import Customer
from app.models.sales_target import SalesTarget

class AnalyticsService:
    @staticmethod
    def _apply_filters(query, filters=None):
        """Applies consistent date range, category, segment, and status filters."""
        if not filters:
            return query

        if filters.get('start_date'):
            query = query.filter(Order.order_date >= filters['start_date'])
        if filters.get('end_date'):
            # Include entire end_date day
            end_dt = filters['end_date']
            if isinstance(end_dt, date) and not isinstance(end_dt, datetime):
                end_dt = datetime.combine(end_dt, datetime.max.time())
            query = query.filter(Order.order_date <= end_dt)

        if filters.get('category_id'):
            query = query.filter(Product.category_id == filters['category_id'])

        if filters.get('product_id'):
            query = query.filter(Product.product_id == filters['product_id'])

        if filters.get('customer_segment'):
            query = query.filter(Customer.customer_segment == filters['customer_segment'])

        if filters.get('order_status'):
            query = query.filter(Order.order_status == filters['order_status'])

        return query

    @classmethod
    def get_kpis(cls, filters=None):
        """
        Calculates the 8 core business intelligence KPIs:
        1. Total Revenue: recognized net revenue for Completed & Paid orders.
        2. Total Orders: distinct count of recognized orders.
        3. Total Units Sold: total units shipped in recognized orders.
        4. Total Profit: Gross Profit (Recognized Net Revenue - COGS).
        5. Average Order Value (AOV): Total Revenue / Total Orders.
        6. Sales Target Achievement: (Actual Revenue / Target Revenue) * 100.
        7. Revenue Growth: % change versus previous comparable period.
        8. Low-Stock Product Count: products below or at reorder threshold.
        """
        # Base query for recognized sales: Completed & Paid
        base_query = db.session.query(
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0).label('total_revenue'),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_cost_at_sale), 0).label('total_cogs'),
            func.count(distinct(Order.order_id)).label('total_orders'),
            func.coalesce(func.sum(OrderItem.quantity), 0).label('total_units')
        ).select_from(Order)\
         .join(OrderItem, Order.order_id == OrderItem.order_id)\
         .join(Product, OrderItem.product_id == Product.product_id)\
         .join(Customer, Order.customer_id == Customer.customer_id)\
         .filter(Order.order_status == 'Completed', Order.payment_status == 'Paid')

        base_query = cls._apply_filters(base_query, filters)
        row = base_query.one()

        total_rev = Decimal(str(row.total_revenue))
        total_cogs = Decimal(str(row.total_cogs))
        total_orders = int(row.total_orders or 0)
        total_units = int(row.total_units or 0)
        total_profit = total_rev - total_cogs

        # Average Order Value
        aov = (total_rev / Decimal(total_orders)) if total_orders > 0 else Decimal('0.00')

        # Target Achievement Calculation
        # Determine current target period (e.g. filters period or current YYYY-MM)
        target_period = None
        if filters and filters.get('month') and filters.get('year'):
            target_period = f"{filters['year']}-{int(filters['month']):02d}"
        elif filters and filters.get('start_date'):
            sd = filters['start_date']
            target_period = sd.strftime('%Y-%m') if isinstance(sd, (date, datetime)) else str(sd)[:7]
        else:
            target_period = datetime.now().strftime('%Y-%m')

        target_query = db.session.query(func.coalesce(func.sum(SalesTarget.target_amount), 0))\
            .filter(SalesTarget.target_period == target_period, SalesTarget.target_type == 'Monthly Revenue')
        if filters and filters.get('category_id'):
            target_query = target_query.filter(SalesTarget.category_id == filters['category_id'])

        target_amount = Decimal(str(target_query.scalar() or '0.00'))
        target_achievement = Decimal('0.00')
        if target_amount > Decimal('0.00'):
            target_achievement = round((total_rev / target_amount) * Decimal('100.00'), 1)

        # Revenue Growth versus Prior Period
        # If date range given, compute prior equivalent window length
        growth_pct = Decimal('0.00')
        has_prior_data = False
        if filters and filters.get('start_date') and filters.get('end_date'):
            s_date = filters['start_date']
            e_date = filters['end_date']
            if isinstance(s_date, str):
                s_date = datetime.strptime(s_date, '%Y-%m-%d').date()
            if isinstance(e_date, str):
                e_date = datetime.strptime(e_date, '%Y-%m-%d').date()

            duration = (e_date - s_date).days or 1
            prior_end = s_date - timedelta(days=1)
            prior_start = prior_end - timedelta(days=duration)

            prior_query = db.session.query(
                func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0)
            ).select_from(Order)\
             .join(OrderItem, Order.order_id == OrderItem.order_id)\
             .filter(Order.order_status == 'Completed', Order.payment_status == 'Paid')\
             .filter(Order.order_date >= prior_start, Order.order_date <= datetime.combine(prior_end, datetime.max.time()))

            prior_rev = Decimal(str(prior_query.scalar() or '0.00'))
            if prior_rev > Decimal('0.00'):
                growth_pct = round(((total_rev - prior_rev) / prior_rev) * Decimal('100.00'), 1)
                has_prior_data = True
            elif total_rev > Decimal('0.00') and prior_rev == Decimal('0.00'):
                growth_pct = Decimal('100.0')
                has_prior_data = True
        else:
            # Default: Compare current calendar month with previous calendar month
            now = datetime.now()
            first_this_month = date(now.year, now.month, 1)
            last_month_end = first_this_month - timedelta(days=1)
            first_last_month = date(last_month_end.year, last_month_end.month, 1)

            curr_month_rev = db.session.query(
                func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0)
            ).select_from(Order).join(OrderItem)\
             .filter(Order.order_status == 'Completed', Order.payment_status == 'Paid')\
             .filter(Order.order_date >= first_this_month).scalar() or 0

            last_month_rev = db.session.query(
                func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0)
            ).select_from(Order).join(OrderItem)\
             .filter(Order.order_status == 'Completed', Order.payment_status == 'Paid')\
             .filter(Order.order_date >= first_last_month, Order.order_date < first_this_month).scalar() or 0

            cm = Decimal(str(curr_month_rev))
            lm = Decimal(str(last_month_rev))
            if lm > 0:
                growth_pct = round(((cm - lm) / lm) * Decimal('100.00'), 1)
                has_prior_data = True
            elif cm > 0:
                growth_pct = Decimal('100.0')
                has_prior_data = True

        # Low-stock product count
        low_stock_count = Product.query.filter(
            Product.stock_quantity <= Product.reorder_level,
            Product.product_status == 'Active'
        ).count()

        return {
            'total_revenue': float(total_rev),
            'total_profit': float(total_profit),
            'profit_margin_pct': float(round((total_profit / total_rev * 100), 1)) if total_rev > 0 else 0.0,
            'total_orders': total_orders,
            'total_units_sold': total_units,
            'average_order_value': float(round(aov, 2)),
            'target_amount': float(target_amount),
            'target_achievement': float(target_achievement),
            'target_period': target_period,
            'growth_pct': float(growth_pct),
            'has_prior_data': has_prior_data,
            'low_stock_count': low_stock_count
        }

    @classmethod
    def get_monthly_revenue_trend(cls, filters=None):
        """Chart 1: Monthly Revenue Trend over time."""
        query = db.session.query(
            func.date_format(Order.order_date, '%Y-%m').label('sales_month'),
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0).label('monthly_revenue'),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_cost_at_sale), 0).label('monthly_cogs')
        ).select_from(Order)\
         .join(OrderItem, Order.order_id == OrderItem.order_id)\
         .join(Product, OrderItem.product_id == Product.product_id)\
         .join(Customer, Order.customer_id == Customer.customer_id)\
         .filter(Order.order_status == 'Completed', Order.payment_status == 'Paid')

        query = cls._apply_filters(query, filters)
        results = query.group_by('sales_month').order_by('sales_month').all()

        labels = [r.sales_month for r in results]
        revenue = [float(r.monthly_revenue) for r in results]
        cogs = [float(r.monthly_cogs) for r in results]
        profit = [float(r.monthly_revenue - r.monthly_cogs) for r in results]

        return {
            'labels': labels,
            'revenue': revenue,
            'cogs': cogs,
            'profit': profit
        }

    @classmethod
    def get_category_revenue(cls, filters=None):
        """Chart 2: Revenue and Margin by Product Category."""
        query = db.session.query(
            Category.category_name,
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0).label('revenue'),
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount - (OrderItem.quantity * OrderItem.unit_cost_at_sale)), 0).label('profit')
        ).select_from(Category)\
         .join(Product, Category.category_id == Product.category_id)\
         .join(OrderItem, Product.product_id == OrderItem.product_id)\
         .join(Order, OrderItem.order_id == Order.order_id)\
         .join(Customer, Order.customer_id == Customer.customer_id)\
         .filter(Order.order_status == 'Completed', Order.payment_status == 'Paid')

        query = cls._apply_filters(query, filters)
        results = query.group_by(Category.category_id, Category.category_name).order_by(text('revenue DESC')).all()

        labels = [r.category_name for r in results]
        revenues = [float(r.revenue) for r in results]
        profits = [float(r.profit) for r in results]

        return {
            'labels': labels,
            'revenue': revenues,
            'profit': profits
        }

    @classmethod
    def get_top_products(cls, limit=10, filters=None):
        """Chart 3: Top N Products by Recognized Sales Revenue."""
        query = db.session.query(
            Product.product_name,
            Product.SKU,
            func.sum(OrderItem.quantity).label('units_sold'),
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0).label('revenue')
        ).select_from(Product)\
         .join(OrderItem, Product.product_id == OrderItem.product_id)\
         .join(Order, OrderItem.order_id == Order.order_id)\
         .join(Customer, Order.customer_id == Customer.customer_id)\
         .filter(Order.order_status == 'Completed', Order.payment_status == 'Paid')

        query = cls._apply_filters(query, filters)
        results = query.group_by(Product.product_id, Product.product_name, Product.SKU)\
                       .order_by(text('revenue DESC')).limit(limit).all()

        return {
            'labels': [r.product_name for r in results],
            'skus': [r.SKU for r in results],
            'units': [int(r.units_sold) for r in results],
            'revenue': [float(r.revenue) for r in results]
        }

    @classmethod
    def get_product_profitability(cls, limit=8, filters=None):
        """Chart 4: Product Profitability (Revenue, COGS, Gross Profit)."""
        query = db.session.query(
            Product.product_name,
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0).label('revenue'),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_cost_at_sale), 0).label('cogs'),
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount - (OrderItem.quantity * OrderItem.unit_cost_at_sale)), 0).label('profit')
        ).select_from(Product)\
         .join(OrderItem, Product.product_id == OrderItem.product_id)\
         .join(Order, OrderItem.order_id == Order.order_id)\
         .join(Customer, Order.customer_id == Customer.customer_id)\
         .filter(Order.order_status == 'Completed', Order.payment_status == 'Paid')

        query = cls._apply_filters(query, filters)
        results = query.group_by(Product.product_id, Product.product_name)\
                       .order_by(text('revenue DESC')).limit(limit).all()

        return {
            'labels': [r.product_name for r in results],
            'revenue': [float(r.revenue) for r in results],
            'cogs': [float(r.cogs) for r in results],
            'profit': [float(r.profit) for r in results]
        }

    @classmethod
    def get_order_status_distribution(cls, filters=None):
        """Chart 5: Order Status Breakdown (Doughnut Chart)."""
        query = db.session.query(
            Order.order_status,
            func.count(Order.order_id).label('status_count')
        ).select_from(Order)\
         .join(Customer, Order.customer_id == Customer.customer_id)

        # Do not filter out cancelled/pending here because we want to see distribution!
        if filters:
            if filters.get('start_date'):
                query = query.filter(Order.order_date >= filters['start_date'])
            if filters.get('end_date'):
                query = query.filter(Order.order_date <= filters['end_date'])
            if filters.get('customer_segment'):
                query = query.filter(Customer.customer_segment == filters['customer_segment'])

        results = query.group_by(Order.order_status).order_by(text('status_count DESC')).all()
        return {
            'labels': [r.order_status for r in results],
            'counts': [int(r.status_count) for r in results]
        }

    @classmethod
    def get_target_vs_actual(cls, year=None):
        """Chart 6: Monthly Sales Target vs Actual Recognized Revenue."""
        if not year:
            year = datetime.now().year

        # Actual sales by month for the given year
        actuals_query = db.session.query(
            func.date_format(Order.order_date, '%Y-%m').label('month'),
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0).label('actual_rev')
        ).select_from(Order).join(OrderItem)\
         .filter(Order.order_status == 'Completed', Order.payment_status == 'Paid')\
         .filter(func.date_format(Order.order_date, '%Y') == str(year))\
         .group_by('month').all()

        actuals_map = {r.month: float(r.actual_rev) for r in actuals_query}

        # Targets for the year
        targets_query = db.session.query(
            SalesTarget.target_period,
            func.sum(SalesTarget.target_amount).label('target_rev')
        ).filter(SalesTarget.target_period.like(f"{year}-%"), SalesTarget.target_type == 'Monthly Revenue')\
         .group_by(SalesTarget.target_period).order_by(SalesTarget.target_period).all()

        target_map = {r.target_period: float(r.target_rev) for r in targets_query}

        # Combine all months that appear in either targets or actuals
        all_months = sorted(list(set(list(actuals_map.keys()) + list(target_map.keys()))))
        if not all_months:
            # Fallback to last 6 months
            all_months = [f"{year}-{m:02d}" for m in range(1, 13)]

        target_data = [target_map.get(m, 0.0) for m in all_months]
        actual_data = [actuals_map.get(m, 0.0) for m in all_months]

        return {
            'labels': all_months,
            'targets': target_data,
            'actuals': actual_data
        }

    @classmethod
    def get_customer_revenue_contribution(cls, limit=10, filters=None):
        """Chart 7: Top Customer Accounts by Recognized Revenue."""
        query = db.session.query(
            Customer.customer_name,
            Customer.customer_segment,
            func.count(distinct(Order.order_id)).label('orders_count'),
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0).label('total_spent')
        ).select_from(Customer)\
         .join(Order, Customer.customer_id == Order.customer_id)\
         .join(OrderItem, Order.order_id == OrderItem.order_id)\
         .join(Product, OrderItem.product_id == Product.product_id)\
         .filter(Order.order_status == 'Completed', Order.payment_status == 'Paid')

        query = cls._apply_filters(query, filters)
        results = query.group_by(Customer.customer_id, Customer.customer_name, Customer.customer_segment)\
                       .order_by(text('total_spent DESC')).limit(limit).all()

        return {
            'labels': [r.customer_name for r in results],
            'segments': [r.customer_segment for r in results],
            'orders': [int(r.orders_count) for r in results],
            'spent': [float(r.total_spent) for r in results]
        }

    @classmethod
    def get_revenue_growth_series(cls):
        """Chart 8: Consecutive Monthly Revenue Comparison & Growth Rate."""
        query = db.session.query(
            func.date_format(Order.order_date, '%Y-%m').label('month'),
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0).label('rev')
        ).select_from(Order).join(OrderItem)\
         .filter(Order.order_status == 'Completed', Order.payment_status == 'Paid')\
         .group_by('month').order_by('month').all()

        months = [r.month for r in query]
        revenues = [float(r.rev) for r in query]
        growth_rates = []

        for i in range(len(revenues)):
            if i == 0 or revenues[i-1] == 0:
                growth_rates.append(0.0)
            else:
                pct = ((revenues[i] - revenues[i-1]) / revenues[i-1]) * 100.0
                growth_rates.append(round(pct, 2))

        return {
            'labels': months,
            'revenue': revenues,
            'growth_rate': growth_rates
        }

    @classmethod
    def get_business_insights(cls, filters=None):
        """
        Generates dynamic, evidence-based business insights from actual database calculations.
        No fabricated or static placeholders.
        """
        insights = []

        # 1. Top performing category insight
        top_cat_query = db.session.query(
            Category.category_name,
            func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount).label('cat_rev')
        ).select_from(Category)\
         .join(Product, Category.category_id == Product.category_id)\
         .join(OrderItem, Product.product_id == OrderItem.product_id)\
         .join(Order, OrderItem.order_id == Order.order_id)\
         .filter(Order.order_status == 'Completed', Order.payment_status == 'Paid')

        if filters and filters.get('start_date'):
            top_cat_query = top_cat_query.filter(Order.order_date >= filters['start_date'])
        if filters and filters.get('end_date'):
            top_cat_query = top_cat_query.filter(Order.order_date <= filters['end_date'])

        top_cat = top_cat_query.group_by(Category.category_name).order_by(text('cat_rev DESC')).first()

        total_rev_all = db.session.query(
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0)
        ).select_from(Order).join(OrderItem)\
         .filter(Order.order_status == 'Completed', Order.payment_status == 'Paid').scalar() or 0

        if top_cat and total_rev_all > 0:
            pct_share = round((float(top_cat.cat_rev) / float(total_rev_all)) * 100, 1)
            insights.append({
                'type': 'success',
                'category': 'Revenue Driver',
                'title': f'Category Dominance: {top_cat.category_name}',
                'description': f'{top_cat.category_name} generated the highest revenue (${float(top_cat.cat_rev):,.2f}), representing {pct_share}% of all eligible completed sales.'
            })

        # 2. Inventory warning insight
        low_stock_prods = Product.query.filter(
            Product.stock_quantity <= Product.reorder_level,
            Product.product_status == 'Active'
        ).all()
        if low_stock_prods:
            prod_names = ", ".join([p.product_name for p in low_stock_prods[:3]])
            suffix = f" and {len(low_stock_prods)-3} others" if len(low_stock_prods) > 3 else ""
            insights.append({
                'type': 'warning',
                'category': 'Inventory Alert',
                'title': f'Stock Warning: {len(low_stock_prods)} Products Below Reorder Level',
                'description': f'Items requiring immediate replenishment include: {prod_names}{suffix}. Stockout risk could constrain prospective order fulfillment.'
            })
        else:
            insights.append({
                'type': 'info',
                'category': 'Inventory Health',
                'title': 'Adequate Inventory Reserves',
                'description': 'All catalog items are currently operating at or above safety threshold reorder buffers.'
            })

        # 3. Monthly target achievement insight
        current_period = datetime.now().strftime('%Y-%m')
        target_obj = SalesTarget.query.filter_by(target_period=current_period, target_type='Monthly Revenue', category_id=None).first()
        if target_obj:
            month_rev = db.session.query(
                func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0)
            ).select_from(Order).join(OrderItem)\
             .filter(Order.order_status == 'Completed', Order.payment_status == 'Paid')\
             .filter(func.date_format(Order.order_date, '%Y-%m') == current_period).scalar() or 0

            achieve_pct = round((float(month_rev) / float(target_obj.target_amount)) * 100, 1)
            status_text = "met or exceeded" if achieve_pct >= 100 else "progressing toward"
            insights.append({
                'type': 'primary' if achieve_pct >= 100 else 'info',
                'category': 'Target Benchmark',
                'title': f'Target Tracking for {current_period}: {achieve_pct}%',
                'description': f'Current month revenue (${float(month_rev):,.2f}) is {status_text} the benchmark target of ${float(target_obj.target_amount):,.2f}.'
            })

        # 4. Customer segment concentration insight
        seg_query = db.session.query(
            Customer.customer_segment,
            func.coalesce(func.sum((OrderItem.quantity * OrderItem.unit_price_at_sale) - OrderItem.discount_amount), 0).label('seg_rev'),
            func.count(distinct(Order.order_id)).label('seg_orders')
        ).select_from(Customer)\
         .join(Order, Customer.customer_id == Order.customer_id)\
         .join(OrderItem, Order.order_id == OrderItem.order_id)\
         .filter(Order.order_status == 'Completed', Order.payment_status == 'Paid')\
         .group_by(Customer.customer_segment).order_by(text('seg_rev DESC')).first()

        if seg_query:
            avg_ticket = (float(seg_query.seg_rev) / seg_query.seg_orders) if seg_query.seg_orders > 0 else 0
            insights.append({
                'type': 'dark',
                'category': 'Customer Segmentation',
                'title': f'Key Client Cohort: {seg_query.customer_segment}',
                'description': f'The {seg_query.customer_segment} segment generated the largest sales share (${float(seg_query.seg_rev):,.2f} across {seg_query.seg_orders} orders) with an Average Order Ticket of ${avg_ticket:,.2f}.'
            })

        return insights
