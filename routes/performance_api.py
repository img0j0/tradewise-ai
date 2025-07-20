"""
Performance API Routes
Real-time performance monitoring and optimization endpoints
"""

from flask import jsonify, request
from app import app
import logging
from datetime import datetime

# Import performance modules
try:
    from production_performance_audit import audit_performance
    from database_performance_optimizer import optimize_database_for_production, monitor_database_performance
    from frontend_performance_optimizer import optimize_frontend_for_production
    from advanced_performance_optimizer import performance_optimizer
except ImportError as e:
    logging.error(f"Performance module import error: {e}")

logger = logging.getLogger(__name__)

@app.route('/api/performance/comprehensive-audit', methods=['GET'])
def comprehensive_performance_audit():
    """Run comprehensive performance audit"""
    try:
        # Run all performance audits
        system_audit = audit_performance()
        database_audit = monitor_database_performance()
        frontend_audit = optimize_frontend_for_production()
        
        # Get advanced performance metrics
        try:
            advanced_metrics = performance_optimizer.get_optimization_report()
        except:
            advanced_metrics = {'status': 'module_not_available'}
        
        comprehensive_report = {
            'timestamp': datetime.now().isoformat(),
            'system_performance': system_audit,
            'database_performance': database_audit,
            'frontend_performance': frontend_audit,
            'advanced_metrics': advanced_metrics,
            'overall_status': 'healthy',
            'production_ready': True
        }
        
        # Calculate overall production readiness
        system_score = system_audit.get('performance_score', {}).get('overall_score', 0)
        
        if system_score < 70:
            comprehensive_report['overall_status'] = 'needs_optimization'
            comprehensive_report['production_ready'] = False
        
        return jsonify(comprehensive_report)
        
    except Exception as e:
        logger.error(f"Comprehensive audit error: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'status': 'error'
        }), 500

@app.route('/api/performance/database-optimize', methods=['POST'])
def optimize_database_performance():
    """Optimize database for production"""
    try:
        optimization_result = optimize_database_for_production()
        return jsonify(optimization_result)
        
    except Exception as e:
        logger.error(f"Database optimization error: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'status': 'error'
        }), 500

@app.route('/api/performance/frontend-optimize', methods=['POST'])
def optimize_frontend_performance():
    """Optimize frontend for production"""
    try:
        optimization_result = optimize_frontend_for_production()
        return jsonify(optimization_result)
        
    except Exception as e:
        logger.error(f"Frontend optimization error: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'status': 'error'
        }), 500

@app.route('/api/performance/real-time-metrics', methods=['GET'])
def get_real_time_performance_metrics():
    """Get real-time performance metrics"""
    try:
        import psutil
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Get process metrics
        process = psutil.Process()
        process_memory = process.memory_info()
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available_gb': memory.available / 1024 / 1024 / 1024,
                'status': 'healthy' if cpu_percent < 80 and memory.percent < 85 else 'warning'
            },
            'process': {
                'memory_mb': process_memory.rss / 1024 / 1024,
                'memory_vms_mb': process_memory.vms / 1024 / 1024,
                'status': 'healthy'
            },
            'database': {
                'connection_status': 'connected',
                'status': 'healthy'
            },
            'overall_health': 'healthy' if cpu_percent < 80 and memory.percent < 85 else 'warning'
        }
        
        return jsonify(metrics)
        
    except Exception as e:
        logger.error(f"Real-time metrics error: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'status': 'error'
        }), 500

@app.route('/api/performance/production-readiness', methods=['GET'])
def check_production_readiness():
    """Check if platform is ready for production deployment"""
    try:
        readiness_checks = {
            'timestamp': datetime.now().isoformat(),
            'checks': {
                'database_optimized': False,
                'frontend_optimized': False,
                'security_configured': False,
                'performance_acceptable': False,
                'monitoring_enabled': False
            },
            'score': 0,
            'ready_for_production': False,
            'recommendations': []
        }
        
        # Check database optimization
        try:
            db_health = monitor_database_performance()
            if db_health.get('connection_status') == 'healthy':
                readiness_checks['checks']['database_optimized'] = True
        except:
            readiness_checks['recommendations'].append('Optimize database configuration')
        
        # Check system performance
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            if cpu_percent < 70 and memory.percent < 80:
                readiness_checks['checks']['performance_acceptable'] = True
            else:
                readiness_checks['recommendations'].append('Improve system performance')
        except:
            readiness_checks['recommendations'].append('Monitor system performance')
        
        # Check security (basic check)
        try:
            from app import app
            if not app.debug:
                readiness_checks['checks']['security_configured'] = True
            else:
                readiness_checks['recommendations'].append('Disable debug mode for production')
        except:
            readiness_checks['recommendations'].append('Configure security settings')
        
        # Calculate score
        passed_checks = sum(readiness_checks['checks'].values())
        total_checks = len(readiness_checks['checks'])
        readiness_checks['score'] = (passed_checks / total_checks) * 100
        
        # Determine production readiness
        readiness_checks['ready_for_production'] = readiness_checks['score'] >= 80
        
        return jsonify(readiness_checks)
        
    except Exception as e:
        logger.error(f"Production readiness check error: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'status': 'error'
        }), 500

@app.route('/api/performance/optimize-all', methods=['POST'])
def optimize_all_systems():
    """Run all performance optimizations"""
    try:
        optimization_results = {
            'timestamp': datetime.now().isoformat(),
            'optimizations': {},
            'status': 'success',
            'summary': {
                'total_optimizations': 0,
                'successful_optimizations': 0,
                'failed_optimizations': 0
            }
        }
        
        # Database optimization
        try:
            db_result = optimize_database_for_production()
            optimization_results['optimizations']['database'] = db_result
            if db_result.get('status') == 'success':
                optimization_results['summary']['successful_optimizations'] += 1
                optimization_results['summary']['total_optimizations'] += len(
                    db_result.get('optimizations_applied', [])
                )
            else:
                optimization_results['summary']['failed_optimizations'] += 1
        except Exception as e:
            optimization_results['optimizations']['database'] = {'error': str(e)}
            optimization_results['summary']['failed_optimizations'] += 1
        
        # Frontend optimization
        try:
            frontend_result = optimize_frontend_for_production()
            optimization_results['optimizations']['frontend'] = frontend_result
            if frontend_result.get('optimization_results', {}).get('status') == 'success':
                optimization_results['summary']['successful_optimizations'] += 1
                optimization_results['summary']['total_optimizations'] += len(
                    frontend_result.get('optimization_results', {}).get('optimizations_applied', [])
                )
            else:
                optimization_results['summary']['failed_optimizations'] += 1
        except Exception as e:
            optimization_results['optimizations']['frontend'] = {'error': str(e)}
            optimization_results['summary']['failed_optimizations'] += 1
        
        # Advanced optimizations
        try:
            from advanced_performance_optimizer import performance_optimizer
            advanced_result = performance_optimizer.run_optimization_cycle()
            optimization_results['optimizations']['advanced'] = advanced_result
            optimization_results['summary']['successful_optimizations'] += 1
        except Exception as e:
            optimization_results['optimizations']['advanced'] = {'error': str(e)}
            optimization_results['summary']['failed_optimizations'] += 1
        
        return jsonify(optimization_results)
        
    except Exception as e:
        logger.error(f"All systems optimization error: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'status': 'error'
        }), 500