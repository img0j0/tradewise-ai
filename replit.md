# Trading Analytics Platform

## Overview

This is a Python Flask-based web application that provides AI-powered stock trading insights and portfolio management. The platform creates an experience where users feel like they have a personal AI assistant working alongside them to build their investment portfolio. It features a professional dark theme with vibrant colors, real-time data updates, and comprehensive portfolio tracking that makes even average investors feel like pros.

## User Preferences

```
Preferred communication style: Simple, everyday language.
```

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM (connected via DATABASE_URL)
- **AI/ML**: scikit-learn with Random Forest classifier for trading predictions
- **Data Processing**: pandas and numpy for data manipulation and analysis

### Frontend Architecture
- **Templates**: Jinja2 templating engine with Bootstrap 5 for responsive UI
- **JavaScript**: Vanilla JavaScript for dynamic interactions and real-time updates
- **Styling**: Custom CSS with CSS variables for theme switching
- **Charts**: Chart.js for data visualization

### Data Layer
- **Models**: SQLAlchemy models for Trade, Portfolio, and Alert entities
- **Data Service**: JSON-based sample data loader with fallback mechanisms
- **AI Engine**: Machine learning service for generating trading insights

## Key Components

### Database Models
- **Trade**: Records buy/sell transactions with confidence scores
- **Portfolio**: Tracks current stock holdings and average prices
- **Alert**: Manages trading alerts and notifications

### Core Services
- **AIInsightsEngine**: Implements Random Forest classification for trading predictions
- **DataService**: Handles sample stock data loading and market overview calculations
- **Routes**: RESTful API endpoints for dashboard data and trading operations, including AI assistant chat endpoints

### Frontend Components
- **Dashboard**: Real-time market overview with welcome banner showing AI accuracy and market trend
- **Stock Analysis**: Individual stock performance and AI insights
- **Portfolio Management**: Holdings tracking and performance metrics
- **Alert System**: Configurable trading alerts and notifications
- **AI Assistant**: Interactive chat interface providing market overview, top picks, portfolio advice, and risk analysis

## Data Flow

1. **Data Ingestion**: Sample stock data loaded from JSON files or generated dynamically
2. **Feature Engineering**: AI engine processes raw stock data into ML features (price changes, volume ratios, technical indicators)
3. **Model Training**: Random Forest classifier trained on historical patterns
4. **Prediction Generation**: AI generates trading recommendations with confidence scores
5. **UI Updates**: Frontend polls backend APIs for real-time data updates
6. **User Interactions**: Trading actions recorded in database with portfolio updates

## External Dependencies

### Python Packages
- Flask ecosystem (Flask, Flask-SQLAlchemy)
- Machine Learning (scikit-learn, pandas, numpy)
- Database (SQLAlchemy, sqlite3)

### Frontend Libraries
- Bootstrap 5 for responsive design
- Chart.js for data visualization
- Font Awesome for icons

### Development Tools
- Werkzeug for WSGI middleware
- Python logging for debugging and monitoring

## Recent Changes (July 16, 2025)

### AI Assistant Integration
- Added interactive AI assistant chat widget in the bottom-right corner with minimize/maximize functionality
- Implemented quick action buttons for market overview, top picks, portfolio advice, and risk analysis
- Created AI chat endpoints in routes.py for handling assistant requests
- Enhanced UI with typing indicators and animated message bubbles

### UI/UX Enhancements
- Added welcome banner with real-time AI accuracy and market trend indicators
- Enhanced dashboard with gradient backgrounds and glowing effects
- Improved card styling with distinct color schemes for different sections
- Added responsive design for mobile compatibility

## Deployment Strategy

### Environment Configuration
- PostgreSQL database connected via DATABASE_URL environment variable
- Environment-based secret key management
- Proxy-aware WSGI configuration for production deployment

### Database Setup
- PostgreSQL database with automatic table creation on application startup
- Database tables: Trade, Portfolio, and Alert for comprehensive trading data management
- Connection pooling and health checks configured for optimal performance
- SQLAlchemy ORM for database operations with support for complex queries

### Production Considerations
- WSGI server compatibility (Gunicorn, uWSGI)
- Static file serving optimization
- Environment variable configuration for secrets
- Database connection pooling for scalability

### Development Features
- Debug mode enabled for local development
- Hot reload capabilities
- Comprehensive logging for troubleshooting
- Sample data generation for testing

The application follows a traditional MVC pattern with clear separation of concerns, making it maintainable and scalable for future enhancements.