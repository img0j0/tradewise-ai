"""
Tool Error Wrapper for TradeWise AI
Provides consistent error handling for all tool operations
"""

import logging
import traceback
from functools import wraps
from typing import Dict, Any, Optional, Callable
from flask import jsonify
from error_handler import TradeWiseError, ERROR_MESSAGES

logger = logging.getLogger(__name__)

def tool_error_handler(tool_name: str, operation: str = "operation"):
    """
    Decorator for wrapping tool operations with comprehensive error handling
    
    Args:
        tool_name: Name of the tool for logging purposes
        operation: Description of the operation being performed
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Dict[str, Any]:
            try:
                logger.info(f"Starting {tool_name} {operation}")
                result = func(*args, **kwargs)
                logger.info(f"Completed {tool_name} {operation} successfully")
                return {
                    'status': 'success',
                    'data': result,
                    'tool': tool_name,
                    'operation': operation
                }
                
            except TradeWiseError as e:
                # Handle known TradeWise errors
                logger.error(f"{tool_name} {operation} failed: {e.error_type} - {e.details}")
                return {
                    'status': 'failed',
                    'error': e.get_error_response()['error'],
                    'tool': tool_name,
                    'operation': operation
                }
                
            except ValueError as e:
                # Handle validation errors
                logger.error(f"{tool_name} validation error: {str(e)}")
                return {
                    'status': 'failed',
                    'error': {
                        'code': 'INPUT_001',
                        'message': 'Invalid input provided',
                        'action': 'Please check your input and try again',
                        'details': str(e),
                        'tool': tool_name
                    }
                }
                
            except ConnectionError as e:
                # Handle connection errors
                logger.error(f"{tool_name} connection error: {str(e)}")
                return {
                    'status': 'failed',
                    'error': {
                        'code': 'API_003',
                        'message': 'External API request failed',
                        'action': 'Please try again later',
                        'details': str(e),
                        'tool': tool_name
                    }
                }
                
            except Exception as e:
                # Handle unexpected errors
                logger.error(f"{tool_name} unexpected error: {str(e)}")
                logger.error(traceback.format_exc())
                return {
                    'status': 'failed',
                    'error': {
                        'code': 'SYS_001',
                        'message': 'An unexpected error occurred',
                        'action': 'Please try again later or contact support',
                        'details': str(e),
                        'tool': tool_name,
                        'stack_trace': traceback.format_exc()
                    }
                }
        
        return wrapper
    return decorator

def api_tool_handler(tool_name: str, api_name: str = "API"):
    """
    Specialized decorator for API-based tool operations
    
    Args:
        tool_name: Name of the tool
        api_name: Name of the external API being used
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Dict[str, Any]:
            try:
                logger.info(f"Starting {tool_name} API call to {api_name}")
                result = func(*args, **kwargs)
                logger.info(f"Completed {tool_name} API call successfully")
                return {
                    'status': 'success',
                    'data': result,
                    'tool': tool_name,
                    'api': api_name
                }
                
            except Exception as e:
                error_message = str(e).lower()
                
                # API-specific error handling
                if 'timeout' in error_message:
                    error_response = {
                        'code': 'API_003',
                        'message': f'{api_name} request timed out',
                        'action': 'Please try again later'
                    }
                elif 'rate limit' in error_message or '429' in error_message:
                    error_response = {
                        'code': 'API_002',
                        'message': f'{api_name} rate limit exceeded',
                        'action': 'Please try again in a few minutes'
                    }
                elif 'unauthorized' in error_message or '401' in error_message:
                    error_response = {
                        'code': 'API_001',
                        'message': f'{api_name} authentication failed',
                        'action': 'Please check your API key configuration'
                    }
                elif 'not found' in error_message or '404' in error_message:
                    error_response = {
                        'code': 'DATA_001',
                        'message': 'Requested data not found',
                        'action': 'Please verify the symbol or try a different search'
                    }
                else:
                    error_response = {
                        'code': 'API_003',
                        'message': f'{api_name} request failed',
                        'action': 'Please try again later'
                    }
                
                error_response.update({
                    'details': str(e),
                    'tool': tool_name,
                    'api': api_name
                })
                
                logger.error(f"{tool_name} API error: {error_response['message']} - {str(e)}")
                
                return {
                    'status': 'failed',
                    'error': error_response
                }
        
        return wrapper
    return decorator

def database_tool_handler(tool_name: str):
    """
    Specialized decorator for database operations
    
    Args:
        tool_name: Name of the tool performing database operations
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Dict[str, Any]:
            try:
                logger.info(f"Starting {tool_name} database operation")
                result = func(*args, **kwargs)
                logger.info(f"Completed {tool_name} database operation successfully")
                return {
                    'status': 'success',
                    'data': result,
                    'tool': tool_name,
                    'operation': 'database'
                }
                
            except Exception as e:
                error_message = str(e).lower()
                
                # Database-specific error handling
                if 'connection' in error_message:
                    error_response = {
                        'code': 'DB_001',
                        'message': 'Database connection failed',
                        'action': 'Please try again later'
                    }
                elif 'constraint' in error_message:
                    error_response = {
                        'code': 'DB_002',
                        'message': 'Data constraint violation',
                        'action': 'Please check your input data'
                    }
                else:
                    error_response = {
                        'code': 'DB_001',
                        'message': 'Database operation failed',
                        'action': 'Please try again later'
                    }
                
                error_response.update({
                    'details': str(e),
                    'tool': tool_name
                })
                
                logger.error(f"{tool_name} database error: {error_response['message']} - {str(e)}")
                
                return {
                    'status': 'failed',
                    'error': error_response
                }
        
        return wrapper
    return decorator

def safe_json_response(data: Dict[str, Any], status_code: int = 200):
    """
    Create a safe JSON response with proper error handling
    
    Args:
        data: Response data
        status_code: HTTP status code
    """
    try:
        return jsonify(data), status_code
    except Exception as e:
        logger.error(f"JSON serialization error: {str(e)}")
        error_response = {
            'status': 'failed',
            'error': {
                'code': 'SYS_002',
                'message': 'Response serialization failed',
                'action': 'Please try again or contact support',
                'details': str(e)
            }
        }
        return jsonify(error_response), 500

# Pre-configured decorators for common tools
stock_analysis_handler = tool_error_handler("Stock Analysis", "analysis")
search_handler = tool_error_handler("Search Engine", "search")
market_data_handler = api_tool_handler("Market Data", "Yahoo Finance")
premium_feature_handler = tool_error_handler("Premium Features", "premium_operation")
alert_handler = tool_error_handler("Smart Alerts", "alert_operation")