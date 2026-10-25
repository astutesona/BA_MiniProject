# Entity-Relationship (ER) Diagram

The following Mermaid diagram visualizes the relational schema of the **Business Sales Intelligence and Revenue Analytics System** (`business_sales_intelligence`), illustrating entity relationships, foreign key constraints, and cardinalities.

```mermaid
erDiagram
    USERS ||--o{ ORDERS : "creates / processes"
    USERS ||--o{ SALES_TARGETS : "configures"
    CUSTOMERS ||--o{ ORDERS : "places"
    CATEGORIES ||--o{ PRODUCTS : "classifies"
    CATEGORIES ||--o{ SALES_TARGETS : "scopes"
    ORDERS ||--|{ ORDER_ITEMS : "contains"
    PRODUCTS ||--o{ ORDER_ITEMS : "included_in"

    USERS {
        int user_id PK
        string full_name
        string username UK
        string email UK
        string password_hash
        string role
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    CUSTOMERS {
        int customer_id PK
        string customer_name
        string email
        string phone
        string city
        string state
        string customer_segment
        date registration_date
        datetime created_at
        datetime updated_at
    }

    CATEGORIES {
        int category_id PK
        string category_name UK
        text description
        datetime created_at
    }

    PRODUCTS {
        int product_id PK
        string product_name
        int category_id FK
        string SKU UK
        decimal unit_price
        decimal unit_cost
        int stock_quantity
        int reorder_level
        string product_status
        datetime created_at
        datetime updated_at
    }

    ORDERS {
        int order_id PK
        int customer_id FK
        datetime order_date
        string order_status
        string payment_status
        string payment_method
        int created_by FK
        datetime created_at
        datetime updated_at
    }

    ORDER_ITEMS {
        int order_item_id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal unit_price_at_sale
        decimal unit_cost_at_sale
        decimal discount_amount
        datetime created_at
    }

    SALES_TARGETS {
        int target_id PK
        string target_period
        string target_type
        int category_id FK
        decimal target_amount
        int created_by FK
        datetime created_at
    }
```

---

## Relationship Cardinality & Integrity Rules

1. **`CUSTOMERS` to `ORDERS` (1 : N)**
   - Cardinality: One customer can place zero or many orders. Each order must reference exactly one customer.
   - Referential Action: `ON DELETE RESTRICT` (Customers with historical transactions cannot be deleted, preserving transactional integrity).

2. **`CATEGORIES` to `PRODUCTS` (1 : N)**
   - Cardinality: One category contains zero or many products. Each product belongs to exactly one category.
   - Referential Action: `ON DELETE RESTRICT` (Categories cannot be deleted if products are assigned).

3. **`ORDERS` to `ORDER_ITEMS` (1 : N)**
   - Cardinality: One order contains one or many line items. Each line item belongs strictly to one parent order.
   - Referential Action: `ON DELETE CASCADE` (Deleting an uncommitted or draft order safely cascades to its constituent line items).

4. **`PRODUCTS` to `ORDER_ITEMS` (1 : N)**
   - Cardinality: One product can appear in multiple line items across different historical orders.
   - Referential Action: `ON DELETE RESTRICT` (A product cannot be deleted if historical sales records reference its SKU).

5. **`USERS` to `ORDERS` (1 : N)**
   - Cardinality: A sales employee or admin user creates/processes zero or many orders.
   - Referential Action: `ON DELETE SET NULL` (If a user account is deleted or pruned, historical orders preserve their audit trail with `created_by` set to NULL).

6. **`CATEGORIES` to `SALES_TARGETS` (1 : N)**
   - Cardinality: A target may be scoped to a specific category or represent overall monthly performance (`category_id IS NULL`).
   - Referential Action: `ON DELETE SET NULL`.
