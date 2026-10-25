# DBMS Concepts Implementation Guide

This project serves as a comprehensive, production-grade practical demonstration of core Database Management System (DBMS) concepts for an MCA academic curriculum.

---

## 1. Data Definition Language (DDL)

DDL commands define, modify, and drop database structures and metadata.

### Operations Demonstrated:
1. **`CREATE DATABASE`:**
   ```sql
   CREATE DATABASE IF NOT EXISTS `business_sales_intelligence`
       CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
2. **`CREATE TABLE`:**
   Enforces primary keys, surrogate auto-increment identifiers, unique constraints, check constraints (`CHECK (quantity > 0)`), and foreign key referential actions (`RESTRICT`, `CASCADE`, `SET NULL`).
3. **`ALTER TABLE` (Demonstrated in `database/ddl_alter_demo.sql`):**
   - Adding columns: `ALTER TABLE order_audit_log ADD COLUMN remarks VARCHAR(255);`
   - Modifying data types: `ALTER TABLE order_audit_log MODIFY COLUMN remarks TEXT;`
   - Adding foreign key constraints: `ALTER TABLE order_audit_log ADD CONSTRAINT fk_audit_order FOREIGN KEY (order_id) REFERENCES orders(order_id);`
4. **`CREATE INDEX` / `DROP INDEX`:**
   B-Tree index construction on high-cardinality foreign keys (`order_id`, `product_id`) and search targets (`customer_name`, `order_date`).
5. **`CREATE VIEW`:**
   The analytical view `vw_completed_sales_items` encapsulates complex multi-table joins and revenue formulas, exposing a clean, secured virtual relation.

---

## 2. Data Manipulation Language (DML)

DML statements manage data records within the normalized tables.

### Operations Demonstrated:
- **`INSERT`:** Parameterized transactional record creation across orders and child items.
- **`UPDATE`:** Inventory restock adjustments, customer profile updates, and order status transitions.
- **`DELETE`:** Customer and product pruning protected by referential integrity constraints.
- **`SELECT`:** Complex queries with filtering, sorting, and aggregate projection.

---

## 3. Data Control Language (DCL) & Access Control

DCL commands manage privileges and account authorization within the database engine.

### Implementation in `database/permissions.sql`:
1. **Application Service Account (Read/Write):**
   ```sql
   CREATE USER IF NOT EXISTS 'bi_app_user'@'localhost' IDENTIFIED BY 'BiAppSecurePass2026!';
   GRANT SELECT, INSERT, UPDATE, DELETE ON `business_sales_intelligence`.* TO 'bi_app_user'@'localhost';
   ```
2. **Reporting / Business Manager Account (Strict Read-Only):**
   ```sql
   CREATE USER IF NOT EXISTS 'bi_report_user'@'localhost' IDENTIFIED BY 'ReportUser2026!';
   GRANT SELECT ON `business_sales_intelligence`.`vw_completed_sales_items` TO 'bi_report_user'@'localhost';
   GRANT SELECT ON `business_sales_intelligence`.`categories` TO 'bi_report_user'@'localhost';
   GRANT SELECT ON `business_sales_intelligence`.`products` TO 'bi_report_user'@'localhost';
   ```
3. **Revocation & Inspection:**
   ```sql
   REVOKE ALL PRIVILEGES ON *.* FROM 'bi_report_user'@'localhost';
   SHOW GRANTS FOR 'bi_report_user'@'localhost';
   ```

---

## 4. Advanced SQL Querying Concepts (SQL Query Lab)

The system features 12 predefined analytical queries implemented in the SQL Query Lab:

| Concept | Explanation | Example Project Query |
|---|---|---|
| **Multi-Table INNER JOIN** | Combines matching rows across related entities | Joining `orders`, `order_items`, `products`, and `categories` for gross sales rollups |
| **LEFT OUTER JOIN** | Preserves all dimension rows regardless of matching fact records | Joining `sales_targets` to subqueries calculating recognized revenue per target period |
| **Aggregate Functions** | `SUM()`, `AVG()`, `COUNT(DISTINCT)`, `MIN()`, `MAX()` | Computing total gross revenue, units sold, and average order values |
| **GROUP BY with HAVING** | Groups rows by categorical keys and filters aggregated sets | Filtering customers with `HAVING total_monetary_spent > 1000` |
| **Derived Subqueries** | Inline subqueries in the `FROM` clause acting as dynamic tables | Calculating segment-level AOV by aggregating order totals first |
| **Window Functions** | Evaluates ranking or cumulative metrics across partitioned windows | `DENSE_RANK() OVER (PARTITION BY category_name ORDER BY total_sales DESC)` |
| **Common Table Expressions (CTE)** | Modular, readable temporary result sets using `WITH` | Encapsulating category-product sales calculations before ranking |
| **Conditional Aggregation** | Pivoting and classification using `CASE WHEN` | Pivoting order counts by status inside `SUM(CASE WHEN ...)` |
| **Date Time Aggregations** | `DATE_FORMAT()`, `DATE_SUB()`, `CURDATE()` | Monthly sales trends and 90-day inventory velocity analysis |
| **Subquery Negation** | `NOT IN` / `NOT EXISTS` | Identifying slow-moving inventory with zero orders in the last 90 days |

---

## 5. ACID Transaction Management

Order creation requires atomic updates across multiple tables (`orders`, `order_items`, and inventory decrement in `products`).

```python
try:
    # 1. Create Order Header
    order = Order(...)
    db.session.add(order)
    db.session.flush()

    # 2. Iterate items & deduct inventory
    for item in items_data:
        product = Product.query.get(item['product_id'])
        if product.stock_quantity < item['quantity']:
            raise ValueError("Insufficient stock")
        product.stock_quantity -= item['quantity']
        db.session.add(OrderItem(order_id=order.order_id, ...))

    # 3. Commit entire transaction atomically
    db.session.commit()
except Exception:
    # Rollback entire state on failure
    db.session.rollback()
    raise
```

- **Atomicity:** All line items and stock adjustments commit together, or none take effect.
- **Consistency:** Foreign key constraints and non-negative check constraints (`stock_quantity >= 0`) are validated by InnoDB.
- **Isolation:** Handled via MySQL InnoDB default REPEATABLE READ isolation level.
- **Durability:** Committed transactions are persisted to the write-ahead transaction log (redo log).
