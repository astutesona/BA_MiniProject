# Business Sales Intelligence and Revenue Analytics System Using DBMS

A complete, database-driven business intelligence and sales analytics web application engineered in Python (Flask) with a MySQL 8.x (InnoDB) database. Developed for an MCA academic capstone demonstration.

---

## 1. Project Title
**Business Sales Intelligence and Revenue Analytics System Using DBMS (BSI-RAS)**

---

## 2. Abstract
The Business Sales Intelligence and Revenue Analytics System (BSI-RAS) is a full-stack, normalized relational database platform designed to record sales transactions, maintain inventory levels, analyze revenue and gross margin trends, monitor customer purchasing behaviors, and generate evidence-based business insights. The platform showcases Database Management System (DBMS) concepts, including Third Normal Form (3NF) relational design, ACID-compliant transactions, advanced SQL aggregations, window functions, Data Control Language (DCL) least-privilege security, and interactive visualizations using Chart.js.

---

## 3. Problem Statement
Many small-to-medium businesses experience operational bottlenecks due to disparate spreadsheets or unnormalized data stores:
- **Update Anomalies:** Redundant customer and category records create data inconsistency.
- **Distorted Historical Reporting:** Changing product prices in naive schemas retroactively alters historical sales reports.
- **Inaccurate Revenue Recognition:** Cancelled, failed, or refunded orders are improperly lumped into gross revenue totals.
- **Lack of Role-Based Security:** Absence of granular access control exposes database structures and administrative functions to general users.

---

## 4. Project Objectives
- Architect a normalized (3NF) relational schema in MySQL 8.x InnoDB.
- Preserve point-in-time pricing and cost snapshots on order line items.
- Implement atomic transaction management with rollback on inventory stockouts.
- Deliver an executive dashboard with 8 real-time calculated KPIs and 8 interactive visualizations.
- Provide a dedicated SQL Query Lab featuring 12 parameterized analytical queries with execution timing.
- Enforce server-side Role-Based Access Control (RBAC) across Admin, Manager, and Sales Employee roles.
- Implement defense-in-depth security against SQL injection, CSRF, and CSV formula injection.

---

## 5. Scope of the Project
The application models end-to-end sales transactions for commercial hardware, consumer electronics, office equipment, networking gear, storage arrays, and enterprise software licenses. It encompasses catalog administration, customer profiling, order processing, stock replenishment, monthly target benchmarks, tabular reporting, and SQL query demonstration.

---

## 6. Features
- **Executive BI Dashboard:** 8 core KPI cards, 8 interactive charts, real-time date/category/segment filters.
- **Dynamic Business Insights:** Automatically synthesized narrative observations driven by SQL aggregations.
- **Sales Order Processing:** Multi-item dynamic order entry, real-time discount calculation, stock decrement, and point-in-time price snapshotting.
- **Customer Relationship Management (CRM):** Customer profiling, segmentation (Enterprise, SMB, Retail, Wholesale), order history tracking.
- **Catalog & Inventory Analytics:** Stock valuation, safety reorder alerts, SKU velocity analysis (fast-moving vs. slow-moving).
- **Sales Targets & Benchmarks:** Target configuration and attainment tracking by month and category.
- **Report Generation & CSV Exports:** 7 tabular reports with date range filtering and formula injection mitigation.
- **SQL Query Lab:** 12 predefined analytical queries with concept explanations and an Admin-only interactive SQL console.
- **User Management & RBAC:** User administration with role assignment (Admin, Manager, Sales Employee).

---

## 7. Technology Stack
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Chart.js 4.4, Font Awesome 6.5
- **Backend:** Python 3.12, Flask 3.1, Flask-SQLAlchemy 3.1, Flask-Login 0.6, Flask-WTF 1.3 / WTForms, Pandas
- **Database:** MySQL 8.0 (InnoDB engine, UTF-8 collation, DECIMAL monetary precision)
- **Database Driver:** PyMySQL 1.2
- **Testing:** pytest 9.1, Flask Test Client

---

## 8. System Architecture
```
[ Frontend: HTML5 / CSS3 / JavaScript / Bootstrap 5 / Chart.js ]
                        |  (REST / JSON API / Form POST with CSRF)
[ Application Layer: Python 3.12 / Flask Application Factory / Blueprints ]
    ├── Authentication & Authorization (Flask-Login, RBAC Decorators)
    ├── Business Intelligence Engine (AnalyticsService, InventoryService)
    └── Security & Export Subsystem (Flask-WTF CSRF, CSV Formula Sanitizer)
                        |  (SQLAlchemy ORM & Raw Parameterized SQL)
[ Database Engine: MySQL 8.x InnoDB ]
    ├── Tables: users, customers, categories, products, orders, order_items, sales_targets
    ├── Analytical View: vw_completed_sales_items
    └── DCL Accounts: bi_app_user, bi_report_user
```

---

## 9. Database Design & Normalization
The database `business_sales_intelligence` satisfies Third Normal Form (3NF):
- **1NF:** Atomic attributes, surrogate primary keys on all tables, no repeating columns.
- **2NF:** All non-key attributes are fully functionally dependent on the complete primary key.
- **3NF:** Transitive dependencies are removed; categories and customers are normalized into independent dimension tables. Line revenues and profits are calculated via SQL rather than stored redundantly.

---

## 10. Entity-Relationship (ER) Diagram
```mermaid
erDiagram
    USERS ||--o{ ORDERS : "creates"
    USERS ||--o{ SALES_TARGETS : "configures"
    CUSTOMERS ||--o{ ORDERS : "places"
    CATEGORIES ||--o{ PRODUCTS : "classifies"
    CATEGORIES ||--o{ SALES_TARGETS : "scopes"
    ORDERS ||--|{ ORDER_ITEMS : "contains"
    PRODUCTS ||--o{ ORDER_ITEMS : "included_in"

    USERS {
        int user_id PK
        string username UK
        string email UK
        string role
    }
    CUSTOMERS {
        int customer_id PK
        string customer_name
        string customer_segment
        string city
    }
    CATEGORIES {
        int category_id PK
        string category_name UK
    }
    PRODUCTS {
        int product_id PK
        string SKU UK
        decimal unit_price
        decimal unit_cost
        int stock_quantity
    }
    ORDERS {
        int order_id PK
        datetime order_date
        string order_status
        string payment_status
    }
    ORDER_ITEMS {
        int order_item_id PK
        int quantity
        decimal unit_price_at_sale
        decimal discount_amount
    }
    SALES_TARGETS {
        int target_id PK
        string target_period
        decimal target_amount
    }
```

---

## 11. Table Descriptions
1. `users`: Stores user credentials (hashed), roles (Admin, Sales Employee, Manager), and account status.
2. `customers`: Stores client profiles, contact information, and business segments.
3. `categories`: Defines product taxonomy and category descriptions.
4. `products`: Catalogs SKUs, unit prices, unit costs, stock quantities, and reorder levels.
5. `orders`: Records sales header data, order dates, fulfillment status, and payment method.
6. `order_items`: Records product line items with point-in-time price and cost snapshots.
7. `sales_targets`: Stores monthly and category benchmark quotas.
8. `vw_completed_sales_items`: Analytical view filtering recognized sales (`Completed` and `Paid`).

---

## 12. DDL, DML, DCL, and Advanced SQL Queries

### Data Definition Language (DDL)
Found in `database/schema.sql` and `database/ddl_alter_demo.sql`:
```sql
CREATE DATABASE IF NOT EXISTS `business_sales_intelligence`;
ALTER TABLE `order_audit_log` ADD COLUMN `remarks` VARCHAR(255) NULL;
CREATE INDEX `idx_orders_date` ON `orders` (`order_date`);
```

### Data Manipulation Language (DML)
```sql
-- Transactional order insertion
INSERT INTO `orders` (customer_id, order_date, order_status, payment_status, payment_method)
VALUES (1, NOW(), 'Completed', 'Paid', 'Credit Card');
```

### Data Control Language (DCL)
Found in `database/permissions.sql`:
```sql
CREATE USER IF NOT EXISTS 'bi_report_user'@'localhost' IDENTIFIED BY 'ReportUser2026!';
GRANT SELECT ON `business_sales_intelligence`.`vw_completed_sales_items` TO 'bi_report_user'@'localhost';
REVOKE ALL PRIVILEGES ON *.* FROM 'bi_report_user'@'localhost';
```

### Advanced SQL Query Example (Window Function from SQL Query Lab)
```sql
WITH category_product_sales AS (
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
ORDER BY category_name, category_rank;
```

---

## 13. Business Analytics Methodology
- **Recognized Revenue:** Sum of net line revenue for orders with `order_status = 'Completed'` AND `payment_status = 'Paid'`. Cancelled, pending, and refunded orders are excluded.
- **Gross Profit:** Recognized Net Revenue minus Cost of Goods Sold (COGS).
- **Average Order Value (AOV):** Total Recognized Revenue divided by the count of recognized orders.
- **Sales Target Achievement:** $\frac{\text{Actual Revenue}}{\text{Target Quota}} \times 100$.
- **Revenue Growth Rate:** Percentage change between current period revenue and the previous comparable period.

---

## 14. Application Layout Guide
- **Sidebar:** Dark graphite navigation (`#171a21`) with role indicator.
- **Main Viewport:** Off-white background (`#f4f5f7`) with warm slate accents (`#1f3a52`) and amber/emerald highlights.
- **KPI Cards:** Tabular numeric presentation with change badges.
- **Charts Grid:** 8 Chart.js visual components with currency-formatted tooltips.

---

## 15. Installation Instructions

### Prerequisites
- Python 3.10+ (Tested on Python 3.12)
- MySQL 8.x Server running locally or remotely
- Git

### Clone & Virtual Environment Setup
```powershell
# Navigate to project directory
cd c:\Users\astut\Desktop\BA_MiniProject

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt
```

---

## 16. MySQL Configuration
Ensure your MySQL server is running on port 3306. You can create the database using the script or let the seeding tool initialize it automatically.

---

## 17. Environment Variable Configuration
Copy `.env.example` to `.env` and verify database credentials:
```ini
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=bi-sales-intel-secret-key-2026-prod-mca-project-secure-salt

# Database Credentials
DB_HOST=localhost
DB_PORT=3306
DB_NAME=business_sales_intelligence
DB_USER=root
DB_PASSWORD=12345678
DATABASE_URL=mysql+pymysql://root:12345678@localhost:3306/business_sales_intelligence
```

---

## 18. Database Initialization Instructions
To create the database and all normalized tables:
```powershell
.\venv\Scripts\python.exe database\seed_data.py --drop
```

---

## 19. Sample Data Generation
The seeding script generates:
- 4 Users across 3 roles
- 6 Categories
- 25 Products with realistic prices, costs, and stock levels
- 64 Customer accounts across 12 cities
- 240 Orders spanning 14 months with 629 line items
- 92 Monthly and category sales targets

---

## 20. Application Startup Instructions
```powershell
.\venv\Scripts\python.exe run.py
```
Open your browser and navigate to:
**http://localhost:5000**

---

## 21. Demo Accounts Setup
| Role | Username | Password | Access Privileges |
|---|---|---|---|
| **Administrator** | `admin` | `Admin@123` | Full system control, catalog editing, user management, SQL console |
| **Business Manager** | `manager` | `Manager@123` | BI dashboards, targets configuration, reports, read-only SQL lab |
| **Sales Employee** | `sales1` | `Sales@123` | Customer management, order creation, transaction processing |

*Convenience feature:* The login screen includes quick-fill buttons for instant demo login.

---

## 22. Testing Instructions
Run the automated test suite with pytest:
```powershell
.\venv\Scripts\pytest.exe -v
```
To run the live MySQL integration check:
```powershell
.\venv\Scripts\python.exe tests\verify_mysql_live.py
```

---

## 23. Security Measures
1. **Password Hashing:** Salted hashes via `generate_password_hash` (no plaintext passwords).
2. **CSRF Protection:** Form tokens enforced across all POST/PUT/DELETE requests.
3. **SQL Injection Defense:** All queries use SQLAlchemy ORM or parameterized `text()` binds.
4. **CSV Formula Injection Mitigation:** Spreadsheet formula prefixes (`=`, `+`, `-`, `@`) are sanitized on export.
5. **Role-Based Authorization:** Server-side route protection via `@role_required` decorators.

---

## 24. Limitations
- Single-currency model (USD `$`). Multi-currency conversion is not implemented.
- Partial line returns are not modeled; returns operate at the order level.

---

## 25. Future Enhancements
- Integration of predictive forecasting models (ARIMA / Holt-Winters) for future revenue forecasting.
- Automated email alerts when items breach reorder thresholds.
- Direct PDF report export alongside CSV.

---

## 26. Conclusion
The Business Sales Intelligence and Revenue Analytics System successfully bridges theoretical DBMS principles with enterprise business intelligence. It provides an effective demonstration of normalized data architecture, transaction safety, and executive analytics.
