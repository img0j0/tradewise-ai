"""
Route Audit System for TradeWise AI Platform
Verifies UI button mappings to valid endpoints and identifies mismatches
"""

import logging
import requests
from typing import Dict, List, Tuple, Any
from flask import Blueprint, jsonify
import re

logger = logging.getLogger(__name__)

class RouteAuditor:
    """Audits platform routes to ensure UI buttons map to valid endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.expected_routes = {}
        self.ui_button_mappings = {}
        self.audit_results = {}
        
    def register_expected_route(self, route: str, method: str = "GET", 
                              description: str = "", ui_element: str = ""):
        """Register an expected route for auditing"""
        self.expected_routes[route] = {
            'method': method,
            'description': description,
            'ui_element': ui_element,
            'status': 'pending'
        }
    
    def register_ui_button_mapping(self, button_id: str, target_route: str, 
                                 button_description: str = ""):
        """Register UI button to route mapping"""
        self.ui_button_mappings[button_id] = {
            'target_route': target_route,
            'description': button_description,
            'status': 'pending'
        }
    
    def test_route(self, route: str, method: str = "GET") -> Dict:
        """Test a single route and return status"""
        try:
            url = f"{self.base_url}{route}"
            
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json={}, timeout=10)
            else:
                return {'status': 'unsupported_method', 'method': method}
            
            return {
                'status': 'success' if response.status_code < 400 else 'error',
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'content_length': len(response.content) if response.content else 0,
                'content_type': response.headers.get('content-type', 'unknown')
            }
            
        except requests.exceptions.ConnectionError:
            return {'status': 'connection_error', 'error': 'Cannot connect to server'}
        except requests.exceptions.Timeout:
            return {'status': 'timeout', 'error': 'Request timed out'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def audit_all_routes(self) -> Dict:
        """Audit all registered routes"""
        results = {
            'audit_timestamp': f"{logger.name}_{int(__import__('time').time())}",
            'total_routes': len(self.expected_routes),
            'successful_routes': 0,
            'failed_routes': 0,
            'route_details': {},
            'ui_mapping_results': {},
            'summary': {}
        }
        
        # Test all expected routes
        for route, config in self.expected_routes.items():
            test_result = self.test_route(route, config['method'])
            
            route_result = {
                'expected': config,
                'actual': test_result,
                'match': test_result['status'] == 'success'
            }
            
            results['route_details'][route] = route_result
            
            if route_result['match']:
                results['successful_routes'] += 1
            else:
                results['failed_routes'] += 1
        
        # Verify UI button mappings
        for button_id, mapping in self.ui_button_mappings.items():
            target_route = mapping['target_route']
            
            if target_route in results['route_details']:
                mapping_result = results['route_details'][target_route]['match']
                status = 'valid' if mapping_result else 'broken'
            else:
                status = 'missing_route'
            
            results['ui_mapping_results'][button_id] = {
                'target_route': target_route,
                'description': mapping['description'],
                'status': status
            }
        
        # Generate summary
        ui_valid = sum(1 for r in results['ui_mapping_results'].values() if r['status'] == 'valid')
        ui_total = len(results['ui_mapping_results'])
        
        results['summary'] = {
            'route_success_rate': (results['successful_routes'] / results['total_routes']) * 100 if results['total_routes'] > 0 else 0,
            'ui_mapping_success_rate': (ui_valid / ui_total) * 100 if ui_total > 0 else 0,
            'critical_issues': results['failed_routes'],
            'ui_issues': ui_total - ui_valid,
            'overall_health': 'healthy' if results['failed_routes'] == 0 and ui_total == ui_valid else 'issues_detected'
        }
        
        self.audit_results = results
        return results
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations based on audit results"""
        recommendations = []
        
        if not self.audit_results:
            return ["Run audit_all_routes() first to get recommendations"]
        
        failed_routes = [route for route, details in self.audit_results['route_details'].items() 
                        if not details['match']]
        
        broken_ui = [button for button, details in self.audit_results['ui_mapping_results'].items()
                    if details['status'] != 'valid']
        
        if failed_routes:
            recommendations.append(f"Fix {len(failed_routes)} failed routes: {', '.join(failed_routes[:3])}")
        
        if broken_ui:
            recommendations.append(f"Fix {len(broken_ui)} broken UI mappings: {', '.join(broken_ui[:3])}")
        
        if self.audit_results['summary']['route_success_rate'] < 90:
            recommendations.append("Route success rate below 90% - critical platform stability issue")
        
        if self.audit_results['summary']['ui_mapping_success_rate'] < 95:
            recommendations.append("UI mapping success rate below 95% - user experience issue")
        
        if not recommendations:
            recommendations.append("All routes and UI mappings are healthy - no action required")
        
        return recommendations

def initialize_route_auditor() -> RouteAuditor:
    """Initialize route auditor with all platform routes"""
    auditor = RouteAuditor()
    
    # Core platform routes
    auditor.register_expected_route("/", "GET", "Main dashboard redirect", "Logo/Home button")
    auditor.register_expected_route("/dashboard", "GET", "Dashboard page", "Dashboard button")
    auditor.register_expected_route("/search", "GET", "Search page", "Search button")
    
    # API endpoints
    auditor.register_expected_route("/api/health", "GET", "Health check", "System status")
    auditor.register_expected_route("/api/stock-analysis", "POST", "Stock analysis", "Analyze button")
    auditor.register_expected_route("/api/watchlist", "GET", "Watchlist data", "Watchlist button")
    auditor.register_expected_route("/api/alerts/active", "GET", "Active alerts", "Alerts button")
    auditor.register_expected_route("/api/favorites", "GET", "Favorites list", "Favorites button")
    auditor.register_expected_route("/api/search/suggestions", "GET", "Search suggestions", "Search autocomplete")
    auditor.register_expected_route("/api/search/history", "GET", "Search history", "History button")
    
    # Premium features
    auditor.register_expected_route("/api/ai/live-opportunities", "GET", "AI opportunities", "AI Scanner button")
    auditor.register_expected_route("/api/ai/enhanced-analysis", "POST", "Enhanced analysis", "Enhanced analysis")
    auditor.register_expected_route("/api/performance/stats", "GET", "Performance stats", "Performance metrics")
    
    # Tools registry routes
    auditor.register_expected_route("/tools/status", "GET", "Tools status", "System health")
    
    # Premium pages
    auditor.register_expected_route("/premium/upgrade", "GET", "Premium upgrade", "Upgrade button")
    auditor.register_expected_route("/backtest", "GET", "Backtesting", "Backtest button")
    auditor.register_expected_route("/peer_comparison", "GET", "Peer comparison", "Peer analysis button")
    
    # UI Button mappings
    auditor.register_ui_button_mapping("search-button", "/search", "Main search interface")
    auditor.register_ui_button_mapping("dashboard-button", "/dashboard", "Dashboard navigation")
    auditor.register_ui_button_mapping("watchlist-button", "/api/watchlist", "Watchlist data")
    auditor.register_ui_button_mapping("alerts-button", "/api/alerts/active", "Active alerts")
    auditor.register_ui_button_mapping("favorites-button", "/api/favorites", "Favorites management")
    auditor.register_ui_button_mapping("premium-upgrade", "/premium/upgrade", "Premium upgrade page")
    auditor.register_ui_button_mapping("ai-scanner", "/api/ai/live-opportunities", "AI market scanner")
    auditor.register_ui_button_mapping("backtest-tool", "/backtest", "Portfolio backtesting")
    auditor.register_ui_button_mapping("peer-analysis", "/peer_comparison", "Peer comparison tool")
    auditor.register_ui_button_mapping("health-status", "/tools/status", "System health check")
    
    logger.info(f"Route auditor initialized with {len(auditor.expected_routes)} routes and {len(auditor.ui_button_mappings)} UI mappings")
    
    return auditor

# Create audit blueprint
audit_bp = Blueprint('audit', __name__, url_prefix='/audit')

@audit_bp.route('/routes')
def audit_routes():
    """Run comprehensive route audit"""
    try:
        auditor = initialize_route_auditor()
        results = auditor.audit_all_routes()
        recommendations = auditor.get_recommendations()
        
        return jsonify({
            'success': True,
            'audit_results': results,
            'recommendations': recommendations,
            'audit_summary': {
                'total_routes_tested': results['total_routes'],
                'successful_routes': results['successful_routes'],
                'failed_routes': results['failed_routes'],
                'ui_mappings_tested': len(results['ui_mapping_results']),
                'route_health': results['summary']['overall_health'],
                'success_rate': f"{results['summary']['route_success_rate']:.1f}%"
            }
        })
        
    except Exception as e:
        logger.error(f"Route audit failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Route audit failed',
            'details': str(e)
        }), 500

@audit_bp.route('/ui-mappings')
def audit_ui_mappings():
    """Audit UI button to route mappings specifically"""
    try:
        auditor = initialize_route_auditor()
        results = auditor.audit_all_routes()
        
        ui_results = results['ui_mapping_results']
        
        return jsonify({
            'success': True,
            'ui_mappings': ui_results,
            'summary': {
                'total_mappings': len(ui_results),
                'valid_mappings': sum(1 for r in ui_results.values() if r['status'] == 'valid'),
                'broken_mappings': sum(1 for r in ui_results.values() if r['status'] != 'valid'),
                'success_rate': f"{results['summary']['ui_mapping_success_rate']:.1f}%"
            }
        })
        
    except Exception as e:
        logger.error(f"UI mapping audit failed: {e}")
        return jsonify({
            'success': False,
            'error': 'UI mapping audit failed',
            'details': str(e)
        }), 500