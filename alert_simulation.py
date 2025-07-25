#!/usr/bin/env python3
"""
Alert simulation script for TradeWise AI
Tests monitoring alerts by simulating various failure conditions
"""

import requests
import time
import threading
import sys
import psutil
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

class AlertSimulator:
    """Simulate various conditions to test monitoring alerts"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level:7} | {message}")
    
    def simulate_high_cpu_load(self, duration: int = 300):
        """Simulate high CPU load for testing CPU alerts"""
        self.log("🔥 Starting CPU load simulation", "ALERT")
        
        def cpu_intensive_task():
            end_time = time.time() + duration
            while time.time() < end_time:
                # CPU intensive calculation
                sum(i * i for i in range(10000))
        
        # Start multiple threads to increase CPU usage
        threads = []
        for _ in range(psutil.cpu_count()):
            thread = threading.Thread(target=cpu_intensive_task)
            thread.start()
            threads.append(thread)
        
        self.log(f"CPU load simulation running for {duration} seconds")
        
        # Monitor CPU usage
        for i in range(duration // 10):
            cpu_percent = psutil.cpu_percent(interval=1)
            self.log(f"Current CPU usage: {cpu_percent:.1f}%", "MONITOR")
            time.sleep(9)
        
        # Wait for threads to finish
        for thread in threads:
            thread.join()
        
        self.log("CPU load simulation completed", "SUCCESS")
    
    def simulate_memory_pressure(self, duration: int = 180):
        """Simulate high memory usage"""
        self.log("💾 Starting memory pressure simulation", "ALERT")
        
        # Allocate large chunks of memory
        memory_chunks = []
        chunk_size = 50 * 1024 * 1024  # 50MB chunks
        
        try:
            for i in range(20):  # Up to 1GB
                chunk = bytearray(chunk_size)
                memory_chunks.append(chunk)
                
                memory_percent = psutil.virtual_memory().percent
                self.log(f"Memory usage: {memory_percent:.1f}%", "MONITOR")
                
                if memory_percent > 85:
                    self.log("High memory usage threshold reached", "WARNING")
                    break
                
                time.sleep(5)
            
            # Hold memory for duration
            self.log(f"Holding memory for {duration} seconds")
            time.sleep(duration)
            
        finally:
            # Clean up memory
            memory_chunks.clear()
            self.log("Memory pressure simulation completed", "SUCCESS")
    
    def simulate_api_errors(self, duration: int = 120):
        """Simulate API error conditions"""
        self.log("❌ Starting API error simulation", "ALERT")
        
        # Create endpoint that returns errors
        error_endpoints = [
            f"{self.base_url}/api/stock-analysis?symbol=INVALID",
            f"{self.base_url}/api/market/nonexistent",
            f"{self.base_url}/api/premium/test-error"
        ]
        
        end_time = time.time() + duration
        error_count = 0
        
        while time.time() < end_time:
            for endpoint in error_endpoints:
                try:
                    response = self.session.get(endpoint, timeout=5)
                    if response.status_code >= 400:
                        error_count += 1
                        self.log(f"Error {response.status_code} from {endpoint}", "ERROR")
                except Exception as e:
                    error_count += 1
                    self.log(f"Request failed: {str(e)[:50]}...", "ERROR")
            
            time.sleep(2)
        
        self.log(f"Generated {error_count} API errors", "SUCCESS")
    
    def simulate_high_latency(self, duration: int = 180):
        """Simulate high response times"""
        self.log("🐌 Starting latency simulation", "ALERT")
        
        # Make requests that should trigger slow responses
        slow_endpoints = [
            f"{self.base_url}/api/stock-analysis?symbol=AAPL&detailed=true",
            f"{self.base_url}/api/market/overview?full=true"
        ]
        
        end_time = time.time() + duration
        latency_measurements = []
        
        while time.time() < end_time:
            for endpoint in slow_endpoints:
                try:
                    start_time = time.time()
                    response = self.session.get(endpoint, timeout=30)
                    latency = (time.time() - start_time) * 1000
                    
                    latency_measurements.append(latency)
                    self.log(f"Response time: {latency:.1f}ms", "MONITOR")
                    
                    if latency > 1000:
                        self.log(f"High latency detected: {latency:.1f}ms", "WARNING")
                
                except Exception as e:
                    self.log(f"Latency test failed: {str(e)[:50]}...", "ERROR")
            
            time.sleep(5)
        
        if latency_measurements:
            avg_latency = sum(latency_measurements) / len(latency_measurements)
            max_latency = max(latency_measurements)
            self.log(f"Avg latency: {avg_latency:.1f}ms, Max: {max_latency:.1f}ms", "SUCCESS")
    
    def simulate_task_queue_backlog(self, duration: int = 150):
        """Simulate task queue backlog"""
        self.log("📚 Starting task queue backlog simulation", "ALERT")
        
        # Submit many async tasks quickly
        task_ids = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            # Submit 60 async tasks rapidly
            for i in range(60):
                future = executor.submit(
                    self.session.post,
                    f"{self.base_url}/api/stock-analysis",
                    json={"symbol": f"TEST{i:02d}", "async": True},
                    timeout=10
                )
                futures.append(future)
                time.sleep(0.1)  # 100ms between submissions
            
            # Collect task IDs
            for future in futures:
                try:
                    response = future.result()
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('task_id'):
                            task_ids.append(data['task_id'])
                except Exception:
                    pass
        
        self.log(f"Submitted {len(task_ids)} tasks to create backlog", "SUCCESS")
        
        # Monitor queue for the duration
        for i in range(duration // 10):
            # Check queue status if endpoint exists
            try:
                response = self.session.get(f"{self.base_url}/api/tasks/status")
                if response.status_code == 200:
                    data = response.json()
                    queue_size = data.get('queue_size', 0)
                    self.log(f"Queue size: {queue_size} tasks", "MONITOR")
                    
                    if queue_size > 50:
                        self.log(f"High queue backlog: {queue_size} tasks", "WARNING")
            except Exception:
                pass
            
            time.sleep(10)
        
        self.log("Task queue simulation completed", "SUCCESS")
    
    def simulate_service_downtime(self, duration: int = 60):
        """Simulate temporary service downtime"""
        self.log("💀 Starting service downtime simulation", "ALERT")
        
        # This would typically involve stopping the service
        # For simulation, we'll just generate failed requests
        end_time = time.time() + duration
        failure_count = 0
        
        while time.time() < end_time:
            try:
                # Try to connect to a non-existent port to simulate downtime
                response = requests.get(
                    "http://localhost:9999/api/health",
                    timeout=5
                )
            except Exception:
                failure_count += 1
                self.log("Service appears down", "ERROR")
            
            time.sleep(5)
        
        self.log(f"Simulated {failure_count} downtime checks", "SUCCESS")
    
    def run_comprehensive_simulation(self):
        """Run all simulation scenarios"""
        self.log("🚨 Starting comprehensive alert simulation", "START")
        
        simulations = [
            ("Service Downtime", self.simulate_service_downtime, 60),
            ("API Errors", self.simulate_api_errors, 120),
            ("High Latency", self.simulate_high_latency, 180),
            ("Task Queue Backlog", self.simulate_task_queue_backlog, 150),
            ("Memory Pressure", self.simulate_memory_pressure, 180),
            ("High CPU Load", self.simulate_high_cpu_load, 300),
        ]
        
        for name, func, duration in simulations:
            self.log(f"▶️  Starting {name} simulation ({duration}s)", "PHASE")
            try:
                func(duration)
                self.log(f"✅ {name} simulation completed", "SUCCESS")
            except Exception as e:
                self.log(f"❌ {name} simulation failed: {str(e)}", "ERROR")
            
            # Brief pause between simulations
            time.sleep(10)
        
        self.log("🎯 All alert simulations completed", "COMPLETE")

def main():
    """Main simulation runner"""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    simulator = AlertSimulator(base_url)
    
    print("TradeWise AI Alert Simulation")
    print("=" * 50)
    print("This script will simulate various conditions to test monitoring alerts:")
    print("- High CPU usage (>80%)")
    print("- High memory usage (>80%)")
    print("- API errors (>5% error rate)")
    print("- High latency (>1000ms)")
    print("- Task queue backlog (>50 tasks)")
    print("- Service downtime")
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        simulator.run_comprehensive_simulation()
    else:
        print("Available simulations:")
        print("1. High CPU Load")
        print("2. Memory Pressure")
        print("3. API Errors")
        print("4. High Latency")
        print("5. Task Queue Backlog")
        print("6. Service Downtime")
        print("7. Run All Simulations")
        
        choice = input("\nSelect simulation (1-7): ").strip()
        
        simulations = {
            "1": ("High CPU Load", simulator.simulate_high_cpu_load, 300),
            "2": ("Memory Pressure", simulator.simulate_memory_pressure, 180),
            "3": ("API Errors", simulator.simulate_api_errors, 120),
            "4": ("High Latency", simulator.simulate_high_latency, 180),
            "5": ("Task Queue Backlog", simulator.simulate_task_queue_backlog, 150),
            "6": ("Service Downtime", simulator.simulate_service_downtime, 60),
            "7": ("All Simulations", simulator.run_comprehensive_simulation, 0),
        }
        
        if choice in simulations:
            name, func, duration = simulations[choice]
            if choice == "7":
                func()
            else:
                print(f"\n🚨 Starting {name} simulation...")
                func(duration)
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()