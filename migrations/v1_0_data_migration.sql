-- -- v1_0_data_migration.sql
-- -- Data Migration Script for PM Coins System v1.0
-- -- Created: November 6, 2025

-- -- Initialize default balances for all existing users
-- UPDATE "user" 
-- SET coins_balance = 0, 
--     total_earned_coins = 0, 
--     total_spent_coins = 0,
--     user_role = 'user'
-- WHERE coins_balance IS NULL;

-- -- Mark existing admin users
-- UPDATE "user" 
-- SET user_role = 'admin' 
-- WHERE is_admin = TRUE;

-- -- Mark existing subscribed users as creators (optional - adjust based on your logic)
-- -- Uncomment if you want all subscribed users to become creators
-- -- UPDATE "user" 
-- -- SET user_role = 'creator' 
-- -- WHERE is_subscribed = TRUE AND user_role = 'user';

-- -- Set all existing prompts to 'basic' access level
-- UPDATE prompt 
-- SET access_level = 'basic' 
-- WHERE access_level IS NULL;

-- -- Drop old follow table if it exists
-- DROP TABLE IF EXISTS follows CASCADE;
-- DROP TABLE IF EXISTS follow CASCADE;

-- -- Add initial welcome coins to all existing users (optional - 100 coins)
-- -- Uncomment if you want to give welcome bonus
-- -- UPDATE "user" SET coins_balance = coins_balance + 100, total_earned_coins = total_earned_coins + 100;
-- -- INSERT INTO coin_transaction (user_id, transaction_type, amount, description)
-- -- SELECT id, 'add', 100, 'Welcome bonus - PM Coins v1.0 launch'
-- -- FROM "user";


-- v1_0_data_migration_mysql.sql
-- Data Migration Script for PM Coins System v1.0
-- Created: November 6, 2025
-- Author: Hardik

-- Initialize default balances for all existing users
UPDATE `user`
SET 
    coins_balance = 0,
    total_earned_coins = 0,
    total_spent_coins = 0,
    user_role = 'user'
WHERE coins_balance IS NULL;

-- Mark existing admin users
UPDATE `user`
SET user_role = 'admin'
WHERE is_admin = 1;

-- Mark existing subscribed users as creators (optional - adjust based on your logic)
-- Uncomment if you want all subscribed users to become creators
-- UPDATE `user`
-- SET user_role = 'creator'
-- WHERE is_subscribed = 1 AND user_role = 'user';

-- Set all existing prompts to 'basic' access level
UPDATE `prompt`
SET access_level = 'basic'
WHERE access_level IS NULL;

-- Drop old follow table if it exists
DROP TABLE IF EXISTS `follows`;
DROP TABLE IF EXISTS `follow`;

-- Add initial welcome coins to all existing users (optional - 100 coins)
-- Uncomment if you want to give welcome bonus
-- UPDATE `user`
-- SET coins_balance = coins_balance + 100,
--     total_earned_coins = total_earned_coins + 100;
--
-- INSERT INTO coin_transaction (user_id, transaction_type, amount, description)
-- SELECT id, 'add', 100, 'Welcome bonus - PM Coins v1.0 launch'
-- FROM `user`;
