#!/bin/bash

# OpenAgentFlow 部署脚本

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

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "命令 $1 未找到，请先安装"
        exit 1
    fi
}

# 显示帮助
show_help() {
    echo "OpenAgentFlow 部署脚本"
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  setup          初始设置"
    echo "  build          构建Docker镜像"
    echo "  start          启动服务"
    echo "  stop           停止服务"
    echo "  restart        重启服务"
    echo "  status         查看服务状态"
    echo "  logs           查看服务日志"
    echo "  update         更新代码并重启"
    echo "  backup         备份数据"
    echo "  restore        恢复数据"
    echo "  help           显示此帮助信息"
}

# 初始设置
setup() {
    log_info "开始初始设置..."
    
    # 检查必要命令
    check_command docker
    check_command docker-compose
    
    # 创建必要的目录
    mkdir -p data logs ssl
    
    # 复制环境变量示例文件
    if [ ! -f .env ]; then
        cp .env.example .env
        log_warning "已创建 .env 文件，请编辑配置文件"
    fi
    
    # 设置文件权限
    chmod +x deploy.sh
    
    log_success "初始设置完成"
}

# 构建Docker镜像
build() {
    log_info "开始构建Docker镜像..."
    
    docker-compose build
    
    log_success "Docker镜像构建完成"
}

# 启动服务
start() {
    log_info "启动 OpenAgentFlow 服务..."
    
    # 检查环境文件
    if [ ! -f .env ]; then
        log_error ".env 文件不存在，请先运行 ./deploy.sh setup"
        exit 1
    fi
    
    # 启动服务
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    if check_service_health; then
        log_success "OpenAgentFlow 服务启动成功"
        log_info "访问地址: http://localhost:8000"
        log_info "API文档: http://localhost:8000/docs"
    else
        log_error "服务启动失败，请检查日志"
        docker-compose logs openagentflow
    fi
}

# 停止服务
stop() {
    log_info "停止 OpenAgentFlow 服务..."
    
    docker-compose down
    
    log_success "服务已停止"
}

# 重启服务
restart() {
    log_info "重启 OpenAgentFlow 服务..."
    
    stop
    start
}

# 查看服务状态
status() {
    log_info "服务状态:"
    
    docker-compose ps
    
    echo ""
    log_info "容器状态:"
    docker-compose ps -a
    
    echo ""
    log_info "日志状态:"
    docker-compose logs --tail=10
}

# 查看服务日志
logs() {
    if [ -z "$1" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f $1
    fi
}

# 更新代码并重启
update() {
    log_info "更新代码并重启服务..."
    
    # 停止服务
    stop
    
    # 更新代码（这里假设用户已经拉取了新代码）
    log_info "拉取最新代码..."
    git pull
    
    # 重新构建
    build
    
    # 启动服务
    start
}

# 备份数据
backup() {
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    
    log_info "备份数据到: $backup_dir"
    
    mkdir -p $backup_dir
    
    # 备份数据库
    if docker-compose ps postgres &> /dev/null; then
        log_info "备份PostgreSQL数据库..."
        docker-compose exec -T postgres pg_dump -U openagentflow openagentflow > $backup_dir/database.sql
    fi
    
    # 备份Redis数据
    if [ -d "data/redis" ]; then
        log_info "备份Redis数据..."
        cp -r data/redis $backup_dir/
    fi
    
    # 备份应用数据
    if [ -d "data" ]; then
        log_info "备份应用数据..."
        cp -r data $backup_dir/
    fi
    
    # 备份日志
    if [ -d "logs" ]; then
        log_info "备份日志..."
        cp -r logs $backup_dir/
    fi
    
    # 创建备份摘要
    cat > $backup_dir/backup.info << EOF
备份时间: $(date)
备份目录: $backup_dir
包含内容:
$(ls -la $backup_dir)
EOF
    
    log_success "备份完成: $backup_dir"
}

# 恢复数据
restore() {
    if [ -z "$1" ]; then
        log_error "请指定备份目录"
        echo "用法: $0 restore <备份目录>"
        exit 1
    fi
    
    local backup_dir=$1
    
    if [ ! -d "$backup_dir" ]; then
        log_error "备份目录不存在: $backup_dir"
        exit 1
    fi
    
    log_info "从 $backup_dir 恢复数据..."
    
    # 停止服务
    stop
    
    # 恢复数据库
    if [ -f "$backup_dir/database.sql" ]; then
        log_info "恢复PostgreSQL数据库..."
        docker-compose up -d postgres
        sleep 10
        docker-compose exec -T postgres psql -U openagentflow openagentflow < $backup_dir/database.sql
    fi
    
    # 恢复Redis数据
    if [ -d "$backup_dir/redis" ]; then
        log_info "恢复Redis数据..."
        rm -rf data/redis
        cp -r $backup_dir/redis data/
    fi
    
    # 恢复应用数据
    if [ -d "$backup_dir/data" ]; then
        log_info "恢复应用数据..."
        rm -rf data
        cp -r $backup_dir/data .
    fi
    
    # 启动服务
    start
    
    log_success "数据恢复完成"
}

# 检查服务健康状态
check_service_health() {
    local retries=10
    local wait_time=3
    
    for i in $(seq 1 $retries); do
        if curl -s -f http://localhost:8000/health &> /dev/null; then
            return 0
        fi
        log_info "等待服务启动 ($i/$retries)..."
        sleep $wait_time
    done
    
    return 1
}

# 主函数
main() {
    case "$1" in
        setup)
            setup
            ;;
        build)
            build
            ;;
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        status)
            status
            ;;
        logs)
            logs "$2"
            ;;
        update)
            update
            ;;
        backup)
            backup
            ;;
        restore)
            restore "$2"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"