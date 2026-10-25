import time
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import text
from app.extensions import db
from app.utils.decorators import role_required

query_lab_bp = Blueprint('query_lab', __name__, url_prefix='/query-lab')

# Predefined analytical queries catalog demonstrating core DBMS concepts
PREDEFINED_QUERIES = [
    {
        "id": 1,
        "title": "Active Product Catalog with Price Sorting & Limits",
        "category": "Basic DML & Filtering",
        "purpose": "Retrieve active catalog products ordered by price descending to inspect premium inventory offerings.",
        "concepts": "SELECT, INNER JOIN, WHERE, ORDER BY, LIMIT",
        "sql": """SELECT 
    p.product_id,
    p.product_name,
    p.SKU,
    c.category_name,
    p.unit_price,
    p.unit_cost,
    p.stock_quantity,
    p.product_status
FROM products p
JOIN categories c ON p.category_id = c.category_id
WHERE p.product_status = 'Active'
ORDER BY p.unit_price DESC
LIMIT 10;"""
    },
    {
        "id": 2,
        "title": "Category-wise Revenue, Volume, and Gross Margin Analysis",
        "category": "Grouping & Aggregations",
        "purpose": "Aggregates recognized sales by category, calculating gross sales, COGS, gross margin, and profit percentage.",
        "concepts": "INNER JOIN, GROUP BY, SUM, COUNT, Arithmetic, NULLIF, ORDER BY",
        "sql": """SELECT 
    c.category_id,
    c.category_name,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity) AS total_units_sold,
    CAST(SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS DECIMAL(12,2)) AS gross_revenue,
    CAST(SUM(oi.quantity * oi.unit_cost_at_sale) AS DECIMAL(12,2)) AS total_cogs,
    CAST(SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount - (oi.quantity * oi.unit_cost_at_sale)) AS DECIMAL(12,2)) AS gross_profit,
    ROUND(
        (SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount - (oi.quantity * oi.unit_cost_at_sale)) / 
        NULLIF(SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount), 0)) * 100, 2
    ) AS profit_margin_pct
FROM categories c
JOIN products p ON c.category_id = p.category_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed' AND o.payment_status = 'Paid'
GROUP BY c.category_id, c.category_name
ORDER BY gross_revenue DESC;"""
    },
    {
        "id": 3,
        "title": "Top 10 High-Revenue Generating Products",
        "category": "Multi-Table Joins & Ranking",
        "purpose": "Identify the top 10 products contributing the highest net revenue after line-item discounts.",
        "concepts": "INNER JOIN, GROUP BY, SUM(), ORDER BY DESC, LIMIT",
        "sql": """SELECT 
    p.product_id,
    p.product_name,
    p.SKU,
    c.category_name,
    SUM(oi.quantity) AS units_sold,
    CAST(SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS DECIMAL(12,2)) AS recognized_revenue,
    CAST(SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount - (oi.quantity * oi.unit_cost_at_sale)) AS DECIMAL(12,2)) AS total_profit
FROM products p
JOIN categories c ON p.category_id = c.category_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed' AND o.payment_status = 'Paid'
GROUP BY p.product_id, p.product_name, p.SKU, c.category_name
ORDER BY recognized_revenue DESC
LIMIT 10;"""
    },
    {
        "id": 4,
        "title": "Monthly Sales Trend with Year-over-Year Aggregates",
        "category": "Time-Series Analytics",
        "purpose": "Track sales volume, line items, and aggregate revenue month by month.",
        "concepts": "DATE_FORMAT, GROUP BY, COUNT(DISTINCT), SUM, AVG",
        "sql": """SELECT 
    DATE_FORMAT(o.order_date, '%Y-%m') AS sales_month,
    COUNT(DISTINCT o.order_id) AS orders_count,
    SUM(oi.quantity) AS units_sold,
    CAST(SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS DECIMAL(12,2)) AS monthly_revenue,
    CAST(AVG((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS DECIMAL(10,2)) AS avg_line_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed' AND o.payment_status = 'Paid'
GROUP BY DATE_FORMAT(o.order_date, '%Y-%m')
ORDER BY sales_month ASC;"""
    },
    {
        "id": 5,
        "title": "High-Value Customers with Spending Above $1,000",
        "category": "Customer Segmentation & Filtering",
        "purpose": "Filter enterprise or retail accounts having cumulative recognized spending over $1,000.",
        "concepts": "INNER JOIN, GROUP BY, HAVING, MAX(), Aggregate Filtering",
        "sql": """SELECT 
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    c.city,
    COUNT(DISTINCT o.order_id) AS order_frequency,
    MAX(o.order_date) AS last_order_date,
    CAST(SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS DECIMAL(12,2)) AS total_monetary_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed' AND o.payment_status = 'Paid'
GROUP BY c.customer_id, c.customer_name, c.customer_segment, c.city
HAVING total_monetary_spent > 1000
ORDER BY total_monetary_spent DESC;"""
    },
    {
        "id": 6,
        "title": "Average Order Value (AOV) by Customer Segment",
        "category": "Nested Subqueries",
        "purpose": "Calculates segment-level AOV by aggregating order totals via an derived subquery table.",
        "concepts": "Derived Table Subquery, JOIN, GROUP BY, AVG(), CAST()",
        "sql": """SELECT 
    c.customer_segment,
    COUNT(DISTINCT order_sub.order_id) AS total_orders,
    CAST(SUM(order_sub.order_net_total) AS DECIMAL(12,2)) AS segment_revenue,
    CAST(AVG(order_sub.order_net_total) AS DECIMAL(10,2)) AS avg_order_value
FROM customers c
JOIN (
    SELECT 
        o.order_id,
        o.customer_id,
        SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS order_net_total
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed' AND o.payment_status = 'Paid'
    GROUP BY o.order_id, o.customer_id
) AS order_sub ON c.customer_id = order_sub.customer_id
GROUP BY c.customer_segment
ORDER BY segment_revenue DESC;"""
    },
    {
        "id": 7,
        "title": "Target vs Actual Performance with Status Classification",
        "category": "Conditional Aggregation & Outer Joins",
        "purpose": "Evaluates sales targets against actual recognized revenue with conditional status flags.",
        "concepts": "LEFT JOIN, Aggregated Subquery, COALESCE, CASE WHEN, Percentage Math",
        "sql": """SELECT 
    st.target_period,
    st.target_type,
    COALESCE(c.category_name, 'All Categories') AS category_scope,
    st.target_amount,
    COALESCE(act.actual_revenue, 0.00) AS actual_revenue,
    ROUND((COALESCE(act.actual_revenue, 0.00) / st.target_amount) * 100, 2) AS achievement_percentage,
    CASE 
        WHEN COALESCE(act.actual_revenue, 0.00) >= st.target_amount THEN 'Achieved'
        WHEN (COALESCE(act.actual_revenue, 0.00) / st.target_amount) >= 0.80 THEN 'Near Target'
        ELSE 'Underperforming'
    END AS target_status
FROM sales_targets st
LEFT JOIN categories c ON st.category_id = c.category_id
LEFT JOIN (
    SELECT 
        DATE_FORMAT(o.order_date, '%Y-%m') AS period,
        p.category_id,
        SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS actual_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.order_status = 'Completed' AND o.payment_status = 'Paid'
    GROUP BY DATE_FORMAT(o.order_date, '%Y-%m'), p.category_id
) AS act ON st.target_period = act.period AND (st.category_id = act.category_id OR st.category_id IS NULL)
ORDER BY st.target_period DESC;"""
    },
    {
        "id": 8,
        "title": "Inventory Stock Valuation & Safety Reorder Alerts",
        "category": "Conditional Logic & Valuation",
        "purpose": "Monitors stock levels against reorder thresholds and classifies operational health.",
        "concepts": "CASE expression, Arithmetic Multiplication, ORDER BY ASC",
        "sql": """SELECT 
    p.product_id,
    p.product_name,
    c.category_name,
    p.stock_quantity,
    p.reorder_level,
    p.unit_cost,
    CAST((p.stock_quantity * p.unit_cost) AS DECIMAL(12,2)) AS inventory_valuation,
    CASE 
        WHEN p.stock_quantity = 0 THEN 'OUT_OF_STOCK'
        WHEN p.stock_quantity <= p.reorder_level THEN 'REORDER_NOW'
        WHEN p.stock_quantity <= (p.reorder_level * 1.5) THEN 'LOW_STOCK'
        ELSE 'ADEQUATE'
    END AS stock_health_status
FROM products p
JOIN categories c ON p.category_id = c.category_id
ORDER BY p.stock_quantity ASC;"""
    },
    {
        "id": 9,
        "title": "Order Fulfillment & Payment Health Distribution",
        "category": "Conditional Aggregation (Pivoting)",
        "purpose": "Pivots all orders across operational and payment statuses into single-row executive metrics.",
        "concepts": "SUM(CASE WHEN ...), COUNT(*), Conditional Aggregation",
        "sql": """SELECT 
    COUNT(*) AS total_order_count,
    SUM(CASE WHEN order_status = 'Completed' AND payment_status = 'Paid' THEN 1 ELSE 0 END) AS completed_orders,
    SUM(CASE WHEN order_status = 'Pending' THEN 1 ELSE 0 END) AS pending_orders,
    SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
    SUM(CASE WHEN order_status = 'Returned' OR payment_status = 'Refunded' THEN 1 ELSE 0 END) AS returned_orders
FROM orders;"""
    },
    {
        "id": 10,
        "title": "Slow-Moving Inventory Audit (No Sales in Last 90 Days)",
        "category": "Subquery Negation",
        "purpose": "Detects products that have generated zero sales in the last 90-day window.",
        "concepts": "NOT IN Subquery, DATE_SUB, CURDATE(), Filtering",
        "sql": """SELECT 
    p.product_id,
    p.product_name,
    c.category_name,
    p.stock_quantity,
    p.unit_price
FROM products p
JOIN categories c ON p.category_id = c.category_id
WHERE p.product_id NOT IN (
    SELECT DISTINCT oi.product_id
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
      AND o.order_status = 'Completed'
)
ORDER BY p.stock_quantity DESC;"""
    },
    {
        "id": 11,
        "title": "Window Function: Product Revenue Ranking within Categories",
        "category": "Window Functions & CTE",
        "purpose": "Ranks products by total sales strictly within their parent categories using DENSE_RANK().",
        "concepts": "Common Table Expression (WITH), DENSE_RANK() OVER (PARTITION BY ... ORDER BY ...)",
        "sql": """WITH category_product_sales AS (
    SELECT 
        c.category_name,
        p.product_name,
        CAST(SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS DECIMAL(12,2)) AS total_sales
    FROM products p
    JOIN categories c ON p.category_id = c.category_id
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'Completed' AND o.payment_status = 'Paid'
    GROUP BY c.category_name, p.product_name
)
SELECT 
    category_name,
    product_name,
    total_sales,
    DENSE_RANK() OVER (PARTITION BY category_name ORDER BY total_sales DESC) as category_rank
FROM category_product_sales
ORDER BY category_name, category_rank;"""
    },
    {
        "id": 12,
        "title": "High-Value Orders Exceeding Overall Average Order Value",
        "category": "Scalar Subquery Comparison",
        "purpose": "Filters individual orders whose monetary total exceeds the global historical average.",
        "concepts": "Scalar Subquery in HAVING, Multi-level Aggregation, HAVING comparison",
        "sql": """SELECT 
    o.order_id,
    o.order_date,
    c.customer_name,
    c.city,
    CAST(SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS DECIMAL(10,2)) AS order_total
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed' AND o.payment_status = 'Paid'
GROUP BY o.order_id, o.order_date, c.customer_name, c.city
HAVING order_total > (
    SELECT AVG(item_sum.total_amount)
    FROM (
        SELECT SUM((sub_oi.quantity * sub_oi.unit_price_at_sale) - sub_oi.discount_amount) AS total_amount
        FROM orders sub_o
        JOIN order_items sub_oi ON sub_o.order_id = sub_oi.order_id
        WHERE sub_o.order_status = 'Completed' AND sub_o.payment_status = 'Paid'
        GROUP BY sub_o.order_id
    ) AS item_sum
)
ORDER BY order_total DESC
LIMIT 15;"""
    }
]

@query_lab_bp.route('/')
@login_required
@role_required('Admin', 'Manager')
def index():
    return render_template('query_lab/index.html', queries=PREDEFINED_QUERIES)

@query_lab_bp.route('/execute/<int:query_id>', methods=['POST'])
@login_required
@role_required('Admin', 'Manager')
def execute_predefined(query_id):
    query_item = next((q for q in PREDEFINED_QUERIES if q["id"] == query_id), None)
    if not query_item:
        return jsonify({'success': False, 'error': f'Query ID #{query_id} not found.'}), 404

    sql_statement = query_item["sql"]
    t0 = time.time()
    try:
        result_proxy = db.session.execute(text(sql_statement))
        columns = list(result_proxy.keys())
        rows = [list(r) for r in result_proxy.fetchall()]
        duration_ms = round((time.time() - t0) * 1000, 2)

        # Convert non-serializable objects (Decimal, Date) to strings
        formatted_rows = []
        for r in rows:
            formatted_row = []
            for cell in r:
                if cell is None:
                    formatted_row.append('-')
                else:
                    formatted_row.append(str(cell))
            formatted_rows.append(formatted_row)

        return jsonify({
            'success': True,
            'query_id': query_id,
            'title': query_item['title'],
            'columns': columns,
            'rows': formatted_rows,
            'row_count': len(formatted_rows),
            'execution_time_ms': duration_ms
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@query_lab_bp.route('/custom', methods=['POST'])
@login_required
@role_required('Admin')
def execute_custom():
    """Restricted SQL Console for Administrators with safety guardrails."""
    sql = request.form.get('sql', '').strip()
    if not sql:
        return jsonify({'success': False, 'error': 'No SQL statement provided.'}), 400

    # Safety checks: Prevent dangerous destruction
    disallowed_keywords = ['drop database', 'truncate', 'grant', 'revoke', 'flush']
    sql_lower = sql.lower()
    for kw in disallowed_keywords:
        if kw in sql_lower:
            return jsonify({'success': False, 'error': f'Execution denied: "{kw.upper()}" is restricted in interactive console.'}), 403

    t0 = time.time()
    try:
        result_proxy = db.session.execute(text(sql))
        if result_proxy.returns_rows:
            columns = list(result_proxy.keys())
            raw_rows = result_proxy.fetchmany(100) # Cap at 100 rows for security & performance
            duration_ms = round((time.time() - t0) * 1000, 2)

            formatted_rows = []
            for r in raw_rows:
                formatted_rows.append([str(c) if c is not None else '-' for c in r])

            return jsonify({
                'success': True,
                'columns': columns,
                'rows': formatted_rows,
                'row_count': len(formatted_rows),
                'execution_time_ms': duration_ms
            })
        else:
            db.session.commit()
            duration_ms = round((time.time() - t0) * 1000, 2)
            return jsonify({
                'success': True,
                'columns': ['Result'],
                'rows': [['Command executed successfully (no result set returned)']],
                'row_count': 0,
                'execution_time_ms': duration_ms
            })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
