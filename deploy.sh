#!/bin/bash

# 电影影评项目一键部署脚本
# 支持开发环境和生产环境部署

set -e

echo "🎬 电影影评智能Agent - 一键部署脚本"
echo "======================================="

# 检查系统要求
check_requirements() {
    echo "📋 检查系统要求..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker未安装，请先安装Docker"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3未安装，请先安装Python3"
        exit 1
    fi
    
    echo "✅ 系统要求检查通过"
}

# 创建环境配置文件
setup_env() {
    echo "⚙️  设置环境配置..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            echo "✅ 已创建.env配置文件，请编辑并设置您的API密钥"
            echo "📝 编辑 .env 文件，设置以下内容："
            echo "   - KIMI_API_KEY: 您的Kimi API密钥"
            echo "   - TMDB_API_KEY: 您的TMDB API密钥"
            read -p "按Enter键继续..."
        else
            echo "❌ 未找到.env.example文件"
            exit 1
        fi
    else
        echo "✅ .env配置文件已存在"
    fi
}

# 创建必要的目录
setup_directories() {
    echo "📁 创建必要的目录..."
    
    mkdir -p logs
    mkdir -p static
    mkdir -p data
    
    echo "✅ 目录创建完成"
}

# 安装依赖（开发模式）
install_dependencies() {
    echo "📦 安装Python依赖..."
    
    if [ -f requirements.txt ]; then
        pip3 install -r requirements.txt
        echo "✅ 依赖安装完成"
    else
        echo "❌ 未找到requirements.txt文件"
        exit 1
    fi
}

# 构建Docker镜像
build_docker() {
    echo "🐳 构建Docker镜像..."
    
    docker-compose build
    echo "✅ Docker镜像构建完成"
}

# 启动服务
start_services() {
    echo "🚀 启动服务..."
    
    docker-compose up -d
    echo "✅ 服务启动完成"
    
    # 显示服务状态
    echo "📊 服务状态："
    docker-compose ps
    
    # 显示访问地址
    echo "🌐 访问地址："
    echo "   - FastAPI API: http://localhost:8000"
    echo "   - Streamlit界面: http://localhost:8501"
    echo "   - API文档: http://localhost:8000/docs"
}

# 停止服务
stop_services() {
    echo "🛑 停止服务..."
    
    docker-compose down
    echo "✅ 服务已停止"
}

# 查看日志
view_logs() {
    echo "📋 查看服务日志..."
    
    docker-compose logs -f
}

# 开发模式启动
dev_mode() {
    echo "🔧 开发模式启动..."
    
    # 启动FastAPI服务
    echo "启动FastAPI服务..."
    python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
    FASTAPI_PID=$!
    
    # 等待FastAPI服务启动
    sleep 5
    
    # 启动Streamlit界面
    echo "启动Streamlit界面..."
    streamlit run app.py --server.port=8501 --server.address=0.0.0.0 &
    STREAMLIT_PID=$!
    
    echo "✅ 开发模式启动完成"
    echo "   - FastAPI: http://localhost:8000"
    echo "   - Streamlit: http://localhost:8501"
    
    # 等待用户中断
    wait $FASTAPI_PID $STREAMLIT_PID
}

# 显示帮助信息
show_help() {
    echo "📖 使用方法："
    echo "   $0 [选项]"
    echo ""
    echo "选项："
    echo "   setup     - 初始化设置环境"
    echo "   dev       - 开发模式启动"
    echo "   build     - 构建Docker镜像"
    echo "   start     - 启动服务"
    echo "   stop      - 停止服务"
    echo "   restart   - 重启服务"
    echo "   logs      - 查看日志"
    echo "   status    - 查看状态"
    echo "   clean     - 清理资源"
    echo "   help      - 显示帮助"
    echo ""
    echo "示例："
    echo "   $0 setup     # 初始化环境"
    echo "   $0 dev       # 开发模式启动"
    echo "   $0 start     # 生产模式启动"
}

# 清理资源
clean_resources() {
    echo "🧹 清理资源..."
    
    docker-compose down -v --remove-orphans
    docker system prune -f
    
    echo "✅ 资源清理完成"
}

# 查看状态
show_status() {
    echo "📊 服务状态："
    docker-compose ps
    
    echo ""
    echo "🌐 访问地址："
    echo "   - FastAPI API: http://localhost:8000"
    echo "   - Streamlit界面: http://localhost:8501"
    echo "   - API文档: http://localhost:8000/docs"
}

# 主函数
main() {
    case "${1:-}" in
        "setup")
            check_requirements
            setup_env
            setup_directories
            ;;
        "dev")
            check_requirements
            setup_env
            setup_directories
            install_dependencies
            dev_mode
            ;;
        "build")
            check_requirements
            setup_env
            build_docker
            ;;
        "start")
            check_requirements
            setup_env
            build_docker
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            start_services
            ;;
        "logs")
            view_logs
            ;;
        "status")
            show_status
            ;;
        "clean")
            clean_resources
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        "")
            echo "❌ 请指定操作选项"
            show_help
            exit 1
            ;;
        *)
            echo "❌ 未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"