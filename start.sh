#!/bin/bash

# 电影影评Agent启动脚本

set -e

echo "🎬 启动电影影评智能Agent..."

# 检查环境变量
if [[ -z "$KIMI_API_KEY" || -z "$TMDB_API_KEY" ]]; then
    echo "❌ 错误: KIMI_API_KEY 和 TMDB_API_KEY 环境变量必须设置"
    echo "请检查 .env 文件或环境变量配置"
    exit 1
fi

echo "✅ API密钥已配置"

# 启动FastAPI服务
echo "🚀 启动FastAPI服务..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --access-log &
FASTAPI_PID=$!

# 等待FastAPI服务启动
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ FastAPI服务已启动"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ FastAPI服务启动失败"
        exit 1
    fi
    echo "等待FastAPI服务启动... ($i/30)"
    sleep 2
done

# 启动Streamlit界面
echo "🖥️  启动Web界面..."
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false