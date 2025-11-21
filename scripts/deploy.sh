#!/bin/bash

# TrevanQuant 部署脚本

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

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose 未安装，请先安装 docker-compose"
        exit 1
    fi

    log_success "Docker 环境检查通过"
}

# 检查配置文件
check_config() {
    if [ ! -f ".env" ]; then
        log_warning ".env 文件不存在，正在创建示例配置..."

        cat > .env << EOF
# 邮件配置
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
EMAIL_RECIPIENTS=recipient1@email.com,recipient2@email.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# 数据库配置
DATABASE_URL=sqlite:///database.db
DATABASE_ECHO=false

# 应用配置
DEBUG=false
LOG_LEVEL=INFO

# 数据获取配置
REQUEST_DELAY=1.0
MAX_RETRIES=3
TIMEOUT=30
BATCH_SIZE=100
EOF

        log_warning "请编辑 .env 文件配置您的邮件信息"
        log_info "编辑完成后重新运行此脚本"
        exit 1
    fi

    log_success "配置文件检查通过"
}

# 构建Docker镜像
build_image() {
    log_info "开始构建 Docker 镜像..."

    if docker build -t trevanquant:latest .; then
        log_success "Docker 镜像构建成功"
    else
        log_error "Docker 镜像构建失败"
        exit 1
    fi
}

# 停止现有容器
stop_containers() {
    log_info "停止现有容器..."

    if docker-compose down --remove-orphans; then
        log_success "容器停止成功"
    else
        log_warning "没有运行的容器"
    fi
}

# 启动容器
start_containers() {
    log_info "启动容器..."

    if docker-compose up -d; then
        log_success "容器启动成功"
    else
        log_error "容器启动失败"
        exit 1
    fi
}

# 检查服务状态
check_status() {
    log_info "检查服务状态..."

    # 等待容器启动
    sleep 5

    # 检查容器状态
    if docker-compose ps; then
        log_success "容器运行正常"
    else
        log_error "容器运行异常"
        exit 1
    fi

    # 检查健康状态
    health_status=$(docker inspect --format='{{.State.Health.Status}}' trevanquant-app 2>/dev/null || echo "unknown")

    if [ "$health_status" = "healthy" ]; then
        log_success "服务健康检查通过"
    elif [ "$health_status" = "unknown" ]; then
        log_warning "健康检查状态未知"
    else
        log_warning "健康检查状态: $health_status"
    fi
}

# 查看日志
show_logs() {
    log_info "显示服务日志（按 Ctrl+C 退出）："
    docker-compose logs -f
}

# 主函数
main() {
    echo "======================================"
    echo "TrevanQuant 部署脚本"
    echo "======================================"

    # 解析命令行参数
    case "${1:-deploy}" in
        "deploy")
            log_info "开始部署 TrevanQuant..."
            check_docker
            check_config
            stop_containers
            build_image
            start_containers
            check_status
            log_success "TrevanQuant 部署完成！"
            ;;
        "update")
            log_info "更新 TrevanQuant..."
            stop_containers
            build_image
            start_containers
            check_status
            log_success "TrevanQuant 更新完成！"
            ;;
        "stop")
            log_info "停止 TrevanQuant..."
            stop_containers
            log_success "TrevanQuant 已停止"
            ;;
        "restart")
            log_info "重启 TrevanQuant..."
            stop_containers
            start_containers
            check_status
            log_success "TrevanQuant 重启完成"
            ;;
        "logs")
            show_logs
            ;;
        "status")
            docker-compose ps
            ;;
        "clean")
            log_warning "这将删除所有容器和镜像，确认继续吗？(y/N)"
            read -r confirm
            if [[ $confirm == [yY] ]]; then
                docker-compose down -v --rmi all
                docker system prune -f
                log_success "清理完成"
            else
                log_info "操作已取消"
            fi
            ;;
        "help"|"-h"|"--help")
            echo "用法: $0 [命令]"
            echo ""
            echo "命令:"
            echo "  deploy  - 部署应用（默认）"
            echo "  update  - 更新应用"
            echo "  stop    - 停止应用"
            echo "  restart - 重启应用"
            echo "  logs    - 查看日志"
            echo "  status  - 查看状态"
            echo "  clean   - 清理所有容器和镜像"
            echo "  help    - 显示帮助"
            ;;
        *)
            log_error "未知命令: $1"
            echo "使用 '$0 help' 查看帮助"
            exit 1
            ;;
    esac
}

# 捕获退出信号
trap 'log_info "脚本被中断"; exit 1' INT TERM

# 执行主函数
main "$@"