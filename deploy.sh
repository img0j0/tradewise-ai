#!/bin/bash
# TradeWise AI Deployment Script
# Builds and deploys the application to Kubernetes

set -e

# Configuration
REGISTRY="your-registry.com"
NAMESPACE="tradewise-ai"
VERSION=${1:-"latest"}
CONTEXT=${2:-"production"}

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

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    commands=("docker" "kubectl" "helm")
    for cmd in "${commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            log_error "$cmd is required but not installed"
            exit 1
        fi
    done
    
    log_success "All dependencies found"
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    # Build main API image
    log_info "Building API image..."
    docker build -t ${REGISTRY}/tradewise-ai:${VERSION} -f Dockerfile .
    
    # Build worker image
    log_info "Building Worker image..."
    docker build -t ${REGISTRY}/tradewise-ai-worker:${VERSION} -f Dockerfile.worker .
    
    log_success "Docker images built successfully"
}

# Push images to registry
push_images() {
    log_info "Pushing images to registry..."
    
    docker push ${REGISTRY}/tradewise-ai:${VERSION}
    docker push ${REGISTRY}/tradewise-ai-worker:${VERSION}
    
    log_success "Images pushed to registry"
}

# Create namespace if it doesn't exist
create_namespace() {
    log_info "Creating namespace if needed..."
    
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        kubectl apply -f k8s/namespace.yaml
        log_success "Namespace $NAMESPACE created"
    else
        log_info "Namespace $NAMESPACE already exists"
    fi
}

# Deploy secrets (if they don't exist)
deploy_secrets() {
    log_info "Deploying secrets..."
    
    if ! kubectl get secret tradewise-secrets -n $NAMESPACE &> /dev/null; then
        log_warning "Secrets not found. Please update k8s/secrets.yaml with actual values"
        read -p "Continue with example secrets? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_error "Deployment aborted. Please configure secrets first."
            exit 1
        fi
    fi
    
    kubectl apply -f k8s/secrets.yaml
    log_success "Secrets deployed"
}

# Deploy infrastructure (PVs, ConfigMaps, etc.)
deploy_infrastructure() {
    log_info "Deploying infrastructure..."
    
    kubectl apply -f k8s/persistent-volumes.yaml
    kubectl apply -f k8s/configmap.yaml
    
    log_success "Infrastructure deployed"
}

# Deploy database
deploy_database() {
    log_info "Deploying PostgreSQL database..."
    
    kubectl apply -f k8s/postgres-deployment.yaml
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/postgres-deployment -n $NAMESPACE
    
    log_success "Database deployed and ready"
}

# Deploy Redis cache
deploy_redis() {
    log_info "Deploying Redis cache..."
    
    kubectl apply -f k8s/redis-deployment.yaml
    
    # Wait for Redis to be ready
    log_info "Waiting for Redis to be ready..."
    kubectl wait --for=condition=available --timeout=120s deployment/redis-deployment -n $NAMESPACE
    
    log_success "Redis deployed and ready"
}

# Deploy application
deploy_application() {
    log_info "Deploying TradeWise AI application..."
    
    # Update image tags in deployment
    sed -i.bak "s|tradewise-ai:latest|${REGISTRY}/tradewise-ai:${VERSION}|g" k8s/api-deployment.yaml
    sed -i.bak "s|tradewise-ai-worker:latest|${REGISTRY}/tradewise-ai-worker:${VERSION}|g" k8s/worker-deployment.yaml
    
    kubectl apply -f k8s/api-deployment.yaml
    kubectl apply -f k8s/worker-deployment.yaml
    
    # Restore original files
    mv k8s/api-deployment.yaml.bak k8s/api-deployment.yaml
    mv k8s/worker-deployment.yaml.bak k8s/worker-deployment.yaml
    
    # Wait for API deployment
    log_info "Waiting for API deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/tradewise-api-deployment -n $NAMESPACE
    
    log_success "Application deployed and ready"
}

# Deploy autoscaling
deploy_autoscaling() {
    log_info "Deploying autoscaling configuration..."
    
    kubectl apply -f k8s/hpa.yaml
    
    log_success "Autoscaling deployed"
}

# Deploy ingress
deploy_ingress() {
    log_info "Deploying ingress..."
    
    kubectl apply -f k8s/ingress.yaml
    
    log_success "Ingress deployed"
}

# Deploy monitoring
deploy_monitoring() {
    log_info "Deploying monitoring (optional)..."
    
    if kubectl api-resources | grep -q servicemonitors; then
        kubectl apply -f k8s/monitoring.yaml
        log_success "Monitoring deployed"
    else
        log_warning "Prometheus operator not found, skipping monitoring deployment"
    fi
}

# Initialize database
initialize_database() {
    log_info "Initializing database..."
    
    # Get a pod name
    POD_NAME=$(kubectl get pods -n $NAMESPACE -l app=tradewise-api -o jsonpath='{.items[0].metadata.name}')
    
    if [ -n "$POD_NAME" ]; then
        kubectl exec -n $NAMESPACE $POD_NAME -- python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"
        log_success "Database initialized"
    else
        log_warning "No API pod found, database initialization skipped"
    fi
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check pod status
    kubectl get pods -n $NAMESPACE
    
    # Check services
    kubectl get services -n $NAMESPACE
    
    # Get ingress info
    kubectl get ingress -n $NAMESPACE
    
    # Test health endpoint
    log_info "Testing health endpoint..."
    
    # Port forward for testing
    kubectl port-forward -n $NAMESPACE service/tradewise-api-service 8080:80 &
    PF_PID=$!
    
    sleep 5
    
    if curl -f http://localhost:8080/api/health &> /dev/null; then
        log_success "Health check passed"
    else
        log_warning "Health check failed"
    fi
    
    kill $PF_PID 2>/dev/null || true
}

# Rollback function
rollback() {
    log_warning "Rolling back to previous version..."
    
    kubectl rollout undo deployment/tradewise-api-deployment -n $NAMESPACE
    kubectl rollout undo deployment/tradewise-worker-deployment -n $NAMESPACE
    
    log_success "Rollback completed"
}

# Main deployment function
main() {
    log_info "Starting TradeWise AI deployment to $CONTEXT..."
    log_info "Registry: $REGISTRY"
    log_info "Version: $VERSION"
    log_info "Namespace: $NAMESPACE"
    
    check_dependencies
    
    case $CONTEXT in
        "build-only")
            build_images
            ;;
        "push-only")
            push_images
            ;;
        "local")
            log_info "Local deployment using docker-compose..."
            docker-compose down
            docker-compose build
            docker-compose up -d
            log_success "Local deployment completed"
            ;;
        "production"|"staging")
            build_images
            push_images
            create_namespace
            deploy_secrets
            deploy_infrastructure
            deploy_database
            deploy_redis
            deploy_application
            deploy_autoscaling
            deploy_ingress
            deploy_monitoring
            initialize_database
            verify_deployment
            ;;
        "rollback")
            rollback
            ;;
        *)
            log_error "Unknown context: $CONTEXT"
            echo "Usage: $0 [version] [context]"
            echo "Contexts: local, production, staging, build-only, push-only, rollback"
            exit 1
            ;;
    esac
    
    log_success "Deployment completed successfully!"
}

# Handle interrupts
trap 'log_error "Deployment interrupted"; exit 1' INT TERM

# Run main function
main "$@"