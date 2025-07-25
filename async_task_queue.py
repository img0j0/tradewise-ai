"""
Asynchronous Task Queue for TradeWise AI
Handles background AI analysis processing with task status tracking
"""

import uuid
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
from app import cache
from ai_insights import AIInsightsEngine
from simple_personalization import SimplePersonalization
from external_api_optimizer import yahoo_optimizer
from performance_monitor import performance_optimized

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

class AsyncTaskQueue:
    """Simple async task queue for AI analysis processing"""
    
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.tasks: Dict[str, AnalysisTask] = {}
        self.task_queue = []
        self.worker_threads = []
        self.is_running = False
        self.ai_engine = AIInsightsEngine()
        self.personalization = SimplePersonalization()
        
    def start_workers(self):
        """Start background worker threads"""
        if self.is_running:
            return
            
        self.is_running = True
        
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"AIWorker-{i+1}",
                daemon=True
            )
            worker.start()
            self.worker_threads.append(worker)
            
        logger.info(f"Started {self.max_workers} async task workers")
    
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
        
        self.tasks[task_id] = task
        self.task_queue.append(task_id)
        
        # Cache task for retrieval
        cache.set(f"task:{task_id}", task, timeout=3600)  # 1 hour
        
        logger.info(f"Submitted analysis task {task_id} for {symbol}")
        return task_id
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the current status of a task"""
        # Try memory first
        if task_id in self.tasks:
            task = self.tasks[task_id]
        else:
            # Try cache
            task = cache.get(f"task:{task_id}")
            if not task:
                return {'error': 'Task not found', 'task_id': task_id}
        
        status_data = {
            'task_id': task.task_id,
            'symbol': task.symbol,
            'strategy': task.strategy,
            'status': task.status.value,
            'created_at': task.created_at.isoformat(),
            'queue_position': self._get_queue_position(task_id) if task.status == TaskStatus.PENDING else None
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
            return self.task_queue.index(task_id) + 1
        except ValueError:
            return 0
    
    def _worker_loop(self):
        """Main worker loop for processing tasks"""
        worker_name = threading.current_thread().name
        logger.info(f"{worker_name} started")
        
        while self.is_running:
            try:
                # Get next task from queue
                task_id = self._get_next_task()
                
                if not task_id:
                    time.sleep(1)  # No tasks, wait
                    continue
                
                # Process the task
                self._process_task(task_id, worker_name)
                
            except Exception as e:
                logger.error(f"Error in {worker_name}: {e}")
                time.sleep(1)
        
        logger.info(f"{worker_name} stopped")
    
    def _get_next_task(self) -> Optional[str]:
        """Get next task from queue"""
        if not self.task_queue:
            return None
            
        task_id = self.task_queue.pop(0)
        
        # Verify task still exists and is pending
        if task_id in self.tasks and self.tasks[task_id].status == TaskStatus.PENDING:
            return task_id
            
        return None
    
    @performance_optimized()
    def _process_task(self, task_id: str, worker_name: str):
        """Process a single analysis task"""
        try:
            task = self.tasks[task_id]
            task.status = TaskStatus.PROCESSING
            task.started_at = datetime.now()
            
            logger.info(f"{worker_name} processing {task.symbol} analysis")
            
            # Update cache
            cache.set(f"task:{task_id}", task, timeout=3600)
            
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
            
            # Update task cache
            cache.set(f"task:{task_id}", task, timeout=3600)
            
            processing_time = (task.completed_at - task.started_at).total_seconds() * 1000
            logger.info(f"{worker_name} completed {task.symbol} in {processing_time:.2f}ms")
            
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {e}")
            
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.error = str(e)
            
            # Update cache
            cache.set(f"task:{task_id}", task, timeout=3600)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get task queue statistics"""
        pending_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])
        processing_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.PROCESSING])
        completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])
        
        return {
            'queue_running': self.is_running,
            'worker_count': len(self.worker_threads),
            'active_workers': len([t for t in self.worker_threads if t.is_alive()]),
            'queue_length': len(self.task_queue),
            'task_counts': {
                'pending': pending_tasks,
                'processing': processing_tasks,
                'completed': completed_tasks,
                'failed': failed_tasks,
                'total': len(self.tasks)
            },
            'performance': {
                'average_processing_time_ms': self._calculate_avg_processing_time(),
                'success_rate': self._calculate_success_rate()
            }
        }
    
    def _calculate_avg_processing_time(self) -> float:
        """Calculate average processing time for completed tasks"""
        completed_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED and t.started_at and t.completed_at]
        
        if not completed_tasks:
            return 0.0
            
        total_time = sum(
            (t.completed_at - t.started_at).total_seconds() * 1000 
            for t in completed_tasks
        )
        
        return total_time / len(completed_tasks)
    
    def _calculate_success_rate(self) -> float:
        """Calculate task success rate"""
        total_finished = len([t for t in self.tasks.values() if t.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]])
        
        if total_finished == 0:
            return 100.0
            
        completed = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
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

# Global task queue instance
task_queue = AsyncTaskQueue(max_workers=3)