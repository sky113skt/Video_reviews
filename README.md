# 电影影评智能Agent 🎬

基于LangChain的智能影评生成系统，能够结合多种信息源生成真实、客观的电影/电视剧影评。

## ✨ 功能特性

- **🔍 智能信息收集**：自动从TMDB、网络等多源收集电影信息
- **🤖 AI深度分析**：基于LangChain和OpenAI GPT进行智能分析
- **✍️ 个性化影评**：根据用户需求生成不同风格的影评
- **📊 情感分析**：分析现有影评的情感倾向
- **🎯 目标导向**：针对不同观众群体提供定制化内容
- **⚡ 实时API**：提供RESTful API接口
- **🖥️ 友好界面**：Streamlit Web界面，易于使用

## 🚀 快速开始

### 环境要求

- Python 3.8+
- OpenAI API Key
- TMDB API Key

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd video_reviews
```

2. **配置环境**
```bash
# 复制环境配置模板
cp .env.example .env

# 编辑.env文件，填入API密钥
nano .env
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **启动服务**
```bash
# 一键启动（推荐）
./start.sh

# 或分别启动
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
streamlit run app.py --server.port 8501
```

### API密钥获取

#### OpenAI API Key
1. 访问 [OpenAI官网](https://platform.openai.com/api-keys)
2. 注册账号并创建API Key

#### TMDB API Key
1. 访问 [TMDB官网](https://www.themoviedb.org/settings/api)
2. 注册账号并申请API Key

## 📖 使用指南

### Web界面使用

1. **访问界面**：启动后在浏览器打开 `http://localhost:8501`
2. **搜索电影**：在侧边栏搜索电影名称
3. **调整参数**：选择目标观众、影评风格等
4. **生成影评**：点击生成按钮，等待AI分析完成
5. **查看结果**：查看生成的影评和评分

### API使用

#### 生成单部影评
```bash
curl -X POST "http://localhost:8000/api/review" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "肖申克的救赎",
    "year": 1994,
    "target_audience": "普通观众",
    "review_style": "professional"
  }'
```

#### 批量生成影评
```bash
curl -X POST "http://localhost:8000/api/review/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "movies": [
      {"title": "肖申克的救赎", "year": 1994},
      {"title": "阿甘正传", "year": 1994}
    ],
    "comparison_mode": true
  }'
```

#### 搜索电影信息
```bash
curl "http://localhost:8000/api/search?query=肖申克的救赎&year=1994"
```

## 🏗️ 项目结构

```
video_reviews/
├── src/
│   ├── agents/              # 智能Agent核心
│   │   └── movie_review_agent.py
│   ├── models/              # 数据模型
│   │   └── review_models.py
│   ├── services/            # 外部服务
│   │   ├── tmdb_service.py
│   │   └── sentiment_analyzer.py
│   └── utils/               # 工具函数
│       └── text_processor.py
├── static/                  # 静态文件
├── logs/                    # 日志文件
├── main.py                  # FastAPI服务
├── app.py                   # Streamlit界面
├── start.sh                 # 启动脚本
├── Dockerfile               # Docker配置
├── requirements.txt         # 依赖列表
├── .env.example            # 环境变量示例
└── README.md               # 项目文档
```

## 🎯 核心功能详解

### 1. 信息收集模块
- **TMDB集成**：获取电影基本信息、评分、演员等
- **网络搜索**：补充背景信息和最新动态
- **维基百科**：获取文化背景和历史意义

### 2. 分析引擎
- **情感分析**：分析现有影评的情感倾向
- **主题提取**：识别电影的核心主题和争议点
- **评分计算**：综合多维度计算客观评分

### 3. 生成引擎
- **个性化定制**：根据用户需求调整风格和深度
- **多语言支持**：支持中英文影评生成
- **质量控制**：确保内容真实、客观、有深度

## 🐳 Docker部署

### 构建镜像
```bash
docker build -t movie-review-agent .
```

### 运行容器
```bash
docker run -d \
  --name movie-agent \
  -p 8000:8000 \
  -p 8501:8501 \
  -e OPENAI_API_KEY=your_key \
  -e TMDB_API_KEY=your_key \
  movie-review-agent
```

### Docker Compose
```yaml
version: '3.8'
services:
  movie-agent:
    build: .
    ports:
      - "8000:8000"
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TMDB_API_KEY=${TMDB_API_KEY}
    volumes:
      - ./logs:/app/logs
```

## 🔧 配置选项

### 环境变量
| 变量名 | 说明 | 示例 |
|--------|------|------|
| OPENAI_API_KEY | OpenAI API密钥 | sk-xxxxxxxx |
| TMDB_API_KEY | TMDB API密钥 | xxxxxxxxx |
| HOST | 服务主机 | 0.0.0.0 |
| PORT | 服务端口号 | 8000 |
| DEBUG | 调试模式 | false |

### 影评参数
- **target_audience**: 目标观众类型
- **review_style**: 影评风格选择
- **max_length**: 最大字数限制
- **include_spoilers**: 是否包含剧透

## 📊 性能优化

### 缓存策略
- 电影信息缓存24小时
- 热门电影列表缓存6小时
- 影评结果不缓存（保证实时性）

### 并发处理
- 异步API调用
- 批量请求并行处理
- 连接池管理

## 🐛 常见问题

### 1. API密钥无效
- 检查.env文件配置
- 确认密钥有效性和额度
- 检查网络连接

### 2. 电影搜索不到
- 尝试使用电影原名
- 检查年份是否正确
- 使用更简单的关键词

### 3. 生成速度慢
- 检查OpenAI API响应时间
- 减少max_length参数
- 使用更快的模型

### 4. 内存占用高
- 降低并发请求数量
- 定期重启服务
- 使用轻量级模型

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境
```bash
# 安装开发依赖
pip install -r requirements.txt
pip install pytest black flake8

# 代码格式化
black src/

# 代码检查
flake8 src/

# 运行测试
pytest tests/
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - 框架支持
- [OpenAI](https://openai.com) - GPT模型
- [TMDB](https://www.themoviedb.org) - 电影数据
- [Streamlit](https://streamlit.io) - Web界面框架

## 📞 联系方式

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Email**: your-email@example.com
- **社区**: [Discord](https://discord.gg/your-server)

---

⭐ 如果这个项目对你有帮助，请给个Star！