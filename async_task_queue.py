"""
Asynchronous Task Queue for TradeWise AI
Redis-based task queue with fallback to in-memory processing
Handles background AI analysis processing with comprehensive status tracking
"""

import uuid
import time
import threading
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
import json
import traceback

# Redis imports with fallback
try:
    import redis
    import pickle
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app import cache
from ai_insights import AIInsightsEngine
from simple_personalization import SimplePersonalization
from external_api_optimizer import yahoo_optimizer
from performance_monitor import performance_optimized
from error_handler import TradeWiseError, handle_redis_error

# Setup worker-specific logging
worker_logger = logging.getLogger('worker')
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AnalysisTask:
    task_id: str
    symbol: str
    strategy: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict] = None
    error: Optional[str] = None

class RedisTaskQueue:
    """Redis-based task queue with fallback to in-memory processing"""
    
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.worker_threads = []
        self.is_running = False
        self.ai_engine = AIInsightsEngine()
        self.personalization = SimplePersonalization()
        
        # Redis configuration with fallback
        self.redis_client = None
        self.use_redis = False
        self._setup_redis()
        
        # Fallback in-memory storage
        self.memory_tasks: Dict[str, AnalysisTask] = {}
        self.memory_queue: List[str] = []
        
        # Worker health tracking
        self.worker_stats = {}
        self.last_heartbeat = {}
        
        # Error handling setup
        self._setup_logging()
    
    def _setup_redis(self):
        """Setup Redis connection with fallback to memory"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, using in-memory fallback")
            return
            
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(redis_url, decode_responses=False)
            
            # Test connection
            self.redis_client.ping()
            self.use_redis = True
            logger.info(f"Connected to Redis: {redis_url}")
            
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory fallback: {e}")
            self.redis_client = None
            self.use_redis = False
    
    def _setup_logging(self):
        """Setup worker logging"""
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Setup worker-specific logging
        worker_logger = logging.getLogger('worker')
        if not worker_logger.handlers:
            handler = logging.FileHandler('logs/worker.log')
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            worker_logger.addHandler(handler)
            worker_logger.setLevel(logging.INFO)
        
    def start_workers(self):
        """Start background worker threads with health monitoring"""
        if self.is_running:
            return
            
        self.is_running = True
        
        for i in range(self.max_workers):
            worker_id = f"worker-{i+1}"
            worker = threading.Thread(
                target=self._worker_loop,
                name=worker_id,
                daemon=True
            )
            worker.start()
            self.worker_threads.append(worker)
            
            # Initialize worker stats
            self.worker_stats[worker_id] = {
                'tasks_processed': 0,
                'errors': 0,
                'start_time': datetime.now(),
                'status': 'running'
            }
            self.last_heartbeat[worker_id] = datetime.now()
            
        logger.info(f"Started {self.max_workers} Redis-backed async task workers (Redis: {self.use_redis})")
    
    def stop_workers(self):
        """Stop all worker threads"""
        self.is_running = False
        logger.info("Stopped async task workers")
    
    def submit_analysis_task(self, symbol: str, strategy: str = 'growth_investor') -> str:
        """Submit a new AI analysis task and return task ID"""
        task_id = str(uuid.uuid4())
        
        task = AnalysisTask(
            task_id=task_id,
            symbol=symbol.upper(),
            strategy=strategy,
            status=TaskStatus.PENDING,
            created_at=datetime.now()
        )
        
        try:
            if self.use_redis and self.redis_client:
                # Store task in Redis
                task_data = pickle.dumps(task)
                self.redis_client.hset("tasks", task_id, task_data)
                self.redis_client.lpush("task_queue", task_id)
                self.redis_client.expire(f"tasks", 3600)  # 1 hour TTL
            else:
                # Fallback to memory
                self.memory_tasks[task_id] = task
                self.memory_queue.append(task_id)
            
            # Also cache in Flask cache for quick access
            cache.set(f"task:{task_id}", task, timeout=3600)
            
            logger.info(f"Submitted analysis task {task_id} for {symbol} (Redis: {self.use_redis})")
            return task_id
            
        except Exception as e:
            logger.error(f"Error submitting task {task_id}: {e}")
            # Fallback to memory even if Redis was supposed to work
            self.memory_tasks[task_id] = task
            self.memory_queue.append(task_id)
            return task_id
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the current status of a task"""
        task = None
        
        try:
            if self.use_redis and self.redis_client:
                # Try Redis first
                task_data = self.redis_client.hget("tasks", task_id)
                if task_data:
                    task = pickle.loads(task_data)
            else:
                # Try memory
                task = self.memory_tasks.get(task_id)
            
            # Fallback to Flask cache
            if not task:
                task = cache.get(f"task:{task_id}")
                
            if not task:
                return {'error': 'Task not found', 'task_id': task_id}
                
        except Exception as e:
            logger.error(f"Error retrieving task {task_id}: {e}")
            return {'error': 'Error retrieving task', 'task_id': task_id, 'details': str(e)}
        
        status_data = {
            'task_id': task.task_id,
            'symbol': task.symbol,
            'strategy': task.strategy,
            'status': task.status.value,
            'created_at': task.created_at.isoformat(),
            'queue_position': self._get_queue_position(task_id) if task.status == TaskStatus.PENDING else None,
            'queue_type': 'redis' if self.use_redis else 'memory'
        }
        
        if task.started_at:
            status_data['started_at'] = task.started_at.isoformat()
            
        if task.completed_at:
            status_data['completed_at'] = task.completed_at.isoformat()
            status_data['processing_time_ms'] = int((task.completed_at - task.started_at).total_seconds() * 1000)
            
        if task.status == TaskStatus.COMPLETED and task.result:
            status_data['result'] = task.result
            
        if task.status == TaskStatus.FAILED and task.error:
            status_data['error'] = task.error
            
        return status_data
    
    def _get_queue_position(self, task_id: str) -> int:
        """Get position of task in queue"""
        try:
            if self.use_redis and self.redis_client:
                queue_items = self.redis_client.lrange("task_queue", 0, -1)
                queue_items = [item.decode() if isinstance(item, bytes) else item for item in queue_items]
                return queue_items.index(task_id) + 1
            else:
                return self.memory_queue.index(task_id) + 1
        except (ValueError, Exception):
            return 0
    
    def _worker_loop(self):
        """Main worker loop for processing tasks with comprehensive error handling"""
        worker_name = threading.current_thread().name
        worker_logger = logging.getLogger('worker')
        worker_logger.info(f"{worker_name} started")
        
        while self.is_running:
            try:
                # Update heartbeat
                self.last_heartbeat[worker_name] = datetime.now()
                
                # Get next task from queue
                task_id = self._get_next_task()
                
                if not task_id:
                    time.sleep(1)  # No tasks, wait
                    continue
                
                # Process the task
                self._process_task(task_id, worker_name)
                
                # Update worker stats
                if worker_name in self.worker_stats:
                    self.worker_stats[worker_name]['tasks_processed'] += 1
                
            except Exception as e:
                worker_logger.error(f"Error in {worker_name}: {e}")
                worker_logger.error(traceback.format_exc())
                
                # Update error stats
                if worker_name in self.worker_stats:
                    self.worker_stats[worker_name]['errors'] += 1
                
                time.sleep(1)
        
        # Update worker status on shutdown
        if worker_name in self.worker_stats:
            self.worker_stats[worker_name]['status'] = 'stopped'
        
        worker_logger.info(f"{worker_name} stopped")
    
    def _get_next_task(self) -> Optional[str]:
        """Get next task from queue (Redis or memory)"""
        try:
            if self.use_redis and self.redis_client:
                # Get from Redis queue (blocking pop with timeout)
                result = self.redis_client.brpop("task_queue", timeout=1)
                if result:
                    task_id = result[1].decode() if isinstance(result[1], bytes) else result[1]
                    return task_id
            else:
                # Get from memory queue
                if not self.memory_queue:
                    return None
                task_id = self.memory_queue.pop(0)
                return task_id
                
        except Exception as e:
            logger.error(f"Error getting next task: {e}")
            
        return None
    
    @performance_optimized()
    def _process_task(self, task_id: str, worker_name: str):
        """Process a single analysis task with comprehensive error handling"""
        worker_logger = logging.getLogger('worker')
        task = None
        
        try:
            # Retrieve task
            if self.use_redis and self.redis_client:
                task_data = self.redis_client.hget("tasks", task_id)
                if task_data:
                    task = pickle.loads(task_data)
            else:
                task = self.memory_tasks.get(task_id)
            
            if not task:
                worker_logger.error(f"Task {task_id} not found for processing")
                return
            
            task.status = TaskStatus.PROCESSING
            task.started_at = datetime.now()
            
            worker_logger.info(f"{worker_name} processing {task.symbol} analysis")
            
            # Update task status
            self._update_task(task_id, task)
            
            # Get stock data
            stock_data = yahoo_optimizer._fetch_single_stock(task.symbol)
            
            if not stock_data:
                raise Exception(f"Could not fetch data for {task.symbol}")
            
            # Generate AI insights
            base_insights = self.ai_engine.get_insights(task.symbol, stock_data)
            
            # Apply strategy personalization
            self.personalization.current_strategy = task.strategy
            personalized_insights = self.personalization.personalize_analysis(task.symbol, base_insights)
            
            # Create comprehensive result
            analysis_result = {
                'success': True,
                'symbol': task.symbol,
                'stock_info': stock_data,
                'analysis': personalized_insights,
                'competitive_features': {
                    'ai_explanations': personalized_insights.get('ai_explanation', {}),
                    'smart_alerts': personalized_insights.get('smart_alerts', []),
                    'educational_insights': personalized_insights.get('educational_insights', {})
                },
                'strategy': task.strategy,
                'async_processed': True,
                'processing_worker': worker_name,
                'completion_time': datetime.now().isoformat()
            }
            
            # Mark task as completed
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = analysis_result
            
            # Cache the result separately for quick access
            result_cache_key = f"async_result:{task.symbol}:{task.strategy}"
            cache.set(result_cache_key, analysis_result, timeout=300)  # 5 minutes
            
            # Update task status
            self._update_task(task_id, task)
            
            processing_time = (task.completed_at - task.started_at).total_seconds() * 1000
            worker_logger.info(f"{worker_name} completed {task.symbol} in {processing_time:.2f}ms")
            
        except Exception as e:
            worker_logger.error(f"Error processing task {task_id}: {e}")
            worker_logger.error(traceback.format_exc())
            
            if task:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()
                task.error = f"{type(e).__name__}: {str(e)}"
                
                # Update task status
                self._update_task(task_id, task)
    
    def _update_task(self, task_id: str, task: AnalysisTask):
        """Update task in storage (Redis or memory)"""
        try:
            if self.use_redis and self.redis_client:
                task_data = pickle.dumps(task)
                self.redis_client.hset("tasks", task_id, task_data)
            else:
                self.memory_tasks[task_id] = task
            
            # Also update Flask cache
            cache.set(f"task:{task_id}", task, timeout=3600)
            
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get comprehensive task queue statistics"""
        all_tasks = self._get_all_tasks()
        
        pending_tasks = len([t for t in all_tasks if t.status == TaskStatus.PENDING])
        processing_tasks = len([t for t in all_tasks if t.status == TaskStatus.PROCESSING])
        completed_tasks = len([t for t in all_tasks if t.status == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in all_tasks if t.status == TaskStatus.FAILED])
        
        # Get queue length
        try:
            if self.use_redis and self.redis_client:
                queue_length = self.redis_client.llen("task_queue")
            else:
                queue_length = len(self.memory_queue)
        except:
            queue_length = 0
        
        # Worker health info
        healthy_workers = 0
        for worker_id, last_beat in self.last_heartbeat.items():
            if (datetime.now() - last_beat).seconds < 30:  # Healthy if heartbeat within 30s
                healthy_workers += 1
        
        return {
            'queue_running': self.is_running,
            'redis_enabled': self.use_redis,
            'redis_connected': self._check_redis_connection(),
            'worker_count': len(self.worker_threads),
            'active_workers': len([t for t in self.worker_threads if t.is_alive()]),
            'healthy_workers': healthy_workers,
            'queue_length': queue_length,
            'task_counts': {
                'pending': pending_tasks,
                'processing': processing_tasks,
                'completed': completed_tasks,
                'failed': failed_tasks,
                'total': len(all_tasks)
            },
            'performance': {
                'average_processing_time_ms': self._calculate_avg_processing_time(),
                'success_rate': self._calculate_success_rate()
            },
            'worker_stats': self.worker_stats
        }
    
    def _get_all_tasks(self) -> List[AnalysisTask]:
        """Get all tasks from Redis or memory"""
        tasks = []
        try:
            if self.use_redis and self.redis_client:
                task_data = self.redis_client.hgetall("tasks")
                for task_bytes in task_data.values():
                    task = pickle.loads(task_bytes)
                    tasks.append(task)
            else:
                tasks = list(self.memory_tasks.values())
        except Exception as e:
            logger.error(f"Error getting all tasks: {e}")
        
        return tasks
    
    def _check_redis_connection(self) -> bool:
        """Check if Redis connection is healthy"""
        if not self.use_redis or not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def _calculate_avg_processing_time(self) -> float:
        """Calculate average processing time for completed tasks"""
        all_tasks = self._get_all_tasks()
        completed_tasks = [t for t in all_tasks if t.status == TaskStatus.COMPLETED and t.started_at and t.completed_at]
        
        if not completed_tasks:
            return 0.0
            
        total_time = sum(
            (t.completed_at - t.started_at).total_seconds() * 1000 
            for t in completed_tasks
        )
        
        return total_time / len(completed_tasks)
    
    def _calculate_success_rate(self) -> float:
        """Calculate task success rate"""
        all_tasks = self._get_all_tasks()
        total_finished = len([t for t in all_tasks if t.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]])
        
        if total_finished == 0:
            return 100.0
            
        completed = len([t for t in all_tasks if t.status == TaskStatus.COMPLETED])
        return (completed / total_finished) * 100
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Clean up old completed/failed tasks"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        old_task_ids = [
            task_id for task_id, task in self.tasks.items()
            if task.completed_at and task.completed_at < cutoff_time
        ]
        
        for task_id in old_task_ids:
            del self.tasks[task_id]
            # Remove from cache
            cache.delete(f"task:{task_id}")
        
        logger.info(f"Cleaned up {len(old_task_ids)} old tasks")

# Global task queue instance - Redis-enabled
task_queue = RedisTaskQueue(max_workers=int(os.getenv('ASYNC_WORKER_COUNT', 3)))