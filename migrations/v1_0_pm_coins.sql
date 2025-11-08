-- -- v1_0_pm_coins.sql
-- -- PostgreSQL Migration Script for PM Coins System v1.0
-- -- Created: November 6, 2025

-- -- Add coin & role fields to users table
-- ALTER TABLE "user"
-- ADD COLUMN IF NOT EXISTS coins_balance INTEGER DEFAULT 0,
-- ADD COLUMN IF NOT EXISTS total_earned_coins INTEGER DEFAULT 0,
-- ADD COLUMN IF NOT EXISTS total_spent_coins INTEGER DEFAULT 0,
-- ADD COLUMN IF NOT EXISTS user_role VARCHAR(20) DEFAULT 'user';

-- -- Create coin transactions log table
-- CREATE TABLE IF NOT EXISTS coin_transaction (
--     id SERIAL PRIMARY KEY,
--     user_id INTEGER NOT NULL,
--     transaction_type VARCHAR(20) NOT NULL,
--     amount INTEGER NOT NULL,
--     description VARCHAR(255),
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
-- );

-- -- Create index on user_id for faster queries
-- CREATE INDEX IF NOT EXISTS idx_coin_transaction_user_id ON coin_transaction(user_id);
-- CREATE INDEX IF NOT EXISTS idx_coin_transaction_created_at ON coin_transaction(created_at);

-- -- Create circle system table (replacing follow system)
-- CREATE TABLE IF NOT EXISTS circle (
--     id SERIAL PRIMARY KEY,
--     user_id INTEGER NOT NULL,
--     creator_id INTEGER NOT NULL,
--     joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
--     FOREIGN KEY (creator_id) REFERENCES "user"(id) ON DELETE CASCADE,
--     UNIQUE(user_id, creator_id)
-- );

-- -- Create indexes for circle queries
-- CREATE INDEX IF NOT EXISTS idx_circle_user_id ON circle(user_id);
-- CREATE INDEX IF NOT EXISTS idx_circle_creator_id ON circle(creator_id);

-- -- Add prompt access level field
-- ALTER TABLE prompt
-- ADD COLUMN IF NOT EXISTS access_level VARCHAR(20) DEFAULT 'basic';

-- -- Add comment for tracking
-- COMMENT ON TABLE coin_transaction IS 'PM Coins transaction history for all users';
-- COMMENT ON TABLE circle IS 'Circle membership system - users join creators circles for exclusive content';

-- v1_0_pm_coins_mysql_legacy.sql
-- ✅ Fully compatible with all MySQL versions (5.7+)
-- PM Coins System v1.0 Migration
-- Created: November 6, 2025
-- Author: Hardik

-- ==========================================
-- 1️⃣ Add new columns to users table safely
-- ==========================================

-- coins_balance
SET @col_exists := (
  SELECT COUNT(*) 
  FROM INFORMATION_SCHEMA.COLUMNS 
  WHERE TABLE_NAME = 'user' AND COLUMN_NAME = 'coins_balance'
);
SET @query := IF(@col_exists = 0, 
  'ALTER TABLE `user` ADD COLUMN `coins_balance` INT DEFAULT 0;', 
  'SELECT "coins_balance already exists";'
);
PREPARE stmt FROM @query; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- total_earned_coins
SET @col_exists := (
  SELECT COUNT(*) 
  FROM INFORMATION_SCHEMA.COLUMNS 
  WHERE TABLE_NAME = 'user' AND COLUMN_NAME = 'total_earned_coins'
);
SET @query := IF(@col_exists = 0, 
  'ALTER TABLE `user` ADD COLUMN `total_earned_coins` INT DEFAULT 0;', 
  'SELECT "total_earned_coins already exists";'
);
PREPARE stmt FROM @query; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- total_spent_coins
SET @col_exists := (
  SELECT COUNT(*) 
  FROM INFORMATION_SCHEMA.COLUMNS 
  WHERE TABLE_NAME = 'user' AND COLUMN_NAME = 'total_spent_coins'
);
SET @query := IF(@col_exists = 0, 
  'ALTER TABLE `user` ADD COLUMN `total_spent_coins` INT DEFAULT 0;', 
  'SELECT "total_spent_coins already exists";'
);
PREPARE stmt FROM @query; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- user_role
SET @col_exists := (
  SELECT COUNT(*) 
  FROM INFORMATION_SCHEMA.COLUMNS 
  WHERE TABLE_NAME = 'user' AND COLUMN_NAME = 'user_role'
);
SET @query := IF(@col_exists = 0, 
  'ALTER TABLE `user` ADD COLUMN `user_role` VARCHAR(20) DEFAULT "user";', 
  'SELECT "user_role already exists";'
);
PREPARE stmt FROM @query; EXECUTE stmt; DEALLOCATE PREPARE stmt;


-- ==========================================
-- 2️⃣ Create coin transactions log table
-- ==========================================
CREATE TABLE IF NOT EXISTS `coin_transaction` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `transaction_type` VARCHAR(20) NOT NULL,
    `amount` INT NOT NULL,
    `description` VARCHAR(255),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX `idx_coin_transaction_user_id` ON `coin_transaction`(`user_id`);
CREATE INDEX `idx_coin_transaction_created_at` ON `coin_transaction`(`created_at`);


-- ==========================================
-- 3️⃣ Create circle (join/connect) system
-- ==========================================
CREATE TABLE IF NOT EXISTS `circle` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `creator_id` INT NOT NULL,
    `joined_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`creator_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `unique_user_creator` (`user_id`, `creator_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX `idx_circle_user_id` ON `circle`(`user_id`);
CREATE INDEX `idx_circle_creator_id` ON `circle`(`creator_id`);


-- ==========================================
-- 4️⃣ Add prompt access level field safely
-- ==========================================
SET @col_exists := (
  SELECT COUNT(*) 
  FROM INFORMATION_SCHEMA.COLUMNS 
  WHERE TABLE_NAME = 'prompt' AND COLUMN_NAME = 'access_level'
);
SET @query := IF(@col_exists = 0, 
  'ALTER TABLE `prompt` ADD COLUMN `access_level` VARCHAR(20) DEFAULT "basic";', 
  'SELECT "access_level already exists";'
);
PREPARE stmt FROM @query; EXECUTE stmt; DEALLOCATE PREPARE stmt;


-- ==========================================
-- 5️⃣ Optional Comments (MySQL)
-- ==========================================
ALTER TABLE `coin_transaction` COMMENT = 'PM Coins transaction history for all users';
ALTER TABLE `circle` COMMENT = 'Circle system - users join creators for exclusive content';
