#!/usr/bin/env python3
"""
Simple Plan Feature Test - No Flask Context Required
"""

def show_plan_comparison():
    """Show clear plan differences without Flask context"""
    
    # Define the exact same configs as in subscription manager
    plans = {
        'free': {
            'name': 'Free Plan',
            'price': '$0/month',
            'api_requests': 50,
            'alerts': 5,
            'watchlist': 10,
            'portfolio_holdings': 10,
            'features': {
                'basic_stock_analysis': True,
                'ai_insights': False,
                'portfolio_backtesting': False,
                'market_scanner': False,
                'real_time_alerts': False,
                'api_access': False,
                'team_collaboration': False
            }
        },
        'pro': {
            'name': 'Pro Plan',
            'price': '$29.99/month',
            'api_requests': 1000,
            'alerts': 100,
            'watchlist': 200,
            'portfolio_holdings': 100,
            'features': {
                'basic_stock_analysis': True,
                'ai_insights': True,
                'portfolio_backtesting': True,
                'market_scanner': True,
                'real_time_alerts': True,
                'api_access': False,
                'team_collaboration': False
            }
        },
        'enterprise': {
            'name': 'Enterprise Plan',
            'price': '$99.99/month',
            'api_requests': 10000,
            'alerts': 500,
            'watchlist': 1000,
            'portfolio_holdings': 500,
            'features': {
                'basic_stock_analysis': True,
                'ai_insights': True,
                'portfolio_backtesting': True,
                'market_scanner': True,
                'real_time_alerts': True,
                'api_access': True,
                'team_collaboration': True
            }
        }
    }
    
    print("TradeWise AI Plan Comparison")
    print("=" * 80)
    
    # Feature comparison
    features = ['ai_insights', 'portfolio_backtesting', 'market_scanner', 'real_time_alerts', 'api_access', 'team_collaboration']
    
    print(f"{'Feature':<25} {'Free':<10} {'Pro':<10} {'Enterprise':<15}")
    print("-" * 70)
    
    for feature in features:
        free_check = "✓" if plans['free']['features'][feature] else "✗"
        pro_check = "✓" if plans['pro']['features'][feature] else "✗"
        enterprise_check = "✓" if plans['enterprise']['features'][feature] else "✗"
        
        feature_name = feature.replace('_', ' ').title()
        print(f"{feature_name:<25} {free_check:<10} {pro_check:<10} {enterprise_check:<15}")
    
    print("\nUsage Limits:")
    print("-" * 70)
    print(f"{'Limit':<25} {'Free':<10} {'Pro':<10} {'Enterprise':<15}")
    print(f"{'API Requests/Day':<25} {plans['free']['api_requests']:<10} {plans['pro']['api_requests']:<10} {plans['enterprise']['api_requests']:<15}")
    print(f"{'Smart Alerts':<25} {plans['free']['alerts']:<10} {plans['pro']['alerts']:<10} {plans['enterprise']['alerts']:<15}")
    print(f"{'Watchlist Items':<25} {plans['free']['watchlist']:<10} {plans['pro']['watchlist']:<10} {plans['enterprise']['watchlist']:<15}")
    print(f"{'Portfolio Holdings':<25} {plans['free']['portfolio_holdings']:<10} {plans['pro']['portfolio_holdings']:<10} {plans['enterprise']['portfolio_holdings']:<15}")
    
    print("\nPricing:")
    print("-" * 70)
    for plan_key, plan_data in plans.items():
        print(f"{plan_data['name']}: {plan_data['price']}")
    
    print("\nKey Differences:")
    print("• Free: Basic analysis only, limited usage")
    print("• Pro: AI insights, backtesting, advanced features")  
    print("• Enterprise: API access, team features, unlimited usage")
    
    return True

if __name__ == "__main__":
    show_plan_comparison()