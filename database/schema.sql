-- ============================================================================
-- BUSINESS SALES INTELLIGENCE AND REVENUE ANALYTICS SYSTEM
-- Database Schema Definition (DDL)
-- Engine: MySQL 8.x InnoDB
-- Character Set: utf8mb4 / Collation: utf8mb4_unicode_ci
-- ============================================================================

-- Step 1: Create Database
CREATE DATABASE IF NOT EXISTS `business_sales_intelligence`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE `business_sales_intelligence`;

-- Disable Foreign Key Checks temporarily for clean setup
SET FOREIGN_KEY_CHECKS = 0;

-- Drop existing tables if re-initializing
DROP TABLE IF EXISTS `sales_targets`;
DROP TABLE IF EXISTS `order_items`;
DROP TABLE IF EXISTS `orders`;
DROP TABLE IF EXISTS `products`;
DROP TABLE IF EXISTS `categories`;
DROP TABLE IF EXISTS `customers`;
DROP TABLE IF EXISTS `users`;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- Table 1: users
-- Purpose: Authentication and Role-Based Authorization
-- ============================================================================
CREATE TABLE `users` (
    `user_id` INT AUTO_INCREMENT PRIMARY KEY,
    `full_name` VARCHAR(100) NOT NULL,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` VARCHAR(50) NOT NULL DEFAULT 'Sales Employee' 
        COMMENT 'Admin, Sales Employee, or Manager',
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_users_role` (`role`),
    INDEX `idx_users_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table 2: customers
-- Purpose: Customer Profiles and Demographics
-- ============================================================================
CREATE TABLE `customers` (
    `customer_id` INT AUTO_INCREMENT PRIMARY KEY,
    `customer_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NULL,
    `phone` VARCHAR(25) NULL,
    `city` VARCHAR(60) NOT NULL,
    `state` VARCHAR(60) NOT NULL,
    `customer_segment` VARCHAR(40) NOT NULL DEFAULT 'Retail' 
        COMMENT 'Retail, Enterprise, SMB, Wholesale',
    `registration_date` DATE NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_customers_name` (`customer_name`),
    INDEX `idx_customers_segment` (`customer_segment`),
    INDEX `idx_customers_city_state` (`city`, `state`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table 3: categories
-- Purpose: Hierarchical Product Taxonomy
-- ============================================================================
CREATE TABLE `categories` (
    `category_id` INT AUTO_INCREMENT PRIMARY KEY,
    `category_name` VARCHAR(60) NOT NULL UNIQUE,
    `description` TEXT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table 4: products
-- Purpose: Catalog, Pricing, and Stock Inventory
-- ============================================================================
CREATE TABLE `products` (
    `product_id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_name` VARCHAR(120) NOT NULL,
    `category_id` INT NOT NULL,
    `SKU` VARCHAR(50) NOT NULL UNIQUE,
    `unit_price` DECIMAL(10, 2) NOT NULL,
    `unit_cost` DECIMAL(10, 2) NOT NULL,
    `stock_quantity` INT NOT NULL DEFAULT 0,
    `reorder_level` INT NOT NULL DEFAULT 10,
    `product_status` VARCHAR(30) NOT NULL DEFAULT 'Active' 
        COMMENT 'Active, Discontinued, Out of Stock',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_products_category`
        FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `chk_unit_price` CHECK (`unit_price` >= 0),
    CONSTRAINT `chk_unit_cost` CHECK (`unit_cost` >= 0),
    CONSTRAINT `chk_stock_quantity` CHECK (`stock_quantity` >= 0),
    CONSTRAINT `chk_reorder_level` CHECK (`reorder_level` >= 0),
    INDEX `idx_products_category` (`category_id`),
    INDEX `idx_products_status` (`product_status`),
    INDEX `idx_products_name` (`product_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table 5: orders
-- Purpose: Sales Header and Transaction Metadata
-- ============================================================================
CREATE TABLE `orders` (
    `order_id` INT AUTO_INCREMENT PRIMARY KEY,
    `customer_id` INT NOT NULL,
    `order_date` DATETIME NOT NULL,
    `order_status` VARCHAR(30) NOT NULL DEFAULT 'Completed' 
        COMMENT 'Completed, Pending, Processing, Cancelled, Returned',
    `payment_status` VARCHAR(30) NOT NULL DEFAULT 'Paid' 
        COMMENT 'Paid, Pending, Failed, Refunded',
    `payment_method` VARCHAR(40) NOT NULL DEFAULT 'Credit Card' 
        COMMENT 'Credit Card, Bank Transfer, UPI, Cash on Delivery',
    `created_by` INT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_orders_customer`
        FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_orders_user`
        FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`)
        ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX `idx_orders_customer` (`customer_id`),
    INDEX `idx_orders_date` (`order_date`),
    INDEX `idx_orders_status` (`order_status`),
    INDEX `idx_orders_payment` (`payment_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table 6: order_items
-- Purpose: Order Line Items with Point-in-time Price & Cost Snapshot
-- ============================================================================
CREATE TABLE `order_items` (
    `order_item_id` INT AUTO_INCREMENT PRIMARY KEY,
    `order_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    `quantity` INT NOT NULL,
    `unit_price_at_sale` DECIMAL(10, 2) NOT NULL,
    `unit_cost_at_sale` DECIMAL(10, 2) NOT NULL,
    `discount_amount` DECIMAL(10, 2) NOT NULL DEFAULT 0.00 
        COMMENT 'Total line-item discount in monetary units',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_order_items_order`
        FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_order_items_product`
        FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `chk_item_quantity` CHECK (`quantity` > 0),
    CONSTRAINT `chk_item_price` CHECK (`unit_price_at_sale` >= 0),
    CONSTRAINT `chk_item_cost` CHECK (`unit_cost_at_sale` >= 0),
    CONSTRAINT `chk_item_discount` CHECK (`discount_amount` >= 0),
    INDEX `idx_order_items_order` (`order_id`),
    INDEX `idx_order_items_product` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table 7: sales_targets
-- Purpose: Benchmark Targets for Period Performance Comparison
-- ============================================================================
CREATE TABLE `sales_targets` (
    `target_id` INT AUTO_INCREMENT PRIMARY KEY,
    `target_period` VARCHAR(7) NOT NULL COMMENT 'Format YYYY-MM e.g. 2026-05',
    `target_type` VARCHAR(40) NOT NULL DEFAULT 'Monthly Revenue' 
        COMMENT 'Monthly Revenue or Category Revenue',
    `category_id` INT NULL,
    `target_amount` DECIMAL(12, 2) NOT NULL,
    `created_by` INT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_targets_category`
        FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT `fk_targets_user`
        FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT `chk_target_amount` CHECK (`target_amount` > 0),
    INDEX `idx_targets_period` (`target_period`),
    INDEX `idx_targets_category` (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Analytical Views for Optimized Querying and Role-Based Separation
-- ============================================================================

-- View: vw_completed_sales_items
-- Consolidates recognized sales line items (Completed & Paid)
CREATE OR REPLACE VIEW `vw_completed_sales_items` AS
SELECT 
    oi.order_item_id,
    o.order_id,
    o.order_date,
    o.customer_id,
    c.customer_name,
    c.customer_segment,
    c.city,
    c.state,
    p.product_id,
    p.product_name,
    p.category_id,
    cat.category_name,
    oi.quantity,
    oi.unit_price_at_sale,
    oi.unit_cost_at_sale,
    oi.discount_amount,
    -- Recognized Net Sales Revenue per item
    ((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) AS line_revenue,
    -- Cost of Goods Sold (COGS)
    (oi.quantity * oi.unit_cost_at_sale) AS line_cogs,
    -- Gross Profit per line item
    (((oi.quantity * oi.unit_price_at_sale) - oi.discount_amount) - (oi.quantity * oi.unit_cost_at_sale)) AS line_gross_profit
FROM `orders` o
JOIN `customers` c ON o.customer_id = c.customer_id
JOIN `order_items` oi ON o.order_id = oi.order_id
JOIN `products` p ON oi.product_id = p.product_id
JOIN `categories` cat ON p.category_id = cat.category_id
WHERE o.order_status = 'Completed' AND o.payment_status = 'Paid';
