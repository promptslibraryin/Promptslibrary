-- Migration: v1.2 Referral System
-- Date: November 2025
-- Description: Adds referral system fields and creates ReferralEvent table
-- Compatible with both MySQL and SQLite

-- ===================
-- MySQL Version
-- ===================
-- Run this section on MySQL/MariaDB databases:

-- ALTER TABLE users ADD COLUMN referral_code VARCHAR(12) UNIQUE;
-- ALTER TABLE users ADD COLUMN referred_by INTEGER REFERENCES users(id);
-- ALTER TABLE users ADD COLUMN email_validated_provider VARCHAR(50);

-- CREATE TABLE IF NOT EXISTS referral_events (
--     id INTEGER PRIMARY KEY AUTO_INCREMENT,
--     referrer_id INTEGER NOT NULL,
--     referred_user_id INTEGER NOT NULL,
--     event_type VARCHAR(30) NOT NULL DEFAULT 'signup_bonus',
--     coins_awarded INTEGER NOT NULL DEFAULT 0,
--     purchase_coins INTEGER DEFAULT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (referrer_id) REFERENCES users(id),
--     FOREIGN KEY (referred_user_id) REFERENCES users(id)
-- );

-- CREATE INDEX idx_referral_code ON users(referral_code);
-- CREATE INDEX idx_referred_by ON users(referred_by);
-- CREATE INDEX idx_referrer_id ON referral_events(referrer_id);
-- CREATE INDEX idx_referred_user_id ON referral_events(referred_user_id);

-- ===================
-- SQLite Version
-- ===================
-- Run this section on SQLite databases (development):

-- Note: SQLite doesn't support ADD COLUMN IF NOT EXISTS
-- You can ignore errors if columns already exist

-- ALTER TABLE user ADD COLUMN referral_code VARCHAR(12) UNIQUE;
-- ALTER TABLE user ADD COLUMN referred_by INTEGER REFERENCES user(id);
-- ALTER TABLE user ADD COLUMN email_validated_provider VARCHAR(50);

-- CREATE TABLE IF NOT EXISTS referral_event (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     referrer_id INTEGER NOT NULL,
--     referred_user_id INTEGER NOT NULL,
--     event_type VARCHAR(30) NOT NULL DEFAULT 'signup_bonus',
--     coins_awarded INTEGER NOT NULL DEFAULT 0,
--     purchase_coins INTEGER DEFAULT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (referrer_id) REFERENCES user(id),
--     FOREIGN KEY (referred_user_id) REFERENCES user(id)
-- );

-- CREATE INDEX IF NOT EXISTS idx_referral_code ON user(referral_code);
-- CREATE INDEX IF NOT EXISTS idx_referred_by ON user(referred_by);
-- CREATE INDEX IF NOT EXISTS idx_referrer_id ON referral_event(referrer_id);
-- CREATE INDEX IF NOT EXISTS idx_referred_user_id ON referral_event(referred_user_id);

-- ===================
-- Common: Update existing admin users to be creators
-- ===================
-- MySQL: UPDATE users SET user_role = 'creator' WHERE is_admin = 1 AND (user_role IS NULL OR user_role != 'creator');
-- SQLite: UPDATE user SET user_role = 'creator' WHERE is_admin = 1 AND (user_role IS NULL OR user_role != 'creator');

-- ===================
-- Notes for Developers:
-- ===================
-- 1. The ORM (SQLAlchemy) will auto-create tables on first run with db.create_all()
-- 2. For production MySQL, run the MySQL section manually
-- 3. For development SQLite, SQLAlchemy handles the schema automatically
-- 4. The referral_code is 12 characters (8 alphanumeric + possible collision suffix)
-- 5. email_validated_provider stores the validated email domain (gmail, yahoo, etc.)
