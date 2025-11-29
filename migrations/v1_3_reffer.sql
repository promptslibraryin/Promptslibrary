-- ============================================================
-- Prompts-Library v1.3 Full Schema Migration for MySQL 8.0
-- ============================================================
-- This migration adds all missing fields and tables from v1.1/v1.2
-- Run this on existing database (backup.sql reference)
-- 
-- Host: localhost
-- User: hardik
-- Password: hardik@005
-- Database: prompt_gallery
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- STEP 1: Add Referral System fields to User table (v1.1)
-- ============================================================

-- Check and add referral_code column
SET @column_exists = (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'prompt_gallery' 
    AND TABLE_NAME = 'user' 
    AND COLUMN_NAME = 'referral_code'
);

SET @sql = IF(@column_exists = 0, 
    'ALTER TABLE `user` ADD COLUMN `referral_code` VARCHAR(12) NULL UNIQUE AFTER `user_role`',
    'SELECT "referral_code already exists"'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Check and add referred_by column
SET @column_exists = (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'prompt_gallery' 
    AND TABLE_NAME = 'user' 
    AND COLUMN_NAME = 'referred_by'
);

SET @sql = IF(@column_exists = 0, 
    'ALTER TABLE `user` ADD COLUMN `referred_by` INT NULL AFTER `referral_code`',
    'SELECT "referred_by already exists"'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Check and add email_validated_provider column
SET @column_exists = (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'prompt_gallery' 
    AND TABLE_NAME = 'user' 
    AND COLUMN_NAME = 'email_validated_provider'
);

SET @sql = IF(@column_exists = 0, 
    'ALTER TABLE `user` ADD COLUMN `email_validated_provider` VARCHAR(50) NULL AFTER `referred_by`',
    'SELECT "email_validated_provider already exists"'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add foreign key for referred_by (self-referencing)
-- First check if foreign key exists
SET @fk_exists = (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
    WHERE TABLE_SCHEMA = 'prompt_gallery' 
    AND TABLE_NAME = 'user' 
    AND CONSTRAINT_NAME = 'fk_user_referred_by'
);

SET @sql = IF(@fk_exists = 0, 
    'ALTER TABLE `user` ADD CONSTRAINT `fk_user_referred_by` FOREIGN KEY (`referred_by`) REFERENCES `user`(`id`) ON DELETE SET NULL',
    'SELECT "fk_user_referred_by already exists"'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add index for referral_code
SET @idx_exists = (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
    WHERE TABLE_SCHEMA = 'prompt_gallery' 
    AND TABLE_NAME = 'user' 
    AND INDEX_NAME = 'idx_user_referral_code'
);

SET @sql = IF(@idx_exists = 0, 
    'CREATE INDEX `idx_user_referral_code` ON `user`(`referral_code`)',
    'SELECT "idx_user_referral_code already exists"'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


-- ============================================================
-- STEP 2: Create Referral Event table (v1.1)
-- ============================================================

CREATE TABLE IF NOT EXISTS `referral_event` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `referrer_id` INT NOT NULL COMMENT 'User who referred',
    `referred_user_id` INT NOT NULL COMMENT 'User who was referred',
    `event_type` VARCHAR(64) NOT NULL COMMENT 'signup_reward or purchase_reward',
    `coins_awarded` INT NOT NULL COMMENT 'Coins given to referrer',
    `purchase_coins` INT DEFAULT 0 COMMENT 'For purchase_reward: coins purchased by referred user',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_referral_event_referrer` (`referrer_id`),
    KEY `idx_referral_event_referred` (`referred_user_id`),
    KEY `idx_referral_event_type` (`event_type`),
    KEY `idx_referral_event_created` (`created_at`),
    CONSTRAINT `fk_referral_referrer` FOREIGN KEY (`referrer_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_referral_referred` FOREIGN KEY (`referred_user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci 
COMMENT='Tracks referral bonuses - signup rewards (20 coins) and purchase rewards (5%)';


-- ============================================================
-- STEP 3: Ensure all indexes exist on existing tables
-- ============================================================

-- Index for user.user_role (for quick creator/admin lookups)
SET @idx_exists = (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
    WHERE TABLE_SCHEMA = 'prompt_gallery' 
    AND TABLE_NAME = 'user' 
    AND INDEX_NAME = 'idx_user_role'
);

SET @sql = IF(@idx_exists = 0, 
    'CREATE INDEX `idx_user_role` ON `user`(`user_role`)',
    'SELECT "idx_user_role already exists"'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Index for prompt.access_level (for quick exclusive content queries)
SET @idx_exists = (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
    WHERE TABLE_SCHEMA = 'prompt_gallery' 
    AND TABLE_NAME = 'prompt' 
    AND INDEX_NAME = 'idx_prompt_access_level'
);

SET @sql = IF(@idx_exists = 0, 
    'CREATE INDEX `idx_prompt_access_level` ON `prompt`(`access_level`)',
    'SELECT "idx_prompt_access_level already exists"'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Index for prompt.created_at (for sorting)
SET @idx_exists = (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
    WHERE TABLE_SCHEMA = 'prompt_gallery' 
    AND TABLE_NAME = 'prompt' 
    AND INDEX_NAME = 'idx_prompt_created_at'
);

SET @sql = IF(@idx_exists = 0, 
    'CREATE INDEX `idx_prompt_created_at` ON `prompt`(`created_at` DESC)',
    'SELECT "idx_prompt_created_at already exists"'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


-- ============================================================
-- STEP 4: Generate referral codes for existing users
-- ============================================================

-- Update users without referral codes
-- This generates 8-character alphanumeric codes
UPDATE `user` 
SET `referral_code` = UPPER(SUBSTRING(MD5(CONCAT(id, email, UNIX_TIMESTAMP())), 1, 8))
WHERE `referral_code` IS NULL;


-- ============================================================
-- STEP 5: Verify schema integrity
-- ============================================================

-- Show final table structures
SELECT 'Migration completed successfully!' AS status;

-- Display user table columns
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'prompt_gallery' AND TABLE_NAME = 'user'
ORDER BY ORDINAL_POSITION;

-- Display referral_event table
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'prompt_gallery' AND TABLE_NAME = 'referral_event'
ORDER BY ORDINAL_POSITION;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- END OF MIGRATION
-- ============================================================
