-- ============================================================================
-- SAMPLE SQL QUERIES DEMONSTRATING ADVANCED DBMS CONCEPTS
-- Used in the SQL Query Lab and Academic Demonstration
-- ============================================================================

USE `business_sales_intelligence`;

-- ----------------------------------------------------------------------------
-- Query 1: Basic Retrieval with Filtering, Sorting, and Formatting
-- Concept: SELECT, WHERE, ORDER BY, LIMIT
-- ----------------------------------------------------------------------------
SELECT 
    p.product_id,
    p.product_name,
    p.SKU,
    c.category_name,
    p.unit_price,
    p.unit_cost,
    p.stock_quantity,
    p.product_status
FROM `products` p
JOIN `categories` c ON p.category_id = c.category_id
WHERE p.product_status = 'Active'
ORDER BY p.unit_price DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- Query 2: Category-wise Revenue, Volume, and Gross Margin
-- Concept: INNER JOIN, GROUP BY, Aggregates (SUM, COUNT), Arithmetic
-- ----------------------------------------------------------------------------
SELECT 
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
FROM `categories` c
JOIN `products` p ON c.category_id = p.category_id
JOIN `order_items` oi ON p.product_id = oi.product_id
JOIN `orders` o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed' AND o.payment_status = 'Paid'
GROUP BY c.category_id, c.category_name
ORDER BY gross_revenue DESC;

-- ----------------------------------------------------------------------------
-- Query 3: Top 10 High-Revenue Generating Products
-- Concept: INNER JOIN, Aggregation, GROUP BY, ORDER BY, LIMIT
-- ----------------------------------------------------------------------------
SELECT 
    p.product_id,
    p.product_name,
    p.SKU,
    c.category_name,
    SUM(oi.quantity) AS units_sold,
    CAST(SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS DECIMAL(12,2)) AS recognized_revenue,
    CAST(SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount - (oi.quantity * oi.unit_cost_at_sale)) AS DECIMAL(12,2)) AS total_profit
FROM `products` p
JOIN `categories` c ON p.category_id = c.category_id
JOIN `order_items` oi ON p.product_id = oi.product_id
JOIN `orders` o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed' AND o.payment_status = 'Paid'
GROUP BY p.product_id, p.product_name, p.SKU, c.category_name
ORDER BY recognized_revenue DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- Query 4: Monthly Sales Trend with Year-over-Year Aggregates
-- Concept: Date formatting, GROUP BY, Aggregate functions
-- ----------------------------------------------------------------------------
SELECT 
    DATE_FORMAT(o.order_date, '%Y-%m') AS sales_month,
    COUNT(DISTINCT o.order_id) AS orders_count,
    SUM(oi.quantity) AS units_sold,
    CAST(SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS DECIMAL(12,2)) AS monthly_revenue,
    CAST(AVG((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS DECIMAL(10,2)) AS avg_line_revenue
FROM `orders` o
JOIN `order_items` oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed' AND o.payment_status = 'Paid'
GROUP BY DATE_FORMAT(o.order_date, '%Y-%m')
ORDER BY sales_month ASC;

-- ----------------------------------------------------------------------------
-- Query 5: Customer RFM Indicators (Recency, Frequency, Monetary Value)
-- Concept: DATEDIFF, MAX, COUNT DISTINCT, GROUP BY, HAVING
-- ----------------------------------------------------------------------------
SELECT 
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    c.city,
    COUNT(DISTINCT o.order_id) AS order_frequency,
    MAX(o.order_date) AS last_order_date,
    CAST(SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS DECIMAL(12,2)) AS total_monetary_spent
FROM `customers` c
JOIN `orders` o ON c.customer_id = o.customer_id
JOIN `order_items` oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed' AND o.payment_status = 'Paid'
GROUP BY c.customer_id, c.customer_name, c.customer_segment, c.city
HAVING total_monetary_spent > 1000
ORDER BY total_monetary_spent DESC;

-- ----------------------------------------------------------------------------
-- Query 6: Average Order Value (AOV) by Customer Segment
-- Concept: Multi-level subquery, GROUP BY, AVG calculation
-- ----------------------------------------------------------------------------
SELECT 
    c.customer_segment,
    COUNT(DISTINCT order_sub.order_id) AS total_orders,
    CAST(SUM(order_sub.order_net_total) AS DECIMAL(12,2)) AS segment_revenue,
    CAST(AVG(order_sub.order_net_total) AS DECIMAL(10,2)) AS avg_order_value
FROM `customers` c
JOIN (
    SELECT 
        o.order_id,
        o.customer_id,
        SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS order_net_total
    FROM `orders` o
    JOIN `order_items` oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed' AND o.payment_status = 'Paid'
    GROUP BY o.order_id, o.customer_id
) AS order_sub ON c.customer_id = order_sub.customer_id
GROUP BY c.customer_segment
ORDER BY segment_revenue DESC;

-- ----------------------------------------------------------------------------
-- Query 7: Sales Target Achievement Analysis (Target vs Actual)
-- Concept: LEFT JOIN with Aggregated Subquery, COALESCE, Percentage Calculation
-- ----------------------------------------------------------------------------
SELECT 
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
FROM `sales_targets` st
LEFT JOIN `categories` c ON st.category_id = c.category_id
LEFT JOIN (
    SELECT 
        DATE_FORMAT(o.order_date, '%Y-%m') AS period,
        p.category_id,
        SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS actual_revenue
    FROM `orders` o
    JOIN `order_items` oi ON o.order_id = oi.order_id
    JOIN `products` p ON oi.product_id = p.product_id
    WHERE o.order_status = 'Completed' AND o.payment_status = 'Paid'
    GROUP BY DATE_FORMAT(o.order_date, '%Y-%m'), p.category_id
) AS act ON st.target_period = act.period AND (st.category_id = act.category_id OR st.category_id IS NULL)
ORDER BY st.target_period DESC;

-- ----------------------------------------------------------------------------
-- Query 8: Inventory Stock Valuation and Reorder Alert Classification
-- Concept: CASE conditional expression, Mathematical formula, WHERE
-- ----------------------------------------------------------------------------
SELECT 
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
FROM `products` p
JOIN `categories` c ON p.category_id = c.category_id
ORDER BY p.stock_quantity ASC;

-- ----------------------------------------------------------------------------
-- Query 9: Order Status and Payment Health Distribution
-- Concept: Conditional Aggregation (CASE inside SUM), COUNT
-- ----------------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_order_count,
    SUM(CASE WHEN order_status = 'Completed' AND payment_status = 'Paid' THEN 1 ELSE 0 END) AS completed_orders,
    SUM(CASE WHEN order_status = 'Pending' THEN 1 ELSE 0 END) AS pending_orders,
    SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
    SUM(CASE WHEN order_status = 'Returned' OR payment_status = 'Refunded' THEN 1 ELSE 0 END) AS returned_orders
FROM `orders`;

-- ----------------------------------------------------------------------------
-- Query 10: Products with Zero Sales in Last 90 Days (Slow-Moving Audit)
-- Concept: NOT IN / NOT EXISTS Subquery, LEFT JOIN with NULL check
-- ----------------------------------------------------------------------------
SELECT 
    p.product_id,
    p.product_name,
    c.category_name,
    p.stock_quantity,
    p.unit_price
FROM `products` p
JOIN `categories` c ON p.category_id = c.category_id
WHERE p.product_id NOT IN (
    SELECT DISTINCT oi.product_id
    FROM `order_items` oi
    JOIN `orders` o ON oi.order_id = o.order_id
    WHERE o.order_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
      AND o.order_status = 'Completed'
)
ORDER BY p.stock_quantity DESC;

-- ----------------------------------------------------------------------------
-- Query 11: Window Function: Product Revenue Ranking within Each Category
-- Concept: DENSE_RANK() OVER (PARTITION BY ... ORDER BY ...)
-- ----------------------------------------------------------------------------
WITH category_product_sales AS (
    SELECT 
        c.category_name,
        p.product_name,
        CAST(SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS DECIMAL(12,2)) AS total_sales
    FROM `products` p
    JOIN `categories` c ON p.category_id = c.category_id
    JOIN `order_items` oi ON p.product_id = oi.product_id
    JOIN `orders` o ON oi.order_id = o.order_id
    WHERE o.order_status = 'Completed' AND o.payment_status = 'Paid'
    GROUP BY c.category_name, p.product_name
)
SELECT 
    category_name,
    product_name,
    total_sales,
    DENSE_RANK() OVER (PARTITION BY category_name ORDER BY total_sales DESC) as category_rank
FROM category_product_sales
ORDER BY category_name, category_rank;

-- ----------------------------------------------------------------------------
-- Query 12: High-Value Orders (Above Overall Average Order Value)
-- Concept: Correlated Subquery with Scalar Subquery Comparison
-- ----------------------------------------------------------------------------
SELECT 
    o.order_id,
    o.order_date,
    c.customer_name,
    c.city,
    CAST(SUM((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS DECIMAL(10,2)) AS order_total
FROM `orders` o
JOIN `customers` c ON o.customer_id = c.customer_id
JOIN `order_items` oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed' AND o.payment_status = 'Paid'
GROUP BY o.order_id, o.order_date, c.customer_name, c.city
HAVING order_total > (
    -- Scalar subquery calculating benchmark average order total
    SELECT AVG(item_sum.total_amount)
    FROM (
        SELECT SUM((sub_oi.quantity * sub_oi.unit_price_at_sale) - sub_oi.discount_amount) AS total_amount
        FROM `orders` sub_o
        JOIN `order_items` sub_oi ON sub_o.order_id = sub_oi.order_id
        WHERE sub_o.order_status = 'Completed' AND sub_o.payment_status = 'Paid'
        GROUP BY sub_o.order_id
    ) AS item_sum
)
ORDER BY order_total DESC
LIMIT 15;
