#!/bin/bash

# PDF处理系统部署脚本
# 支持开发、测试、生产环境部署

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
    log_info "检查系统依赖..."
    
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
    
    # 检查Python（用于本地开发）
    if ! command -v python3 &> /dev/null; then
        log_warning "Python3未安装，将无法进行本地开发"
    fi
    
    # 检查Node.js（用于本地开发）
    if ! command -v node &> /dev/null; then
        log_warning "Node.js未安装，将无法进行本地开发"
    fi
    
    log_success "依赖检查完成"
}

# 创建环境配置文件
create_env_file() {
    log_info "创建环境配置文件..."
    
    if [ ! -f .env ]; then
        cat > .env << EOF
# 数据库配置
DB_ROOT_PASSWORD=rootpassword
DB_USER=milstd6016
DB_PASSWORD=milstd6016
DB_NAME=milstd6016

# 应用配置
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
MAX_WORKERS=4

# 安全配置
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# 文件配置
MAX_FILE_SIZE=50
UPLOAD_DIR=uploads
OUTPUT_DIR=output
LOG_DIR=logs
EOF
        log_success "环境配置文件已创建"
    else
        log_info "环境配置文件已存在"
    fi
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p uploads output logs ssl
    chmod 755 uploads output logs ssl
    
    log_success "目录创建完成"
}

# 构建Docker镜像
build_images() {
    log_info "构建Docker镜像..."
    
    docker-compose build --no-cache
    
    log_success "Docker镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    check_services
    
    log_success "服务启动完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    # 检查数据库
    if docker-compose exec mysql mysqladmin ping -h localhost --silent; then
        log_success "数据库服务正常"
    else
        log_error "数据库服务异常"
        exit 1
    fi
    
    # 检查后端API
    if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
        log_success "后端API服务正常"
    else
        log_error "后端API服务异常"
        exit 1
    fi
    
    # 检查前端
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_success "前端服务正常"
    else
        log_error "前端服务异常"
        exit 1
    fi
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    
    # 等待数据库启动
    sleep 10
    
    # 运行数据库初始化脚本
    if [ -f init.sql ]; then
        docker-compose exec -T mysql mysql -u root -p${DB_ROOT_PASSWORD:-rootpassword} ${DB_NAME:-milstd6016} < init.sql
        log_success "数据库初始化完成"
    else
        log_warning "未找到数据库初始化脚本 init.sql"
    fi
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    docker-compose down
    
    log_success "服务已停止"
}

# 清理资源
cleanup() {
    log_info "清理资源..."
    
    docker-compose down -v
    docker system prune -f
    
    log_success "资源清理完成"
}

# 查看日志
view_logs() {
    local service=${1:-""}
    
    if [ -n "$service" ]; then
        docker-compose logs -f "$service"
    else
        docker-compose logs -f
    fi
}

# 备份数据
backup_data() {
    local backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
    
    log_info "备份数据到 $backup_dir..."
    
    mkdir -p "$backup_dir"
    
    # 备份数据库
    docker-compose exec mysql mysqldump -u root -p${DB_ROOT_PASSWORD:-rootpassword} ${DB_NAME:-milstd6016} > "$backup_dir/database.sql"
    
    # 备份上传文件
    if [ -d uploads ]; then
        cp -r uploads "$backup_dir/"
    fi
    
    # 备份输出文件
    if [ -d output ]; then
        cp -r output "$backup_dir/"
    fi
    
    # 备份日志
    if [ -d logs ]; then
        cp -r logs "$backup_dir/"
    fi
    
    log_success "数据备份完成: $backup_dir"
}

# 恢复数据
restore_data() {
    local backup_dir=${1:-""}
    
    if [ -z "$backup_dir" ]; then
        log_error "请指定备份目录"
        exit 1
    fi
    
    if [ ! -d "$backup_dir" ]; then
        log_error "备份目录不存在: $backup_dir"
        exit 1
    fi
    
    log_info "从 $backup_dir 恢复数据..."
    
    # 恢复数据库
    if [ -f "$backup_dir/database.sql" ]; then
        docker-compose exec -T mysql mysql -u root -p${DB_ROOT_PASSWORD:-rootpassword} ${DB_NAME:-milstd6016} < "$backup_dir/database.sql"
        log_success "数据库恢复完成"
    fi
    
    # 恢复文件
    if [ -d "$backup_dir/uploads" ]; then
        cp -r "$backup_dir/uploads" ./
        log_success "上传文件恢复完成"
    fi
    
    if [ -d "$backup_dir/output" ]; then
        cp -r "$backup_dir/output" ./
        log_success "输出文件恢复完成"
    fi
    
    if [ -d "$backup_dir/logs" ]; then
        cp -r "$backup_dir/logs" ./
        log_success "日志文件恢复完成"
    fi
    
    log_success "数据恢复完成"
}

# 显示帮助信息
show_help() {
    cat << EOF
PDF处理系统部署脚本

用法: $0 [命令] [选项]

命令:
    deploy          完整部署（默认）
    start           启动服务
    stop            停止服务
    restart         重启服务
    status          查看服务状态
    logs [service]  查看日志
    backup          备份数据
    restore <dir>   恢复数据
    cleanup         清理资源
    help            显示帮助信息

选项:
    --env <env>     指定环境 (development|testing|production)
    --no-build      不重新构建镜像
    --no-init       不初始化数据库

示例:
    $0 deploy                    # 完整部署
    $0 start --no-build          # 启动服务（不重新构建）
    $0 logs backend              # 查看后端日志
    $0 backup                    # 备份数据
    $0 restore backup_20240101_120000  # 恢复数据

EOF
}

# 主函数
main() {
    local command=${1:-"deploy"}
    local env="production"
    local no_build=false
    local no_init=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --env)
                env="$2"
                shift 2
                ;;
            --no-build)
                no_build=true
                shift
                ;;
            --no-init)
                no_init=true
                shift
                ;;
            *)
                break
                ;;
        esac
    done
    
    # 设置环境变量
    export ENVIRONMENT="$env"
    
    case $command in
        deploy)
            log_info "开始部署PDF处理系统..."
            check_dependencies
            create_env_file
            create_directories
            if [ "$no_build" = false ]; then
                build_images
            fi
            start_services
            if [ "$no_init" = false ]; then
                init_database
            fi
            log_success "部署完成！"
            log_info "访问地址: http://localhost"
            log_info "API文档: http://localhost/api/docs"
            ;;
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            start_services
            ;;
        status)
            check_services
            ;;
        logs)
            view_logs "$2"
            ;;
        backup)
            backup_data
            ;;
        restore)
            restore_data "$2"
            ;;
        cleanup)
            cleanup
            ;;
        help)
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
