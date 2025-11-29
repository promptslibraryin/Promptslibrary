# Prompts-Library - AI Social & Gamified Platform

## Overview
Prompts-Library is India's first AI-powered social platform where creators share prompts, connect with circles, and earn coins through gamified creativity. This platform allows users to discover, share, and manage a variety of AI-generated content prompts.

## Current State
- **Status**: Running successfully on Replit
- **Frontend**: Flask web application with HTML templates
- **Backend**: Python Flask with MySQL database (external service required)
- **Port**: 5000 (configured for Replit webview)
- **Database**: Uses `MYSQL_DATABASE_URL` for production MySQL, falls back to SQLite for development

## Recent Changes
### November 29, 2025 - Referral System & Mobile Improvements v1.2
- **Referral & Earn System**: Implemented referral code system with:
  - 20 PM Coins awarded to both referrer and referred user after OTP verification (prevents abuse)
  - 5% ongoing bonus on all coin purchases made by referrals (floor calculation)
  - ReferralEvent model for tracking referral bonuses
  - API endpoints: `/api/referral/link`, `/api/referral/stats`
- **Email Validation**: Added whitelist validation for email providers (Gmail, Yahoo, Zoho, Outlook, Hotmail, ProtonMail) with plus-addressing rejection
- **Free Basic Prompts**: Removed subscription checks - all basic prompts are now free to view
- **Premium Content via Circles**: Exclusive prompts require joining creator's circle (50 coins)
- **Admin Auto-Creator**: Admin users are automatically flagged as creators on login
- **Mobile Responsive CSS**: Comprehensive mobile-first CSS with:
  - Optimized header layout (logo + title + bell + 3-dots on one row)
  - Added `.auth-card` CSS class for reliable mobile styling on auth pages
  - Scrollable dropdown menus (max-height: 65vh)
  - Mobile-friendly hero section, cards, and grids
  - Touch-friendly buttons with proper tap targets (min 36px)
  - Grid layouts converting to single column on mobile
  - iOS zoom prevention (16px minimum font on inputs)
- **Landing Page Updates**: Added referral section with messaging about 20 coins + 5% forever benefits

### November 6, 2025 - PM Coins v1.0 Launch & Mobile Improvements
- **PM Coins System**: Implemented virtual currency system with buy coins, become creator, and circle membership features
- **Circle Members Display**: Added Instagram-style followers display on creator profiles showing member avatars
- **Mobile Navigation Fix**: Fixed three-dot menu visibility on mobile devices
- **Admin Dashboard**: Created comprehensive admin panel with PM Coins statistics and transaction tracking
- **Security Fixes**: Moved Razorpay credentials to environment variables
- **Exclusive Content Access**: Implemented proper access control for exclusive prompts (creator/circle-only)
- Application running successfully with all v1.0 features operational

### November 6, 2025 - GitHub Import and Replit Setup
- Successfully imported project from GitHub
- Installed Python 3.11 and all dependencies from requirements.txt
- Installed psycopg2-binary for PostgreSQL database connectivity
- Configured Flask development workflow on port 5000 with host 0.0.0.0
- Set up deployment configuration with Gunicorn for production
- Verified database initialization and application functionality

## Project Architecture

### Technology Stack
- **Backend Framework**: Flask 3.1.2
- **Database**: MySQL (via external service like PlanetScale, Railway, etc.) with PyMySQL driver
- **ORM**: SQLAlchemy 2.0.43
- **Authentication**: Flask-Login 0.6.3
- **Payment Integration**: Razorpay 1.4.2
- **Template Engine**: Jinja2 3.1.6
- **WSGI Server**: Gunicorn 23.0.0 (production)

### Project Structure
```
/
├── app.py                 # Flask app initialization & config
├── main.py                # Development server entry point
├── wsgi.py                # Production WSGI entry point
├── models.py              # Database models (User, Category, Prompt, etc.)
├── routes.py              # Application routes and endpoints
├── extensions.py          # Flask extensions (SQLAlchemy)
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Homepage/gallery
│   ├── profile.html       # User profile editing
│   ├── public_profile.html # Public user profiles
│   ├── add_prompt.html    # Add new prompts
│   └── ...                # Other pages
├── static/                # Static assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   ├── images/            # Images and logos
│   └── uploads/           # User-uploaded content
│       ├── profiles/      # Profile pictures
│       └── prompts/       # Prompt images
└── requirements.txt       # Python dependencies
```

### Database Schema
- **User**: User accounts with profile info, social links, referral system fields (referral_code, referred_by, email_validated_provider)
- **Category**: Prompt categories with SEO-friendly slugs
- **Prompt**: User-created prompts with images, descriptions, and metadata
- **SavedPrompt**: User's saved/bookmarked prompts
- **Sponsorship**: Sponsored content management
- **Circle**: Creator circle memberships (50 coins to join)
- **CoinTransaction**: PM Coins transaction history
- **ReferralEvent**: Tracks referral bonuses (signup_bonus, purchase_reward)
- **Notification**: User notifications
- **WithdrawRequest**: Coin withdrawal requests

### Key Features
1. **SEO Optimizations**
   - Structured data (Schema.org JSON-LD)
   - Enhanced meta tags and Open Graph support
   - SEO-friendly URLs with slugs
   
2. **User Profiles**
   - Profile customization with bio and social links
   - Profile pictures and Instagram integration
   - Public profile pages with user statistics
   
3. **Prompt Management**
   - Create, edit, and delete prompts
   - Category-based organization
   - Image uploads for prompts
   - Save/bookmark functionality
   
4. **PM Coins & Circle System**
   - Free basic prompts for all users
   - Premium/exclusive prompts via creator circles (50 coins)
   - PM Coins: Buy coins (200 for ₹49, 1000 for ₹199)
   - Become Creator: 400 coins to upgrade
   - Razorpay payment integration

5. **Referral System**
   - Dedicated "Refer & Earn" page (/refer) with:
     - Referral link with copy button
     - Share buttons for WhatsApp, Telegram, Twitter
     - Stats showing total referrals and coins earned
     - List of referred users with verification status
   - Unique referral codes for each user
   - 20 PM Coins on signup (both parties, after OTP verification)
   - 5% ongoing bonus on referral purchases
   - Email provider validation (Gmail, Yahoo, Zoho, Outlook, Hotmail, ProtonMail)
   - Anti-aliasing (rejects plus-addressed emails)
   
6. **Admin Features**
   - User management
   - Sponsorship management
   - Content moderation

## Environment Variables
- `MYSQL_DATABASE_URL`: MySQL connection string (format: `mysql+pymysql://user:password@host/database`)
  - **Required for production** - use an external MySQL service (PlanetScale, Railway, etc.)
  - Falls back to SQLite for local development if not set
- `SESSION_SECRET`: Flask session secret key
- `RAZORPAY_KEY_ID`: Razorpay API key (optional)
- `RAZORPAY_KEY_SECRET`: Razorpay secret key (optional)

## Development (Replit)
- **Workflow**: Flask App (runs on port 5000)
- **Hot Reload**: Debug mode enabled for development
- **Database**: SQLite (automatic fallback when no MySQL URL set)

## Local Deployment (Your Machine)

### Step 1: Clone/Download the project
Download all files from Replit to your local machine.

### Step 2: Create MySQL Database
```sql
CREATE DATABASE prompt_gallery;
```

### Step 3: Set Environment Variable
**Windows (CMD):**
```cmd
set MYSQL_DATABASE_URL=mysql+pymysql://hardik:hardik%%40005@localhost/prompt_gallery
```

**Windows (PowerShell):**
```powershell
$env:MYSQL_DATABASE_URL="mysql+pymysql://hardik:hardik%40005@localhost/prompt_gallery"
```

**Linux/Mac:**
```bash
export MYSQL_DATABASE_URL="mysql+pymysql://hardik:hardik%40005@localhost/prompt_gallery"
```

> Note: `%40` is URL-encoded `@` character in password

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Run the Application
```bash
python main.py
```
App will run on http://localhost:5000

### MySQL Connection Details (Pre-configured)
- **Host**: localhost
- **User**: hardik
- **Password**: hardik@005
- **Database**: prompt_gallery

## Cloud Deployment
- **Type**: Autoscale (serverless)
- **Production Server**: Gunicorn with 2 workers
- **Port**: 5000 (exposed for web preview)

## User Preferences
- Theme: Professional, modern design with SEO focus
- Style: Pixel-art / neon aesthetic (pending implementation)
