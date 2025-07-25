#!/bin/bash
# TradeWise AI Scaling Script
# Manual scaling and autoscaling management

set -e

# Configuration
NAMESPACE="tradewise-ai"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Show current scaling status
show_status() {
    log_info "Current TradeWise AI scaling status:"
    echo
    
    # Show deployments
    echo "=== DEPLOYMENTS ==="
    kubectl get deployments -n $NAMESPACE -o wide
    echo
    
    # Show HPA status
    echo "=== HORIZONTAL POD AUTOSCALERS ==="
    kubectl get hpa -n $NAMESPACE
    echo
    
    # Show pods
    echo "=== PODS ==="
    kubectl get pods -n $NAMESPACE -o wide
    echo
    
    # Show resource usage
    echo "=== RESOURCE USAGE ==="
    kubectl top pods -n $NAMESPACE --sort-by=cpu 2>/dev/null || log_warning "Metrics server not available"
    echo
}

# Scale API deployment
scale_api() {
    local replicas=$1
    
    if [[ ! $replicas =~ ^[0-9]+$ ]] || [ $replicas -lt 1 ] || [ $replicas -gt 50 ]; then
        log_error "Invalid replica count. Must be between 1 and 50"
        exit 1
    fi
    
    log_info "Scaling API deployment to $replicas replicas..."
    kubectl scale deployment tradewise-api-deployment --replicas=$replicas -n $NAMESPACE
    
    # Wait for scaling to complete
    kubectl rollout status deployment/tradewise-api-deployment -n $NAMESPACE --timeout=300s
    
    log_success "API deployment scaled to $replicas replicas"
}

# Scale worker deployment
scale_workers() {
    local replicas=$1
    
    if [[ ! $replicas =~ ^[0-9]+$ ]] || [ $replicas -lt 0 ] || [ $replicas -gt 20 ]; then
        log_error "Invalid replica count. Must be between 0 and 20"
        exit 1
    fi
    
    log_info "Scaling worker deployment to $replicas replicas..."
    kubectl scale deployment tradewise-worker-deployment --replicas=$replicas -n $NAMESPACE
    
    # Wait for scaling to complete
    kubectl rollout status deployment/tradewise-worker-deployment -n $NAMESPACE --timeout=300s
    
    log_success "Worker deployment scaled to $replicas replicas"
}

# Enable autoscaling
enable_autoscaling() {
    log_info "Enabling autoscaling..."
    
    # Check if HPA exists, if not apply it
    if ! kubectl get hpa tradewise-api-hpa -n $NAMESPACE &> /dev/null; then
        log_info "Creating HPA for API..."
        kubectl apply -f k8s/hpa.yaml
    fi
    
    # Verify HPA status
    kubectl get hpa -n $NAMESPACE
    
    log_success "Autoscaling enabled"
}

# Disable autoscaling
disable_autoscaling() {
    log_warning "Disabling autoscaling..."
    
    # Delete HPA resources
    kubectl delete hpa --all -n $NAMESPACE
    
    log_success "Autoscaling disabled"
}

# Load test helper
load_test() {
    local duration=${1:-"60s"}
    local requests_per_second=${2:-"10"}
    local endpoint=${3:-"/api/health"}
    
    log_info "Starting load test..."
    log_info "Duration: $duration"
    log_info "RPS: $requests_per_second"
    log_info "Endpoint: $endpoint"
    
    # Get service URL
    kubectl port-forward -n $NAMESPACE service/tradewise-api-service 8080:80 &
    PF_PID=$!
    
    sleep 3
    
    # Check if hey is available
    if command -v hey &> /dev/null; then
        hey -z $duration -q $requests_per_second http://localhost:8080$endpoint
    elif command -v ab &> /dev/null; then
        # Calculate total requests for ab
        duration_seconds=$(echo $duration | sed 's/s$//')
        total_requests=$((duration_seconds * requests_per_second))
        ab -n $total_requests -c 10 http://localhost:8080$endpoint
    else
        log_warning "No load testing tool found (hey or ab). Running simple curl test..."
        for i in {1..10}; do
            curl -s http://localhost:8080$endpoint > /dev/null
            echo "Request $i completed"
            sleep 1
        done
    fi
    
    # Clean up port forward
    kill $PF_PID 2>/dev/null || true
    
    log_success "Load test completed"
}

# Monitor scaling behavior
monitor_scaling() {
    local duration=${1:-"300"}  # 5 minutes default
    
    log_info "Monitoring scaling behavior for $duration seconds..."
    log_info "Press Ctrl+C to stop monitoring"
    
    # Monitor loop
    end_time=$((SECONDS + duration))
    
    while [ $SECONDS -lt $end_time ]; do
        clear
        echo "=== TRADEWISE AI SCALING MONITOR ==="
        echo "Monitoring for $((end_time - SECONDS)) more seconds"
        echo
        
        # Show current time
        echo "Time: $(date)"
        echo
        
        # Show HPA status
        echo "=== AUTOSCALER STATUS ==="
        kubectl get hpa -n $NAMESPACE 2>/dev/null || echo "No HPA configured"
        echo
        
        # Show pods
        echo "=== ACTIVE PODS ==="
        kubectl get pods -n $NAMESPACE -o wide --sort-by=.metadata.creationTimestamp
        echo
        
        # Show resource usage
        echo "=== RESOURCE USAGE ==="
        kubectl top pods -n $NAMESPACE --sort-by=cpu 2>/dev/null || echo "Metrics server not available"
        echo
        
        # Show recent events
        echo "=== RECENT EVENTS ==="
        kubectl get events -n $NAMESPACE --sort-by=.metadata.creationTimestamp | tail -5
        
        sleep 10
    done
    
    log_success "Monitoring completed"
}

# Performance test with scaling
performance_test() {
    log_info "Running performance test with scaling simulation..."
    
    # Start with minimum replicas
    scale_api 2
    scale_workers 1
    
    # Enable autoscaling
    enable_autoscaling
    
    # Monitor initial state
    log_info "Initial state (30 seconds):"
    monitor_scaling 30
    
    # Run moderate load test
    log_info "Starting moderate load test..."
    load_test "120s" "5" "/api/stock-analysis?symbol=AAPL" &
    LOAD_PID=$!
    
    # Monitor during load
    monitor_scaling 120
    
    # Wait for load test to complete
    wait $LOAD_PID
    
    # Run high load test
    log_info "Starting high load test..."
    load_test "180s" "15" "/api/stock-analysis?symbol=TSLA" &
    LOAD_PID=$!
    
    # Monitor during high load
    monitor_scaling 180
    
    # Wait for load test to complete
    wait $LOAD_PID
    
    # Cool down period
    log_info "Cool down period (120 seconds):"
    monitor_scaling 120
    
    log_success "Performance test completed"
}

# Emergency scale down
emergency_scale_down() {
    log_warning "EMERGENCY SCALE DOWN - Reducing all replicas to minimum"
    
    # Disable autoscaling first
    disable_autoscaling
    
    # Scale down to minimum
    scale_api 1
    scale_workers 0
    
    log_success "Emergency scale down completed"
}

# Scale up for high traffic
scale_for_traffic() {
    local traffic_level=$1
    
    case $traffic_level in
        "low")
            log_info "Scaling for low traffic..."
            scale_api 2
            scale_workers 1
            ;;
        "medium")
            log_info "Scaling for medium traffic..."
            scale_api 5
            scale_workers 2
            ;;
        "high")
            log_info "Scaling for high traffic..."
            scale_api 10
            scale_workers 4
            ;;
        "peak")
            log_info "Scaling for peak traffic..."
            scale_api 15
            scale_workers 6
            ;;
        *)
            log_error "Invalid traffic level: $traffic_level"
            echo "Valid levels: low, medium, high, peak"
            exit 1
            ;;
    esac
    
    # Enable autoscaling after manual scaling
    enable_autoscaling
}

# Show help
show_help() {
    echo "TradeWise AI Scaling Script"
    echo
    echo "Usage: $0 <command> [options]"
    echo
    echo "Commands:"
    echo "  status                          Show current scaling status"
    echo "  scale-api <replicas>           Scale API deployment (1-50)"
    echo "  scale-workers <replicas>       Scale worker deployment (0-20)"
    echo "  enable-autoscaling             Enable horizontal pod autoscaling"
    echo "  disable-autoscaling            Disable autoscaling"
    echo "  load-test [duration] [rps] [endpoint]  Run load test"
    echo "  monitor [seconds]              Monitor scaling behavior"
    echo "  performance-test               Run comprehensive performance test"
    echo "  traffic <level>                Scale for traffic level (low|medium|high|peak)"
    echo "  emergency-down                 Emergency scale down to minimum"
    echo "  help                           Show this help"
    echo
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 scale-api 5"
    echo "  $0 scale-workers 3"
    echo "  $0 load-test 60s 10 /api/health"
    echo "  $0 traffic high"
    echo "  $0 monitor 300"
}

# Main function
main() {
    local command=$1
    
    case $command in
        "status")
            show_status
            ;;
        "scale-api")
            scale_api $2
            ;;
        "scale-workers")
            scale_workers $2
            ;;
        "enable-autoscaling")
            enable_autoscaling
            ;;
        "disable-autoscaling")
            disable_autoscaling
            ;;
        "load-test")
            load_test $2 $3 $4
            ;;
        "monitor")
            monitor_scaling $2
            ;;
        "performance-test")
            performance_test
            ;;
        "traffic")
            scale_for_traffic $2
            ;;
        "emergency-down")
            emergency_scale_down
            ;;
        "help"|"--help"|"-h"|"")
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Handle interrupts
trap 'log_error "Operation interrupted"; exit 1' INT TERM

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    log_error "kubectl is required but not installed"
    exit 1
fi

# Run main function
main "$@"