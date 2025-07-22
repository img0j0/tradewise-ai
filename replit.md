# TradeWise AI - Comprehensive Trading Platform

## Overview

TradeWise AI is a sophisticated stock analysis platform that provides AI-powered investment research, real-time market data, and comprehensive stock insights. The platform combines modern web technologies with machine learning capabilities to deliver institutional-grade analysis tools focused purely on investment research without trading capabilities.

## Recent Changes (July 22, 2025)
- **Strategic Platform Pivot**: Successfully transformed from trading platform to pure stock analysis platform
- **Major Codebase Cleanup**: Removed 50+ conflicting Python modules and JavaScript files that were causing errors and interface conflicts
- **Trading Functionality Removal**: Eliminated all trading capabilities (accounts, transactions, payments, portfolio trading)
- **Analysis-Focused Database**: New models for StockAnalysis and WatchlistItem to track analysis history and research insights
- **API Transformation**: Updated /api/stock-search to /api/stock-analysis with enhanced AI-powered research capabilities
- **Analysis History Tracking**: Added functionality to save and compare AI recommendations over time
- **Streamlined Architecture**: Clean, focused codebase without conflicting interfaces or redundant trading code
- **Robot Mascot Fix**: Properly centered facial features using CSS transforms for perfect alignment
- **Stable Core Functionality**: Stock analysis API working reliably with real-time data from Yahoo Finance
- **Complete Smart Alerts System**: Fixed all LSP errors, added missing API endpoints (/api/alerts/suggestions, /api/alerts/create-smart, /api/alerts/active), and resolved frontend-backend URL mismatches for alert deletion functionality
- **Enhanced Alert Data Quality**: Integrated real-time market data from Yahoo Finance for current prices, improved alert descriptions, and dynamic current value updates for all price-based alerts
- **Fully Functional Alert Management**: Alerts can be created, deleted, and display with accurate real-time market data including current prices vs target values
- **Complete Watchlist Functionality**: Fixed duplicate displayWatchlist functions, added missing remove buttons, resolved CSS layout issues (justify-content), and enabled full watchlist management (add, remove, analyze stocks)
- **Portfolio Integration**: Fixed portfolio button function calls and verified all major platform tools are working correctly with real-time data integration

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Flask with Jinja2 templating
- **UI Libraries**: Bootstrap 5, Font Awesome icons, Chart.js for visualizations
- **CSS Organization**: Modular CSS files for specific features (style.css, premium_features.css, tier_styles.css, institutional_ui_optimization.css)
- **Mobile Optimization**: Responsive design with iPhone/iOS-specific optimizations
- **Real-time Updates**: WebSocket integration for live market data streaming

### Backend Architecture
- **Web Framework**: Flask with Blueprint organization
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Authentication**: Flask-Login for user session management
- **Password Security**: Werkzeug for password hashing
- **Performance**: Flask-Caching for data caching, Flask-Compress for response compression

### AI/ML Components
- **Machine Learning**: Scikit-learn for predictive models (RandomForest, GradientBoosting, MLPClassifier)
- **Data Processing**: Pandas and NumPy for data manipulation
- **Market Data**: yfinance library for real-time stock data
- **Natural Language**: TextBlob for sentiment analysis
- **Model Persistence**: Joblib for model serialization

## Key Components

### Core Services
1. **Intelligent Stock Analyzer** (`intelligent_stock_analyzer.py`) - Real-time stock analysis with AI insights
2. **AI Advice Engine** (`ai_advice_engine.py`) - Advanced ML-based trading recommendations
3. **Market Predictor** (`ai_market_predictor.py`) - Institutional-grade market forecasting
4. **Portfolio Manager** (`portfolio_manager.py`) - Comprehensive portfolio tracking and analytics
5. **Trading Copilot** (`ai_trading_copilot.py`) - Real-time AI assistant for trading signals

### User Management
- **Models** (`models.py`) - User, Portfolio, Trade, Alert, Transaction, UserAccount entities
- **Account Settings** (`account_settings.py`) - Payment methods, subscriptions, profile management
- **Subscription Tiers** - Free, Pro, Elite, Institutional with feature-based access control

### Data & Intelligence
- **Market Data Collector** (`market_data_collector.py`) - Real-time market data aggregation
- **News Service** (`market_news.py`) - News aggregation with sentiment analysis
- **Technical Indicators** (`technical_indicators.py`) - SMA, EMA, RSI calculations
- **Performance Tracking** (`performance_tracker.py`) - Portfolio metrics and analytics

### Advanced Features
- **Dynamic Search** (`dynamic_search_autocomplete.py`) - AI-powered stock search with autocomplete
- **Smart Alerts** (`smart_stock_alerts.py`) - Intelligent price and technical alerts
- **Strategy Builder** (`strategy_builder.py`) - Custom trading strategy creation and backtesting
- **Watchlist Manager** (`watchlist_manager.py`) - Professional watchlist management

## Data Flow

1. **User Interaction**: Users interact through responsive web interface or mobile-optimized views
2. **Authentication**: Flask-Login manages user sessions and access control
3. **Data Ingestion**: yfinance API provides real-time market data, cached for performance
4. **AI Processing**: Multiple ML models analyze data and generate insights
5. **Real-time Updates**: WebSocket connections stream live data to connected clients
6. **Database Operations**: SQLAlchemy handles all data persistence with relationship management
7. **Response Generation**: Formatted JSON responses for API calls, templated HTML for views

## External Dependencies

### Market Data
- **Yahoo Finance (yfinance)**: Primary data source for stock prices, company information, and historical data
- **Stripe API**: Payment processing for subscription management
- **Real-time WebSocket**: Live market data streaming to connected clients

### Machine Learning Stack
- **Scikit-learn**: Core ML algorithms for predictions and classifications
- **Pandas/NumPy**: Data processing and numerical computations
- **TextBlob**: Natural language processing for sentiment analysis

### Infrastructure
- **Redis** (optional): Advanced caching for high-performance scenarios
- **WebSocket**: Real-time bidirectional communication
- **Bootstrap/Chart.js**: Frontend UI components and data visualization

## Deployment Strategy

### Database Configuration
- **Development**: SQLite for local development and testing
- **Production**: PostgreSQL support configured via DATABASE_URL environment variable
- **Connection Pooling**: SQLAlchemy pool settings for production scalability

### Environment Configuration
- **Secrets Management**: Environment variables for API keys (STRIPE_SECRET_KEY)
- **Session Security**: Configurable session cookies with security headers
- **Performance Optimization**: Caching, compression, and connection pooling enabled

### Scaling Considerations
- **Performance Optimizer** (`performance_optimizer.py`) - Advanced caching and WebSocket pooling
- **Error Recovery** (`error_recovery.py`) - Comprehensive error handling and recovery mechanisms
- **Real-time Monitoring** - Performance tracking and optimization systems
- **Mobile Optimization** - iPhone/iOS specific optimizations for mobile deployment

### Key Architectural Decisions

1. **Modular Design**: Separated concerns with dedicated modules for different functionalities (AI, data, UI)
2. **Real-time Capabilities**: WebSocket implementation for live market data streaming
3. **AI-First Approach**: Multiple ML models provide comprehensive market intelligence
4. **Subscription Model**: Tiered access control with payment integration
5. **Mobile-First UI**: Responsive design optimized for mobile trading experience
6. **Performance Focus**: Caching strategies and optimization engines for scalability
7. **Error Resilience**: Comprehensive error handling and fallback mechanisms
8. **Data Consistency**: SQLAlchemy relationships ensure referential integrity

The platform is designed to scale from individual retail traders to institutional clients, with a focus on providing sophisticated AI-powered insights through an intuitive interface.