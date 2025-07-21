from app import app, db

# Import models and routes after app is created
import models
import routes

# Install comprehensive TradeWise AI enhancements
from comprehensive_enhancement_manager import install_all_enhancements

print("🚀 Installing TradeWise AI Comprehensive Enhancements...")
enhancement_result = install_all_enhancements(app)

if enhancement_result['success']:
    print("✅ All enhancements installed successfully!")
    print(f"📊 Features: {enhancement_result['features_installed']} installed")
    print("🎯 TradeWise AI: Full-Featured Trading Platform Ready")
else:
    print("⚠️  Some enhancements may not be available")
    print(f"Error: {enhancement_result.get('error', 'Unknown')}")
from ai_trading_copilot import start_ai_copilot

# Apply production optimizations
try:
    from production_optimization_engine import apply_production_optimizations
    optimization_report = apply_production_optimizations(app)
    print(f"✅ Production optimizations applied: {optimization_report['total_optimizations']} optimizations")
    print(f"✅ Performance score: {optimization_report['performance_score']['percentage']:.1f}% ({optimization_report['performance_score']['grade']})")
except Exception as e:
    print(f"⚠️ Production optimization error: {e}")

# Apply institutional-grade optimizations
try:
    from institutional_optimization_engine import get_institutional_optimizer
    institutional_optimizer = get_institutional_optimizer(app)
    if institutional_optimizer:
        optimization_results = institutional_optimizer.apply_institutional_optimizations()
        print(f"🚀 Institutional optimizations applied: {len(optimization_results)} enterprise features")
        print("📊 TradeWise AI: Bloomberg Terminal Competitor - Institutional Grade Ready")
except Exception as e:
    print(f"⚠️ Institutional optimization error: {e}")

# Create tables
with app.app_context():
    db.create_all()
    
# Start AI copilot service for premium users
start_ai_copilot()

# WebSocket optimization for App Store deployment
# Disabled WebSocket features to prevent memory issues and worker crashes

if __name__ == '__main__':
    # Production-ready configuration for App Store
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
