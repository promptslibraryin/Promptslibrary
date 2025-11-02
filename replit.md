# Prompts-Library - AI Social & Gamified Platform

## Overview
Prompts-Library is India's first AI-powered social platform where creators share prompts, connect with circles, and earn coins through gamified creativity. This platform allows users to discover, share, and manage a variety of AI-generated content prompts.

## Current State
- **Status**: Running successfully on Replit
- **Frontend**: Flask web application with HTML templates
- **Backend**: Python Flask with PostgreSQL database
- **Port**: 5000 (configured for Replit webview)

## Recent Changes
### November 1, 2025 - Initial Replit Setup
- Migrated from MySQL to PostgreSQL for Replit compatibility
- Updated database configuration to use Replit's PostgreSQL instance
- Installed all Python dependencies (Flask, SQLAlchemy, psycopg2-binary, etc.)
- Configured workflow for Flask development server
- Set up deployment configuration with Gunicorn
- Added comprehensive .gitignore for Python projects

## Project Architecture

### Technology Stack
- **Backend Framework**: Flask 3.1.2
- **Database**: PostgreSQL (via Replit's built-in database)
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
- **User**: User accounts with profile info, social links, subscription status
- **Category**: Prompt categories with SEO-friendly slugs
- **Prompt**: User-created prompts with images, descriptions, and metadata
- **SavedPrompt**: User's saved/bookmarked prompts
- **Sponsorship**: Sponsored content management

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
   
4. **Subscription System**
   - Free trial support
   - Premium membership features
   - Razorpay payment integration
   
5. **Admin Features**
   - User management
   - Sponsorship management
   - Content moderation

## Environment Variables
- `DATABASE_URL`: PostgreSQL connection string (auto-configured by Replit)
- `SESSION_SECRET`: Flask session secret key
- `RAZORPAY_KEY_ID`: Razorpay API key (optional)
- `RAZORPAY_KEY_SECRET`: Razorpay secret key (optional)

## Development
- **Workflow**: Flask App (runs on port 5000)
- **Hot Reload**: Debug mode enabled for development
- **Database**: Automatically creates tables on first run

## Deployment
- **Type**: Autoscale (serverless)
- **Production Server**: Gunicorn with 2 workers
- **Port**: 5000 (exposed for web preview)

## User Preferences
- Theme: Professional, modern design with SEO focus
- Style: Pixel-art / neon aesthetic (pending implementation)
