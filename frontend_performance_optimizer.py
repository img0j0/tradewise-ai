#!/usr/bin/env python3
"""
Frontend Performance Optimizer
Optimize frontend assets and delivery for production
"""

import os
import gzip
import mimetypes
import hashlib
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FrontendPerformanceOptimizer:
    def __init__(self):
        self.static_dir = 'static'
        self.optimizations_applied = []
        
    def optimize_static_assets(self):
        """Comprehensive static asset optimization"""
        optimizations = []
        
        try:
            # 1. Compress CSS and JS files
            compression_results = self._compress_assets()
            optimizations.extend(compression_results)
            
            # 2. Generate cache headers
            cache_optimization = self._optimize_caching()
            optimizations.extend(cache_optimization)
            
            # 3. Analyze asset sizes
            size_analysis = self._analyze_asset_sizes()
            optimizations.append({
                'category': 'analysis',
                'optimization': 'Asset size analysis completed',
                'details': size_analysis
            })
            
            # 4. Generate performance recommendations
            recommendations = self._generate_frontend_recommendations()
            optimizations.append({
                'category': 'recommendations',
                'optimization': 'Performance recommendations generated',
                'details': recommendations
            })
            
            return {
                'optimizations_applied': optimizations,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Frontend optimization error: {e}")
            return {
                'optimizations_applied': [],
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _compress_assets(self):
        """Compress CSS and JS files with gzip"""
        optimizations = []
        
        if not os.path.exists(self.static_dir):
            return optimizations
        
        compressible_extensions = ['.css', '.js', '.json', '.svg']
        total_original_size = 0
        total_compressed_size = 0
        files_compressed = 0
        
        for root, dirs, files in os.walk(self.static_dir):
            for file in files:
                filepath = os.path.join(root, file)
                _, ext = os.path.splitext(file)
                
                if ext.lower() in compressible_extensions:
                    try:
                        # Read original file
                        with open(filepath, 'rb') as f:
                            original_data = f.read()
                        
                        original_size = len(original_data)
                        total_original_size += original_size
                        
                        # Create compressed version
                        compressed_path = filepath + '.gz'
                        with gzip.open(compressed_path, 'wb') as f:
                            f.write(original_data)
                        
                        compressed_size = os.path.getsize(compressed_path)
                        total_compressed_size += compressed_size
                        files_compressed += 1
                        
                        compression_ratio = (1 - compressed_size / original_size) * 100
                        
                        optimizations.append({
                            'category': 'compression',
                            'optimization': f'Compressed {file}',
                            'details': {
                                'original_size': original_size,
                                'compressed_size': compressed_size,
                                'compression_ratio': f"{compression_ratio:.1f}%"
                            }
                        })
                        
                    except Exception as e:
                        logger.error(f"Compression error for {filepath}: {e}")
        
        if files_compressed > 0:
            overall_compression = (1 - total_compressed_size / total_original_size) * 100
            optimizations.append({
                'category': 'compression_summary',
                'optimization': 'Asset compression completed',
                'details': {
                    'files_compressed': files_compressed,
                    'total_original_size': total_original_size,
                    'total_compressed_size': total_compressed_size,
                    'overall_compression_ratio': f"{overall_compression:.1f}%",
                    'bytes_saved': total_original_size - total_compressed_size
                }
            })
        
        return optimizations
    
    def _optimize_caching(self):
        """Generate caching optimization recommendations"""
        optimizations = []
        
        # Cache headers configuration
        cache_config = {
            'static_assets': {
                'max_age': 31536000,  # 1 year for static assets
                'headers': {
                    'Cache-Control': 'public, max-age=31536000, immutable',
                    'Expires': 'Thu, 31 Dec 2037 23:55:55 GMT'
                }
            },
            'html_pages': {
                'max_age': 3600,  # 1 hour for HTML
                'headers': {
                    'Cache-Control': 'public, max-age=3600',
                    'ETag': 'generate_etag'
                }
            },
            'api_responses': {
                'max_age': 300,  # 5 minutes for API
                'headers': {
                    'Cache-Control': 'public, max-age=300',
                    'Vary': 'Accept-Encoding'
                }
            }
        }
        
        optimizations.append({
            'category': 'caching',
            'optimization': 'Cache headers configuration',
            'details': cache_config
        })
        
        return optimizations
    
    def _analyze_asset_sizes(self):
        """Analyze static asset sizes and identify optimization opportunities"""
        analysis = {
            'total_size': 0,
            'file_count': 0,
            'size_by_type': {},
            'large_files': [],
            'optimization_opportunities': []
        }
        
        if not os.path.exists(self.static_dir):
            return analysis
        
        large_file_threshold = 100 * 1024  # 100KB
        
        for root, dirs, files in os.walk(self.static_dir):
            for file in files:
                filepath = os.path.join(root, file)
                _, ext = os.path.splitext(file)
                
                try:
                    size = os.path.getsize(filepath)
                    analysis['total_size'] += size
                    analysis['file_count'] += 1
                    
                    # Track by file type
                    if ext not in analysis['size_by_type']:
                        analysis['size_by_type'][ext] = {'count': 0, 'total_size': 0}
                    
                    analysis['size_by_type'][ext]['count'] += 1
                    analysis['size_by_type'][ext]['total_size'] += size
                    
                    # Identify large files
                    if size > large_file_threshold:
                        analysis['large_files'].append({
                            'file': file,
                            'path': filepath,
                            'size': size,
                            'size_mb': size / 1024 / 1024
                        })
                
                except Exception as e:
                    logger.error(f"Size analysis error for {filepath}: {e}")
        
        # Generate optimization opportunities
        if analysis['large_files']:
            analysis['optimization_opportunities'].append(
                f"Found {len(analysis['large_files'])} large files that could be optimized"
            )
        
        if analysis['total_size'] > 5 * 1024 * 1024:  # 5MB
            analysis['optimization_opportunities'].append(
                "Total asset size is large - consider implementing CDN"
            )
        
        # Convert total size to MB for readability
        analysis['total_size_mb'] = analysis['total_size'] / 1024 / 1024
        
        return analysis
    
    def _generate_frontend_recommendations(self):
        """Generate specific frontend performance recommendations"""
        recommendations = {
            'immediate': [],
            'short_term': [],
            'long_term': []
        }
        
        # Immediate optimizations
        recommendations['immediate'].extend([
            'Enable gzip compression for all text assets',
            'Set appropriate cache headers for static assets',
            'Minify CSS and JavaScript files',
            'Optimize image file sizes and formats'
        ])
        
        # Short-term optimizations
        recommendations['short_term'].extend([
            'Implement lazy loading for images and charts',
            'Bundle and concatenate JavaScript files',
            'Use CSS sprites for small icons',
            'Implement service worker for offline functionality'
        ])
        
        # Long-term optimizations
        recommendations['long_term'].extend([
            'Implement Content Delivery Network (CDN)',
            'Use HTTP/2 server push for critical resources',
            'Implement Progressive Web App (PWA) features',
            'Consider server-side rendering for initial load'
        ])
        
        return recommendations
    
    def create_flask_optimization_middleware(self):
        """Create Flask middleware for production optimizations"""
        middleware_code = '''
# Flask Performance Middleware
# Add this to your main Flask application

from flask import Flask, request, make_response, g
import gzip
import io
import time
from functools import wraps

def create_performance_middleware(app):
    """Apply performance optimizations to Flask app"""
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        # Add performance headers
        if hasattr(g, 'start_time'):
            response.headers['X-Response-Time'] = str(time.time() - g.start_time)
        
        # Enable compression for text responses
        if (response.content_type.startswith('text/') or 
            response.content_type.startswith('application/json') or
            response.content_type.startswith('application/javascript')):
            
            accept_encoding = request.headers.get('Accept-Encoding', '')
            if 'gzip' in accept_encoding.lower():
                response.direct_passthrough = False
                
                if response.status_code < 200 or response.status_code >= 300:
                    return response
                
                gzip_buffer = io.BytesIO()
                with gzip.GzipFile(fileobj=gzip_buffer, mode='wb') as gzip_file:
                    gzip_file.write(response.get_data())
                
                response.set_data(gzip_buffer.getvalue())
                response.headers['Content-Encoding'] = 'gzip'
                response.headers['Content-Length'] = len(response.get_data())
        
        # Add caching headers for static assets
        if request.endpoint == 'static':
            response.headers['Cache-Control'] = 'public, max-age=31536000'
            response.headers['Expires'] = 'Thu, 31 Dec 2037 23:55:55 GMT'
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    return app

# Usage: create_performance_middleware(app)
'''
        
        with open('flask_performance_middleware.py', 'w') as f:
            f.write(middleware_code)
        
        return {
            'category': 'middleware',
            'optimization': 'Flask performance middleware created',
            'details': {
                'file': 'flask_performance_middleware.py',
                'features': [
                    'Response time tracking',
                    'Automatic gzip compression',
                    'Cache headers for static assets',
                    'Security headers'
                ]
            }
        }
    
    def generate_performance_report(self):
        """Generate comprehensive frontend performance report"""
        optimization_results = self.optimize_static_assets()
        middleware_creation = self.create_flask_optimization_middleware()
        
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'optimization_results': optimization_results,
            'middleware_created': middleware_creation,
            'production_checklist': self._generate_production_checklist(),
            'performance_score': self._calculate_frontend_score(optimization_results)
        }
        
        return report
    
    def _generate_production_checklist(self):
        """Generate production readiness checklist"""
        return {
            'asset_optimization': [
                'CSS and JS files minified',
                'Images optimized and compressed',
                'Gzip compression enabled',
                'Cache headers configured'
            ],
            'performance': [
                'Lazy loading implemented',
                'Critical CSS inlined',
                'Non-critical JS deferred',
                'CDN configured for static assets'
            ],
            'monitoring': [
                'Performance monitoring enabled',
                'Error tracking configured',
                'Analytics implemented',
                'Uptime monitoring active'
            ]
        }
    
    def _calculate_frontend_score(self, optimization_results):
        """Calculate frontend performance score"""
        optimizations = optimization_results.get('optimizations_applied', [])
        
        # Count different types of optimizations
        compression_optimizations = len([o for o in optimizations if o.get('category') == 'compression'])
        caching_optimizations = len([o for o in optimizations if o.get('category') == 'caching'])
        
        # Calculate score based on optimizations applied
        score = 0
        if compression_optimizations > 0:
            score += 40
        if caching_optimizations > 0:
            score += 30
        if len(optimizations) > 5:
            score += 20
        
        # Add bonus for comprehensive optimization
        if len(optimizations) > 10:
            score += 10
        
        return {
            'score': min(100, score),
            'grade': 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'D',
            'optimizations_count': len(optimizations)
        }

# Global optimizer instance
frontend_optimizer = FrontendPerformanceOptimizer()

def optimize_frontend_for_production():
    """Optimize frontend for production deployment"""
    return frontend_optimizer.generate_performance_report()

if __name__ == "__main__":
    # Run frontend optimization
    report = optimize_frontend_for_production()
    print("Frontend Optimization Report:")
    print("=" * 50)
    print(json.dumps(report, indent=2, default=str))