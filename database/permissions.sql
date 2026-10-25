-- ============================================================================
-- DATA CONTROL LANGUAGE (DCL) & ACCESS CONTROL SCRIPT
-- Demonstrating: Database User Creation, GRANT, REVOKE, SHOW GRANTS,
-- and Least-Privilege Role Separation.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Create Dedicated Application Service Account (Read/Write)
-- Used by the Flask backend for normal operational transactions
-- ----------------------------------------------------------------------------
CREATE USER IF NOT EXISTS 'bi_app_user'@'localhost' IDENTIFIED BY 'BiAppSecurePass2026!';

-- Grant strictly required DML and limited DDL privileges to the application user
GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE 
    ON `business_sales_intelligence`.* 
    TO 'bi_app_user'@'localhost';

-- ----------------------------------------------------------------------------
-- 2. Create Dedicated Read-Only Reporting / Manager Account
-- Restricted strictly to analytical views and reporting queries
-- ----------------------------------------------------------------------------
CREATE USER IF NOT EXISTS 'bi_report_user'@'localhost' IDENTIFIED BY 'ReportUser2026!';

-- Grant SELECT only on the analytical view and dimension tables
GRANT SELECT ON `business_sales_intelligence`.`vw_completed_sales_items` TO 'bi_report_user'@'localhost';
GRANT SELECT ON `business_sales_intelligence`.`categories` TO 'bi_report_user'@'localhost';
GRANT SELECT ON `business_sales_intelligence`.`products` TO 'bi_report_user'@'localhost';
GRANT SELECT ON `business_sales_intelligence`.`sales_targets` TO 'bi_report_user'@'localhost';

-- ----------------------------------------------------------------------------
-- 3. Revoke Demonstration
-- Example: Revoking sensitive customer data access from the reporting user
-- ----------------------------------------------------------------------------
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'bi_report_user'@'localhost';

-- Re-grant only the approved analytical view
GRANT SELECT ON `business_sales_intelligence`.`vw_completed_sales_items` TO 'bi_report_user'@'localhost';

-- ----------------------------------------------------------------------------
-- 4. Flush privileges and inspect effective grants
-- ----------------------------------------------------------------------------
FLUSH PRIVILEGES;

-- Verify effective permissions:
SHOW GRANTS FOR 'bi_app_user'@'localhost';
SHOW GRANTS FOR 'bi_report_user'@'localhost';
