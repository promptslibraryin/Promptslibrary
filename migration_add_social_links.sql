-- =====================================================
-- DATABASE MIGRATION: Add Social Media Links to Users
-- =====================================================
-- Version: 1.0
-- Date: 2025
-- Description: Adds GitHub, LinkedIn, Twitter, and Portfolio URL fields to the User table
--
-- Purpose: Enable users to showcase their professional presence across multiple platforms
-- This enhances user profiles and improves SEO through structured data
--
-- TABLES AFFECTED:
--   - user: Adding 4 new VARCHAR columns for social media links
--
-- CHANGES SUMMARY:
--   1. Add github_url column (max 200 characters)
--   2. Add linkedin_url column (max 200 characters)
--   3. Add twitter_url column (max 200 characters)
--   4. Add portfolio_url column (max 200 characters)
--
-- SAFETY: This migration is non-destructive and backward compatible
-- All new columns are NULLABLE, so existing data remains intact
-- =====================================================

-- Step 1: Add GitHub URL column
ALTER TABLE user ADD COLUMN IF NOT EXISTS github_url VARCHAR(200) NULL;

-- Step 2: Add LinkedIn URL column
ALTER TABLE user ADD COLUMN IF NOT EXISTS linkedin_url VARCHAR(200) NULL;

-- Step 3: Add Twitter/X URL column
ALTER TABLE user ADD COLUMN IF NOT EXISTS twitter_url VARCHAR(200) NULL;

-- Step 4: Add Portfolio/Website URL column
ALTER TABLE user ADD COLUMN IF NOT EXISTS portfolio_url VARCHAR(200) NULL;

-- Verify the migration
SELECT
    'Migration completed successfully!' as status,
    COUNT(*) as total_users,
    SUM(CASE WHEN github_url IS NOT NULL THEN 1 ELSE 0 END) as users_with_github,
    SUM(CASE WHEN linkedin_url IS NOT NULL THEN 1 ELSE 0 END) as users_with_linkedin,
    SUM(CASE WHEN twitter_url IS NOT NULL THEN 1 ELSE 0 END) as users_with_twitter,
    SUM(CASE WHEN portfolio_url IS NOT NULL THEN 1 ELSE 0 END) as users_with_portfolio
FROM user;

-- =====================================================
-- ROLLBACK SCRIPT (if needed)
-- =====================================================
-- CAUTION: Only use if you need to revert this migration
-- Uncomment the lines below to remove the social link columns
--
-- ALTER TABLE user DROP COLUMN IF EXISTS github_url;
-- ALTER TABLE user DROP COLUMN IF EXISTS linkedin_url;
-- ALTER TABLE user DROP COLUMN IF EXISTS twitter_url;
-- ALTER TABLE user DROP COLUMN IF EXISTS portfolio_url;
-- =====================================================

-- =====================================================
-- TESTING QUERIES
-- =====================================================
-- Use these queries to test the new functionality

-- Test 1: Check if columns exist
DESCRIBE user;

-- Test 2: Sample update (replace with actual user ID)
-- UPDATE user
-- SET
--     github_url = 'https://github.com/username',
--     linkedin_url = 'https://linkedin.com/in/username',
--     twitter_url = 'https://twitter.com/username',
--     portfolio_url = 'https://yourwebsite.com'
-- WHERE id = 1;

-- Test 3: Verify social links for a user
-- SELECT
--     id,
--     username,
--     email,
--     instagram_id,
--     github_url,
--     linkedin_url,
--     twitter_url,
--     portfolio_url
-- FROM user
-- WHERE id = 1;

-- =====================================================
-- NOTES FOR DEVELOPERS
-- =====================================================
--
-- 1. Frontend Integration:
--    - Updated templates/profile.html with new input fields
--    - Updated templates/public_profile.html to display social links
--    - Added Font Awesome icons for visual consistency
--
-- 2. Backend Integration:
--    - Updated models.py User class with new db.Column definitions
--    - Updated routes.py profile() function to handle new form fields
--    - Added validation for URL formats in the frontend
--
-- 3. SEO Benefits:
--    - Social links are included in Person schema structured data
--    - Improves profile discoverability in search engines
--    - Enables rich snippets in search results
--
-- 4. Security Considerations:
--    - All URLs should be validated on the frontend
--    - Consider adding backend URL validation
--    - Sanitize user input to prevent XSS attacks
--    - rel="noopener noreferrer" added to external links
--
-- 5. Performance:
--    - New columns are indexed automatically with user.id
--    - No additional indexes needed unless you plan to search by social URLs
--    - Minimal impact on query performance
--
-- =====================================================
