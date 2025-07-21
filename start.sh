#!/bin/bash

# 电影影评Agent启动脚本

echo "🎬 启动电影影评智能Agent..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python3"
    exit 1
fi

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3未安装，请先安装pip3"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖包..."
pip3 install -r requirements.txt

# 检查.env文件
if [ ! -f .env ]; then
    echo "⚠️  未找到.env文件，创建示例配置文件..."
    cp .env.example .env
    echo "🔧 请编辑.env文件配置API密钥"
fi

# 启动FastAPI服务
echo "🚀 启动FastAPI服务..."
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > logs/api.log 2>&1 &

# 等待服务启动
sleep 3

# 启动Streamlit界面
echo "🖥️  启动Web界面..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0