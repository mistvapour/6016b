#!/bin/bash

# MIL-STD-6016 微服务部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
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

# 检查依赖
check_dependencies() {
    log_info "检查部署依赖..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    # 检查kubectl（如果使用Kubernetes）
    if [ "$1" = "k8s" ]; then
        if ! command -v kubectl &> /dev/null; then
            log_error "kubectl未安装，请先安装kubectl"
            exit 1
        fi
    fi
    
    log_success "依赖检查完成"
}

# 构建镜像
build_images() {
    log_info "构建微服务镜像..."
    
    # 构建API网关
    log_info "构建API网关镜像..."
    docker build -t milstd6016/api-gateway:latest ./api-gateway/
    
    # 构建PDF服务
    log_info "构建PDF服务镜像..."
    docker build -t milstd6016/pdf-service:latest ./pdf-service/
    
    # 构建语义服务
    log_info "构建语义服务镜像..."
    docker build -t milstd6016/semantic-service:latest ./semantic-service/
    
    # 构建CDM服务
    log_info "构建CDM服务镜像..."
    docker build -t milstd6016/cdm-service:latest ./cdm-service/
    
    # 构建导入服务
    log_info "构建导入服务镜像..."
    docker build -t milstd6016/import-service:latest ./import-service/
    
    # 构建用户服务
    log_info "构建用户服务镜像..."
    docker build -t milstd6016/user-service:latest ./user-service/
    
    # 构建配置服务
    log_info "构建配置服务镜像..."
    docker build -t milstd6016/config-service:latest ./config-service/
    
    # 构建监控服务
    log_info "构建监控服务镜像..."
    docker build -t milstd6016/monitor-service:latest ./monitor-service/
    
    # 构建存储服务
    log_info "构建存储服务镜像..."
    docker build -t milstd6016/storage-service:latest ./storage-service/
    
    log_success "镜像构建完成"
}

# Docker Compose部署
deploy_docker_compose() {
    log_info "使用Docker Compose部署微服务..."
    
    # 创建网络
    docker network create milstd6016-network 2>/dev/null || true
    
    # 启动服务
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    check_services_docker_compose
    
    log_success "Docker Compose部署完成"
}

# Kubernetes部署
deploy_kubernetes() {
    log_info "使用Kubernetes部署微服务..."
    
    # 创建命名空间
    kubectl apply -f k8s/namespace.yaml
    
    # 部署基础设施
    log_info "部署基础设施服务..."
    kubectl apply -f k8s/mysql.yaml
    kubectl apply -f k8s/redis.yaml
    
    # 等待基础设施就绪
    log_info "等待基础设施就绪..."
    kubectl wait --for=condition=ready pod -l app=mysql -n milstd6016 --timeout=300s
    kubectl wait --for=condition=ready pod -l app=redis -n milstd6016 --timeout=300s
    
    # 部署微服务
    log_info "部署微服务..."
    kubectl apply -f k8s/api-gateway.yaml
    kubectl apply -f k8s/pdf-service.yaml
    # 添加其他服务的部署...
    
    # 等待服务就绪
    log_info "等待微服务就绪..."
    kubectl wait --for=condition=ready pod -l app=api-gateway -n milstd6016 --timeout=300s
    kubectl wait --for=condition=ready pod -l app=pdf-service -n milstd6016 --timeout=300s
    
    # 检查服务状态
    check_services_kubernetes
    
    log_success "Kubernetes部署完成"
}

# 检查Docker Compose服务状态
check_services_docker_compose() {
    log_info "检查服务状态..."
    
    services=("api-gateway" "pdf-service" "semantic-service" "cdm-service" "import-service")
    
    for service in "${services[@]}"; do
        if docker-compose ps | grep -q "$service.*Up"; then
            log_success "$service 服务运行正常"
        else
            log_error "$service 服务运行异常"
        fi
    done
}

# 检查Kubernetes服务状态
check_services_kubernetes() {
    log_info "检查服务状态..."
    
    # 检查Pod状态
    kubectl get pods -n milstd6016
    
    # 检查服务状态
    kubectl get services -n milstd6016
    
    # 检查Ingress状态
    kubectl get ingress -n milstd6016
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查API网关
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "API网关健康检查通过"
    else
        log_error "API网关健康检查失败"
    fi
    
    # 检查PDF服务
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        log_success "PDF服务健康检查通过"
    else
        log_error "PDF服务健康检查失败"
    fi
    
    # 检查其他服务...
}

# 清理资源
cleanup() {
    log_info "清理资源..."
    
    if [ "$1" = "k8s" ]; then
        # 清理Kubernetes资源
        kubectl delete namespace milstd6016
    else
        # 清理Docker Compose资源
        docker-compose down -v
        docker network rm milstd6016-network 2>/dev/null || true
    fi
    
    log_success "资源清理完成"
}

# 显示帮助信息
show_help() {
    echo "MIL-STD-6016 微服务部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  docker-compose    使用Docker Compose部署"
    echo "  k8s              使用Kubernetes部署"
    echo "  build            只构建镜像"
    echo "  health           执行健康检查"
    echo "  cleanup          清理资源"
    echo "  help             显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 docker-compose    # 使用Docker Compose部署"
    echo "  $0 k8s              # 使用Kubernetes部署"
    echo "  $0 build            # 只构建镜像"
    echo "  $0 health           # 执行健康检查"
    echo "  $0 cleanup docker-compose  # 清理Docker Compose资源"
}

# 主函数
main() {
    case "${1:-help}" in
        "docker-compose")
            check_dependencies
            build_images
            deploy_docker_compose
            health_check
            ;;
        "k8s")
            check_dependencies k8s
            build_images
            deploy_kubernetes
            health_check
            ;;
        "build")
            check_dependencies
            build_images
            ;;
        "health")
            health_check
            ;;
        "cleanup")
            cleanup "$2"
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@"
