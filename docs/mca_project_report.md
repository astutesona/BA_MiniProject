# MCA Academic Project Report: Business Sales Intelligence & Revenue Analytics System Using DBMS

**Degree:** Master of Computer Applications (MCA)  
**Domain:** Database Management Systems (DBMS) & Business Intelligence (BI)  
**System Title:** Business Sales Intelligence and Revenue Analytics System (BSI-RAS)

---

## Abstract
Modern enterprises generate voluminous transactional sales data requiring systematic normalization, rigorous referential integrity, and performant analytics to guide tactical and strategic decision-making. The **Business Sales Intelligence and Revenue Analytics System (BSI-RAS)** is a full-stack, database-driven business intelligence web platform engineered using **MySQL 8.x (InnoDB)** and **Python / Flask**. 

The application implements a 3rd Normal Form (3NF) relational architecture spanning catalog management, customer relationship data, point-of-sale snapshots, and sales targets. Advanced DBMS concepts—including Data Definition Language (DDL), Data Manipulation Language (DML), Data Control Language (DCL), multi-table joins, derived subqueries, Common Table Expressions (CTEs), and SQL window functions—are demonstrated through an interactive SQL Query Lab and automated business analytics dashboards.

---

## 1. Problem Statement & Objectives
Small and medium-sized enterprises frequently face critical challenges:
1. **Unnormalized Data Stores:** Inconsistent data modeling leading to update anomalies and data corruption.
2. **Distorted Historical Reporting:** Failure to snapshot historical unit prices and costs at the time of sale, distorting financial analytics when product prices change.
3. **Flawed Revenue Accounting:** Failure to properly distinguish between gross orders and recognized sales (excluding cancelled or refunded transactions).
4. **Lack of Granular Access Control:** Exposure of sensitive database functions without strict role separation.

### Project Objectives:
- Model a normalized (3NF) relational database schema in MySQL InnoDB.
- Implement transactional ACID compliance during order processing with stock decrements.
- Engineer an executive dashboard with 8 real-time calculated business intelligence KPIs and 8 interactive visualizations.
- Provide an SQL Query Lab executing 12 parameterized analytical queries with execution timing.
- Enforce Role-Based Access Control (RBAC) across Administrator, Business Manager, and Sales Employee tiers.
- Mitigate security vulnerabilities including SQL injection, CSRF, and CSV formula injection.

---

## 2. System Architecture & Tech Stack

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

## 3. Business Analytics & Financial Methodology

### 3.1 Recognized Sales Revenue
Recognized sales revenue represents actual earned revenue, calculated strictly from eligible completed transactions:
$$\text{Recognized Revenue} = \sum_{\text{eligible items}} \Big( (\text{quantity} \times \text{unit\_price\_at\_sale}) - \text{discount\_amount} \Big)$$
*Eligibility Condition:* `order_status = 'Completed'` AND `payment_status = 'Paid'`.

### 3.2 Gross Profit & Cost of Goods Sold (COGS)
Gross profit models product-level profitability without falsely representing operating overhead or taxes as net profit:
$$\text{COGS} = \sum (\text{quantity} \times \text{unit\_cost\_at\_sale})$$
$$\text{Gross Profit} = \text{Recognized Net Revenue} - \text{COGS}$$
$$\text{Gross Profit Margin (\%)} = \left( \frac{\text{Gross Profit}}{\text{Recognized Revenue}} \right) \times 100$$

### 3.3 Average Order Value (AOV)
$$\text{AOV} = \frac{\text{Total Recognized Revenue}}{\text{Total Count of Eligible Orders}}$$

### 3.4 Target Achievement Ratio
$$\text{Achievement (\%)} = \left( \frac{\text{Actual Recognized Revenue}}{\text{Configured Sales Target}} \right) \times 100$$

---

## 4. Verification and Testing Results
A comprehensive test suite of 22 automated unit and integration tests was authored and executed using `pytest`:

| Test Suite | Scenario Verified | Outcome |
|---|---|---|
| `test_auth.py` | Session authentication, invalid password rejection, logout, unauthenticated redirect | **PASSED** (4/4) |
| `test_customers.py` | Customer creation, profile modification, referential integrity deletion blocking | **PASSED** (3/3) |
| `test_products.py` | Catalog creation, negative price rejection, inventory restock | **PASSED** (3/3) |
| `test_orders.py` | Multi-item order creation, negative quantity rejection, ACID rollback on stockout, historical price snapshot preservation | **PASSED** (4/4) |
| `test_analytics.py` | Revenue & profit formulas, cancelled order exclusion, target achievement calculation, category rollups | **PASSED** (3/3) |
| `test_permissions.py` | Role-based route restriction (RBAC), CSV formula injection sanitization | **PASSED** (5/5) |
| **Total** | **Full Suite Test Execution** | **22 / 22 PASSED (100%)** |

---

## 5. Conclusion
The **Business Sales Intelligence and Revenue Analytics System** successfully demonstrates the integration of relational database engineering and modern web technologies. By combining 3NF database normalization, ACID-compliant transaction safety, advanced SQL analytics, interactive visualizations, and strict access controls, the project fulfills all academic criteria for an advanced MCA capstone project.
