-- ============================================================================
-- DDL DEMONSTRATION AND MODIFICATION SCRIPT
-- Demonstrating: CREATE TABLE, ALTER TABLE (ADD, MODIFY, DROP COLUMN,
-- ADD CONSTRAINT), CREATE INDEX, DROP INDEX, and safe DROP TABLE.
-- ============================================================================

USE `business_sales_intelligence`;

-- 1. Create a demonstration audit table
CREATE TABLE IF NOT EXISTS `order_audit_log` (
    `log_id` INT AUTO_INCREMENT PRIMARY KEY,
    `order_id` INT NOT NULL,
    `action_type` VARCHAR(30) NOT NULL,
    `old_status` VARCHAR(30) NULL,
    `new_status` VARCHAR(30) NULL,
    `changed_by` INT NULL,
    `changed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. ALTER TABLE: Add a column with comments
ALTER TABLE `order_audit_log`
    ADD COLUMN `remarks` VARCHAR(255) NULL AFTER `new_status`;

-- 3. ALTER TABLE: Modify column definition
ALTER TABLE `order_audit_log`
    MODIFY COLUMN `remarks` TEXT NULL;

-- 4. CREATE INDEX: Add a performance index on foreign reference
CREATE INDEX `idx_audit_order_id` ON `order_audit_log` (`order_id`);

-- 5. ALTER TABLE: Add foreign key constraint safely
ALTER TABLE `order_audit_log`
    ADD CONSTRAINT `fk_audit_order`
    FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`)
    ON DELETE CASCADE;

-- 6. DROP INDEX demonstration
ALTER TABLE `order_audit_log` DROP INDEX `idx_audit_order_id`;

-- 7. Re-create index
CREATE INDEX `idx_audit_order_id` ON `order_audit_log` (`order_id`);

-- 8. Safe DROP TABLE demonstration (Restricted to non-production demo entity)
-- Note: Destructive DDL like DROP TABLE must be executed only with strict authorization.
-- DROP TABLE IF EXISTS `order_audit_log`;
