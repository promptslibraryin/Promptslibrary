-- -- v1_1_notifications_withdrawals.sql
-- -- PostgreSQL Migration Script for Notifications & Withdrawal System
-- -- Created: November 7, 2025
-- -- Author: AI Agent for Hardik

-- -- ==========================================
-- -- 1️⃣ Create notifications table
-- -- ==========================================
-- CREATE TABLE IF NOT EXISTS notification (
--     id SERIAL PRIMARY KEY,
--     user_id INTEGER NOT NULL,
--     message TEXT NOT NULL,
--     type VARCHAR(20) DEFAULT 'info',
--     is_read BOOLEAN DEFAULT FALSE,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
-- );

-- -- Create indexes for faster queries
-- CREATE INDEX IF NOT EXISTS idx_notification_user_id ON notification(user_id);
-- CREATE INDEX IF NOT EXISTS idx_notification_is_read ON notification(is_read);
-- CREATE INDEX IF NOT EXISTS idx_notification_created_at ON notification(created_at DESC);

-- -- ==========================================
-- -- 2️⃣ Create withdraw_requests table
-- -- ==========================================
-- CREATE TABLE IF NOT EXISTS withdraw_request (
--     id SERIAL PRIMARY KEY,
--     user_id INTEGER NOT NULL,
--     coins INTEGER NOT NULL,
--     amount DECIMAL(10,2) NOT NULL,
--     payment_method VARCHAR(50) NOT NULL,
--     payment_details TEXT NOT NULL,
--     status VARCHAR(20) DEFAULT 'pending',
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     admin_note TEXT,
--     FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
--     CHECK (coins >= 100),
--     CHECK (amount > 0),
--     CHECK (status IN ('pending', 'approved', 'rejected'))
-- );

-- -- Create indexes for faster queries
-- CREATE INDEX IF NOT EXISTS idx_withdraw_request_user_id ON withdraw_request(user_id);
-- CREATE INDEX IF NOT EXISTS idx_withdraw_request_status ON withdraw_request(status);
-- CREATE INDEX IF NOT EXISTS idx_withdraw_request_created_at ON withdraw_request(created_at DESC);

-- -- ==========================================
-- -- 3️⃣ Add comments for documentation
-- -- ==========================================
-- COMMENT ON TABLE notification IS 'User notifications for coins, circles, withdrawals, and admin messages';
-- COMMENT ON TABLE withdraw_request IS 'User withdrawal requests for PM Coins conversion to real currency';

-- v1_1_notifications_withdrawals_mysql.sql
-- ✅ MySQL Migration Script for Notifications & Withdrawal System
-- Created: November 7, 2025
-- Author: Hardik

-- ==========================================
-- 1️⃣ Create notifications table
-- ==========================================
CREATE TABLE IF NOT EXISTS `notification` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `message` TEXT NOT NULL,
    `type` VARCHAR(20) DEFAULT 'info',
    `is_read` TINYINT(1) DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create indexes for faster queries
CREATE INDEX `idx_notification_user_id` ON `notification`(`user_id`);
CREATE INDEX `idx_notification_is_read` ON `notification`(`is_read`);
CREATE INDEX `idx_notification_created_at` ON `notification`(`created_at`);

-- ==========================================
-- 2️⃣ Create withdraw_requests table
-- ==========================================
CREATE TABLE IF NOT EXISTS `withdraw_request` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `coins` INT NOT NULL,
    `amount` DECIMAL(10,2) NOT NULL,
    `payment_method` VARCHAR(50) NOT NULL,
    `payment_details` TEXT NOT NULL,
    `status` VARCHAR(20) DEFAULT 'pending',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `admin_note` TEXT,
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
    CHECK (`coins` >= 100),
    CHECK (`amount` > 0),
    CHECK (`status` IN ('pending', 'approved', 'rejected'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create indexes for faster queries
CREATE INDEX `idx_withdraw_request_user_id` ON `withdraw_request`(`user_id`);
CREATE INDEX `idx_withdraw_request_status` ON `withdraw_request`(`status`);
CREATE INDEX `idx_withdraw_request_created_at` ON `withdraw_request`(`created_at`);

-- ==========================================
-- 3️⃣ Add comments for documentation
-- ==========================================
ALTER TABLE `notification` COMMENT = 'User notifications for coins, circles, withdrawals, and admin messages';
ALTER TABLE `withdraw_request` COMMENT = 'User withdrawal requests for PM Coins conversion to real currency';
