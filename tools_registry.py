"""
Centralized Tool Registry for TradeWise AI Platform
Manages registration, health monitoring, and status checking for all tools
"""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from flask import Blueprint, jsonify, request
from functools import wraps
import traceback

logger = logging.getLogger(__name__)

class ToolsRegistry:
    """Central registry for all platform tools with health monitoring"""
    
    def __init__(self):
        self.tools = {}
        self.health_status = {}
        self.last_health_check = None
        self.initialization_time = datetime.utcnow()
        
    def register_tool(self, name: str, module_path: str, description: str, 
                     route_prefix: Optional[str] = None, health_check_func: Optional[callable] = None):
        """Register a tool with the central registry"""
        try:
            # Import the module dynamically
            module = None
            if module_path:
                try:
                    module = __import__(module_path, fromlist=[''])
                except ImportError as ie:
                    logger.warning(f"Could not import {module_path}: {ie}")
                    module = None
                
            tool_info = {
                'name': name,
                'module_path': module_path,
                'module': module,
                'description': description,
                'route_prefix': route_prefix or f'/tools/{name.lower()}',
                'health_check_func': health_check_func,
                'registration_time': datetime.utcnow(),
                'status': 'registered',
                'last_used': None,
                'usage_count': 0,
                'error_count': 0
            }
            
            self.tools[name] = tool_info
            self.health_status[name] = {'status': 'unknown', 'last_check': None}
            
            logger.info(f"Tool registered: {name} -> {route_prefix}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register tool {name}: {e}")
            self.tools[name] = {
                'name': name,
                'status': 'failed',
                'error': str(e),
                'registration_time': datetime.utcnow()
            }
            return False
    
    def get_tool_status(self, name: str) -> Dict:
        """Get status of a specific tool"""
        if name not in self.tools:
            return {'status': 'not_found'}
        
        tool = self.tools[name]
        health = self.health_status.get(name, {})
        
        return {
            'name': name,
            'status': tool.get('status', 'unknown'),
            'description': tool.get('description', ''),
            'route_prefix': tool.get('route_prefix', ''),
            'health': health.get('status', 'unknown'),
            'last_health_check': health.get('last_check'),
            'usage_count': tool.get('usage_count', 0),
            'error_count': tool.get('error_count', 0),
            'last_used': tool.get('last_used')
        }
    
    def check_tool_health(self, name: str) -> bool:
        """Check health of a specific tool"""
        if name not in self.tools:
            return False
            
        tool = self.tools[name]
        try:
            # Run custom health check if available
            if tool.get('health_check_func'):
                result = tool['health_check_func']()
                status = 'healthy' if result else 'unhealthy'
            else:
                # Basic health check - verify module is importable
                if tool.get('module'):
                    status = 'healthy'
                else:
                    status = 'unhealthy'
            
            self.health_status[name] = {
                'status': status,
                'last_check': datetime.utcnow().isoformat()
            }
            
            return status == 'healthy'
            
        except Exception as e:
            logger.error(f"Health check failed for {name}: {e}")
            self.health_status[name] = {
                'status': 'error',
                'last_check': datetime.utcnow().isoformat(),
                'error': str(e)
            }
            return False
    
    def check_all_tools_health(self) -> Dict:
        """Check health of all registered tools"""
        results = {}
        
        for name in self.tools.keys():
            results[name] = self.check_tool_health(name)
        
        self.last_health_check = datetime.utcnow()
        return results
    
    def get_registry_status(self) -> Dict:
        """Get complete registry status"""
        total_tools = len(self.tools)
        healthy_tools = sum(1 for status in self.health_status.values() 
                          if status.get('status') == 'healthy')
        
        return {
            'registry_status': 'operational',
            'total_tools': total_tools,
            'healthy_tools': healthy_tools,
            'health_percentage': (healthy_tools / total_tools * 100) if total_tools > 0 else 0,
            'initialization_time': self.initialization_time.isoformat(),
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'tools': {name: self.get_tool_status(name) for name in self.tools.keys()}
        }

# Global registry instance
tools_registry = ToolsRegistry()

def tool_endpoint(tool_name: str):
    """Decorator to track tool usage and errors"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Update usage tracking
                if tool_name in tools_registry.tools:
                    tools_registry.tools[tool_name]['usage_count'] += 1
                    tools_registry.tools[tool_name]['last_used'] = datetime.utcnow()
                
                # Execute the function
                result = func(*args, **kwargs)
                
                # Log performance
                execution_time = (time.time() - start_time) * 1000
                logger.info(f"Tool {tool_name} executed in {execution_time:.1f}ms")
                
                return result
                
            except Exception as e:
                # Update error tracking
                if tool_name in tools_registry.tools:
                    tools_registry.tools[tool_name]['error_count'] += 1
                
                logger.error(f"Tool {tool_name} error: {e}")
                logger.error(traceback.format_exc())
                
                return jsonify({
                    'success': False,
                    'error': f'Tool {tool_name} encountered an error',
                    'details': str(e)
                }), 500
        
        return wrapper
    return decorator

# Create tools blueprint for centralized routes
tools_bp = Blueprint('tools', __name__, url_prefix='/tools')

@tools_bp.route('/status')
def tools_status():
    """Comprehensive tools status endpoint"""
    try:
        # Check all tools health
        health_results = tools_registry.check_all_tools_health()
        
        # Get registry status
        registry_status = tools_registry.get_registry_status()
        
        # Add external service status
        external_services = check_external_services()
        
        return jsonify({
            'success': True,
            'timestamp': datetime.utcnow().isoformat(),
            'registry': registry_status,
            'external_services': external_services,
            'health_summary': {
                'all_systems_operational': all(health_results.values()) and external_services['all_healthy'],
                'tools_healthy': sum(health_results.values()),
                'tools_total': len(health_results),
                'external_services_healthy': sum(1 for s in external_services['services'].values() if s['status'] == 'healthy')
            }
        })
        
    except Exception as e:
        logger.error(f"Tools status check failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Status check failed',
            'details': str(e)
        }), 500

def check_external_services() -> Dict:
    """Check status of external services (Redis, async workers, databases)"""
    services = {}
    
    # Check database connectivity
    try:
        from app import db
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        services['database'] = {'status': 'healthy', 'type': 'postgresql'}
    except Exception as e:
        services['database'] = {'status': 'unhealthy', 'error': str(e), 'type': 'postgresql'}
    
    # Check Redis (if available)
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        services['redis'] = {'status': 'healthy', 'type': 'cache'}
    except Exception:
        services['redis'] = {'status': 'not_available', 'type': 'cache'}
    
    # Check Yahoo Finance API
    try:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        if info and info.get('symbol'):
            services['yahoo_finance'] = {'status': 'healthy', 'type': 'data_source'}
        else:
            services['yahoo_finance'] = {'status': 'degraded', 'type': 'data_source'}
    except Exception as e:
        services['yahoo_finance'] = {'status': 'unhealthy', 'error': str(e), 'type': 'data_source'}
    
    # Check async workers
    try:
        from async_task_queue import task_queue
        stats = task_queue.get_queue_stats()
        if stats['queue_running'] and stats['active_workers'] > 0:
            services['async_workers'] = {
                'status': 'healthy', 
                'type': 'background_processing',
                'active_workers': stats['active_workers'],
                'queue_length': stats['queue_length']
            }
        else:
            services['async_workers'] = {'status': 'unhealthy', 'type': 'background_processing'}
    except Exception as e:
        services['async_workers'] = {'status': 'error', 'error': str(e), 'type': 'background_processing'}
    
    all_healthy = all(s['status'] == 'healthy' for s in services.values() 
                     if s['status'] not in ['not_available', 'not_implemented'])
    
    return {
        'services': services,
        'all_healthy': all_healthy,
        'check_time': datetime.utcnow().isoformat()
    }

def initialize_tools_registry():
    """Initialize all tools in the registry"""
    logger.info("Initializing centralized tools registry...")
    
    # Register core AI tools
    tools_registry.register_tool(
        name="ai_insights",
        module_path="ai_insights", 
        description="Core AI insights and analysis engine",
        route_prefix="/tools/ai/insights"
    )
    
    tools_registry.register_tool(
        name="ai_capability_enhancer",
        module_path="ai_capability_enhancer",
        description="Advanced AI capability enhancement",
        route_prefix="/tools/ai/enhanced"
    )
    
    # Register search tools
    tools_registry.register_tool(
        name="advanced_search",
        module_path="advanced_search_engine",
        description="Advanced search and autocomplete",
        route_prefix="/tools/search/advanced"
    )
    
    tools_registry.register_tool(
        name="symbol_mapper",
        module_path="symbol_mapper",
        description="Company name to symbol mapping",
        route_prefix="/tools/search/symbols"
    )
    
    # Register market data tools
    tools_registry.register_tool(
        name="market_data_collector",
        module_path="market_data_collector",
        description="Real-time market data collection",
        route_prefix="/tools/market/data"
    )
    
    tools_registry.register_tool(
        name="intelligent_stock_analyzer",
        module_path="intelligent_stock_analyzer",
        description="Intelligent stock analysis",
        route_prefix="/tools/analysis/stocks"
    )
    
    # Register premium features
    tools_registry.register_tool(
        name="premium_features",
        module_path="premium_features",
        description="Premium subscription features",
        route_prefix="/tools/premium/features"
    )
    
    tools_registry.register_tool(
        name="enhanced_premium_features",
        module_path="enhanced_premium_features", 
        description="Enhanced premium capabilities",
        route_prefix="/tools/premium/enhanced"
    )
    
    # Register alert and notification tools
    tools_registry.register_tool(
        name="smart_event_alerts",
        module_path="smart_event_alerts",
        description="Smart event detection and alerts",
        route_prefix="/tools/alerts/smart"
    )
    
    # Register utility tools
    tools_registry.register_tool(
        name="performance_monitor",
        module_path="performance_monitor",
        description="Performance monitoring and optimization",
        route_prefix="/tools/system/performance"
    )
    
    # Run initial health check
    health_results = tools_registry.check_all_tools_health()
    
    healthy_count = sum(health_results.values())
    total_count = len(health_results)
    
    logger.info(f"Tools registry initialized: {healthy_count}/{total_count} tools healthy")
    
    return tools_registry

@tools_bp.route('/worker-status')
def worker_status():
    """Get comprehensive worker health and status"""
    try:
        from async_task_queue import task_queue
        
        stats = task_queue.get_queue_stats()
        return jsonify({
            'success': True,
            'worker_health': {
                'queue_running': stats['queue_running'],
                'redis_enabled': stats['redis_enabled'],
                'redis_connected': stats['redis_connected'],
                'total_workers': stats['worker_count'],
                'active_workers': stats['active_workers'],
                'healthy_workers': stats['healthy_workers']
            },
            'queue_status': {
                'pending_tasks': stats['task_counts']['pending'],
                'processing_tasks': stats['task_counts']['processing'],
                'queue_length': stats['queue_length']
            },
            'performance_metrics': {
                'average_processing_time_ms': stats['performance']['average_processing_time_ms'],
                'success_rate_percent': stats['performance']['success_rate'],
                'total_completed': stats['task_counts']['completed'],
                'total_failed': stats['task_counts']['failed']
            },
            'worker_details': stats['worker_stats'],
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting worker status: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get worker status',
            'details': str(e)
        }), 500

@tools_bp.route('/task-status/<task_id>')
def task_status(task_id: str):
    """Get status of a specific task"""
    try:
        from async_task_queue import task_queue
        
        status = task_queue.get_task_status(task_id)
        
        if 'error' in status:
            return jsonify({
                'success': False,
                'task_id': task_id,
                'error': status['error'],
                'details': status.get('details', '')
            }), 404
        
        return jsonify({
            'success': True,
            'task_status': status,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting task status for {task_id}: {e}")
        return jsonify({
            'success': False,
            'task_id': task_id,
            'error': 'Failed to get task status',
            'details': str(e)
        }), 500