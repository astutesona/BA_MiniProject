# Database Architecture and Normalization Report

## 1. System Database Specification
- **Database Engine:** MySQL 8.x InnoDB
- **Storage Subsystem:** ACID-Compliant Transactional Storage Engine
- **Character Encoding:** `utf8mb4` with `utf8mb4_unicode_ci` Collation
- **Primary Monetary Convention:** Fixed-Point `DECIMAL(10, 2)` and `DECIMAL(12, 2)` to eliminate floating-point rounding errors

---

## 2. Normalization Analysis (1NF to 3NF)

The database schema `business_sales_intelligence` is engineered in strict accordance with **Third Normal Form (3NF)** principles to prevent insert, update, and deletion anomalies while maintaining query performance.

### First Normal Form (1NF)
- **Atomic Values:** Every column contains non-divisible, atomic values. For instance, customer full addresses are decomposed into distinct attributes (`city`, `state`), and line items are separated from sales headers.
- **Unique Primary Keys:** Every table is indexed on a unique, auto-incrementing integer surrogate primary key (`user_id`, `customer_id`, `category_id`, `product_id`, `order_id`, `order_item_id`, `target_id`).
- **No Repeating Groups:** Instead of storing multiple products as comma-separated values or array attributes within the `orders` table, line items are normalized into the separate relation `order_items`.

### Second Normal Form (2NF)
- **Full Functional Dependency:** The schema satisfies 1NF, and all non-key attributes are fully functionally dependent on the entire primary key.
- In `order_items`, the composite natural key `(order_id, product_id)` is augmented with a surrogate key `order_item_id`. Attributes such as `quantity`, `unit_price_at_sale`, `unit_cost_at_sale`, and `discount_amount` describe that specific order-item line only, and do not depend on subsets of composite keys.

### Third Normal Form (3NF)
- **Elimination of Transitive Dependencies:** Every non-prime attribute is non-transitively dependent on the primary key ($X \rightarrow Y$ where $Y$ is not dependent on another non-key attribute $Z$).
  - Product category descriptions are not duplicated across rows in the `products` table; instead, `category_id` references the `categories` dimension table.
  - Customer contact information (`phone`, `email`, `city`, `state`) is maintained strictly in `customers`. The `orders` table only retains `customer_id`.
  - Line-item calculations (such as `line_revenue` or `line_profit`) are derived dynamically via deterministic SQL formulas or analytical views (`vw_completed_sales_items`) rather than persisted as redundant update-prone columns.

---

## 3. Data Dictionary

### Table: `users`
| Column Name | Data Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `user_id` | INT AUTO_INCREMENT | No | Primary Key | Unique user account identifier |
| `full_name` | VARCHAR(100) | No | None | Employee or administrator full legal name |
| `username` | VARCHAR(50) | No | Unique, Index | Unique authentication handle |
| `email` | VARCHAR(100) | No | Unique | Unique corporate email address |
| `password_hash` | VARCHAR(255) | No | None | Argon2/PBKDF2 salted hash (no plaintext) |
| `role` | VARCHAR(50) | No | Index | 'Admin', 'Sales Employee', or 'Manager' |
| `is_active` | BOOLEAN | No | DEFAULT TRUE | Active account flag for authentication |
| `created_at` | DATETIME | No | DEFAULT CURRENT_TIMESTAMP | Audit timestamp of creation |
| `updated_at` | DATETIME | No | ON UPDATE CURRENT_TIMESTAMP | Audit timestamp of last update |

### Table: `customers`
| Column Name | Data Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `customer_id` | INT AUTO_INCREMENT | No | Primary Key | Unique customer identifier |
| `customer_name` | VARCHAR(100) | No | Index | Legal entity or individual client name |
| `email` | VARCHAR(100) | Yes | None | Procurement contact email |
| `phone` | VARCHAR(25) | Yes | None | Contact telephone number |
| `city` | VARCHAR(60) | No | Index | Operational city location |
| `state` | VARCHAR(60) | No | Index | State / province code |
| `customer_segment` | VARCHAR(40) | No | Index | 'Enterprise', 'SMB', 'Retail', 'Wholesale' |
| `registration_date` | DATE | No | None | Date account was onboarded |
| `created_at` | DATETIME | No | DEFAULT CURRENT_TIMESTAMP | Record creation audit timestamp |
| `updated_at` | DATETIME | No | ON UPDATE CURRENT_TIMESTAMP | Record update audit timestamp |

### Table: `categories`
| Column Name | Data Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `category_id` | INT AUTO_INCREMENT | No | Primary Key | Unique product category identifier |
| `category_name` | VARCHAR(60) | No | Unique | Category designation name |
| `description` | TEXT | Yes | None | Scope and taxonomy narrative |
| `created_at` | DATETIME | No | DEFAULT CURRENT_TIMESTAMP | Record creation audit timestamp |

### Table: `products`
| Column Name | Data Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `product_id` | INT AUTO_INCREMENT | No | Primary Key | Unique catalog product identifier |
| `product_name` | VARCHAR(120) | No | Index | Product commercial trade name |
| `category_id` | INT | No | Foreign Key, Index | References `categories(category_id)` RESTRICT |
| `SKU` | VARCHAR(50) | No | Unique, Index | Stock Keeping Unit code |
| `unit_price` | DECIMAL(10, 2) | No | CHECK (`unit_price` >= 0) | Standard catalog retail selling price |
| `unit_cost` | DECIMAL(10, 2) | No | CHECK (`unit_cost` >= 0) | Standard wholesale procurement unit cost |
| `stock_quantity` | INT | No | CHECK (`stock_quantity` >= 0) | Real-time physical inventory count |
| `reorder_level` | INT | No | CHECK (`reorder_level` >= 0) | Minimum stock safety threshold |
| `product_status` | VARCHAR(30) | No | Index | 'Active', 'Discontinued', 'Out of Stock' |
| `created_at` | DATETIME | No | DEFAULT CURRENT_TIMESTAMP | Record creation audit timestamp |
| `updated_at` | DATETIME | No | ON UPDATE CURRENT_TIMESTAMP | Record update audit timestamp |

### Table: `orders`
| Column Name | Data Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `order_id` | INT AUTO_INCREMENT | No | Primary Key | Unique sales order identifier |
| `customer_id` | INT | No | Foreign Key, Index | References `customers(customer_id)` RESTRICT |
| `order_date` | DATETIME | No | Index | Transaction timestamp |
| `order_status` | VARCHAR(30) | No | Index | 'Completed', 'Pending', 'Processing', 'Cancelled', 'Returned' |
| `payment_status` | VARCHAR(30) | No | Index | 'Paid', 'Pending', 'Failed', 'Refunded' |
| `payment_method` | VARCHAR(40) | No | None | 'Credit Card', 'Bank Transfer', 'UPI/Net Banking', 'Cash on Delivery' |
| `created_by` | INT | Yes | Foreign Key | References `users(user_id)` ON DELETE SET NULL |
| `created_at` | DATETIME | No | DEFAULT CURRENT_TIMESTAMP | Order creation audit timestamp |
| `updated_at` | DATETIME | No | ON UPDATE CURRENT_TIMESTAMP | Order update audit timestamp |

### Table: `order_items`
| Column Name | Data Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `order_item_id` | INT AUTO_INCREMENT | No | Primary Key | Unique line-item identifier |
| `order_id` | INT | No | Foreign Key, Index | References `orders(order_id)` ON DELETE CASCADE |
| `product_id` | INT | No | Foreign Key, Index | References `products(product_id)` RESTRICT |
| `quantity` | INT | No | CHECK (`quantity` > 0) | Units purchased |
| `unit_price_at_sale` | DECIMAL(10, 2) | No | CHECK (`unit_price_at_sale` >= 0) | Point-in-time captured selling price |
| `unit_cost_at_sale` | DECIMAL(10, 2) | No | CHECK (`unit_cost_at_sale` >= 0) | Point-in-time captured procurement cost |
| `discount_amount` | DECIMAL(10, 2) | No | CHECK (`discount_amount` >= 0) | Total discount applied to this line item |
| `created_at` | DATETIME | No | DEFAULT CURRENT_TIMESTAMP | Line creation audit timestamp |

### Table: `sales_targets`
| Column Name | Data Type | Nullable | Key / Constraint | Description |
|---|---|---|---|---|
| `target_id` | INT AUTO_INCREMENT | No | Primary Key | Unique benchmark target identifier |
| `target_period` | VARCHAR(7) | No | Index | Target period in 'YYYY-MM' format |
| `target_type` | VARCHAR(40) | No | None | 'Monthly Revenue' or 'Category Revenue' |
| `category_id` | INT | Yes | Foreign Key, Index | References `categories(category_id)` ON DELETE SET NULL |
| `target_amount` | DECIMAL(12, 2) | No | CHECK (`target_amount` > 0) | Targeted monetary revenue quota |
| `created_by` | INT | Yes | Foreign Key | References `users(user_id)` ON DELETE SET NULL |
| `created_at` | DATETIME | No | DEFAULT CURRENT_TIMESTAMP | Target creation timestamp |

---

## 4. Indexing Strategy & Query Optimization

| Table | Index Name | Columns | Intended Optimization Benefit |
|---|---|---|---|
| `orders` | `idx_orders_date` | `order_date` | Accelerates chronological time-series aggregations and date-range range scans |
| `orders` | `idx_orders_status_pay` | `order_status`, `payment_status` | Speeds up filtering for recognized revenue (`Completed` AND `Paid`) |
| `orders` | `idx_orders_customer` | `customer_id` | Optimizes customer order history lookups and joins |
| `order_items` | `idx_order_items_order` | `order_id` | Essential for order header-to-detail JOINs |
| `order_items` | `idx_order_items_product` | `product_id` | Speeds up product sales volume and profitability rollups |
| `products` | `idx_products_category` | `category_id` | Enables fast category-wise catalog filtering |
| `products` | `idx_products_status` | `product_status` | Speeds up active catalog filtering and inventory audits |
| `customers` | `idx_customers_segment` | `customer_segment` | Optimizes RFM customer segmentation and segment-level AOV rollups |
| `sales_targets` | `uq_period_type_category` | `target_period`, `target_type`, `category_id` | Enforces uniqueness so duplicate quotas cannot be entered for the same period |
