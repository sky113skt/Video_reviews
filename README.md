# 🎬 电影影评智能Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Streamlit](https://img.shields.io/badge/streamlit-app-red.svg)](https://streamlit.io/)

基于LangChain和Kimi AI的智能影评生成系统，能够结合多源信息生成真实、客观、专业的电影/电视剧影评。

## ✨ 核心特性

### 🤖 AI智能分析
- **Kimi AI驱动**: 使用月之暗面Kimi大模型，提供高质量的中文内容生成
- **多维度分析**: 从剧情、演技、摄影、音乐等多个角度深度解析
- **情感识别**: 智能分析电影情感倾向和观众反应
- **主题提取**: 自动识别电影核心主题和文化内涵

### 🎯 个性化定制
- **多种风格**: 专业学术、轻松休闲、娱乐导向等5种风格选择
- **目标导向**: 针对不同观众群体（普通观众、影迷、影评人等）定制内容
- **长度控制**: 支持500-2000字的灵活字数设置
- **剧透选项**: 可选择是否包含剧情剧透内容

### ⚡ 实时体验
- **进度追踪**: 实时显示AI分析和生成进度
- **响应迅速**: 30-45秒完成一篇完整影评
- **即时预览**: 生成完成后立即显示结果
- **历史记录**: 自动保存生成历史，支持查看和对比

### 🛠️ 技术架构
- **现代化界面**: 基于Streamlit的响应式Web界面
- **RESTful API**: 提供完整的API接口，支持第三方集成
- **容器化部署**: Docker + Docker Compose，一键部署
- **生产就绪**: 包含nginx反向代理、健康检查、日志监控

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Docker & Docker Compose (推荐)
- Kimi API Key
- TMDB API Key

### 一键部署 (推荐)

```bash
# 1. 克隆项目
git clone https://github.com/sky113skt/Video_reviews.git
cd video_reviews

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥

# 3. 一键部署
chmod +x deploy.sh
./deploy.sh setup
./deploy.sh start
```

### 手动部署

#### 开发环境
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境
cp .env.example .env
# 编辑 .env 文件

# 启动服务
./start.sh
```

#### 生产环境
```bash
# 使用Docker Compose
docker-compose up -d

# 或使用部署脚本
./deploy.sh build
./deploy.sh start
```

## 🔑 API密钥获取

### Kimi API Key
1. 访问 [月之暗面官网](https://platform.moonshot.cn)
2. 注册账号并完成实名认证
3. 在控制台创建API Key
4. 充值账户余额（新用户有免费额度）

### TMDB API Key
1. 访问 [TMDB官网](https://www.themoviedb.org/settings/api)
2. 注册开发者账号
3. 申请API Key（通常即时生效）
4. 记录API Key和API Read Access Token

## 📖 使用指南

### Web界面操作

1. **访问应用**: 启动后访问 `http://localhost:8501`
2. **搜索电影**: 在首页输入电影名称
3. **设置参数**: 
   - 选择目标观众群体
   - 选择影评风格
   - 设置字数限制
   - 选择是否包含剧透
4. **生成影评**: 点击搜索按钮，等待AI分析
5. **查看结果**: 实时查看生成进度和最终结果

### API接口使用

#### 生成单部影评
```bash
curl -X POST "http://localhost:8000/api/review" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "肖申克的救赎",
    "year": 1994,
    "target_audience": "普通观众",
    "review_style": "professional",
    "max_length": 1000,
    "include_spoilers": false
  }'
```

#### 搜索电影信息
```bash
curl "http://localhost:8000/api/search?query=肖申克的救赎&year=1994"
```

#### 获取生成状态
```bash
curl "http://localhost:8000/api/review/status/{task_id}"
```

#### 获取生成结果
```bash
curl "http://localhost:8000/api/review/result/{task_id}"
```

## 🏗️ 项目架构

```
video_reviews/
├── src/
│   ├── agents/                    # AI智能体
│   │   └── movie_review_agent.py  # 主要影评生成Agent
│   ├── models/                    # 数据模型
│   │   └── review_models.py       # Pydantic模型定义
│   ├── services/                  # 外部服务
│   │   ├── tmdb_service.py        # TMDB API服务
│   │   ├── sentiment_analyzer.py  # 情感分析服务
│   │   └── kimi_sentiment_analyzer.py # Kimi情感分析
│   └── utils/                     # 工具函数
├── nginx/                         # Nginx配置
│   └── nginx.conf                 # 生产环境配置
├── static/                        # 静态资源
├── logs/                          # 日志文件
├── main.py                        # FastAPI应用入口
├── app.py                         # Streamlit界面
├── deploy.sh                      # 部署脚本
├── start.sh                       # 启动脚本
├── Dockerfile                     # Docker镜像配置
├── docker-compose.yml             # Docker Compose配置
├── requirements.txt               # Python依赖
├── .env.example                   # 环境变量示例
└── README.md                      # 项目文档
```

## 🎯 核心功能详解

### 1. 智能信息收集
- **TMDB集成**: 获取电影基本信息、评分、演员阵容、剧情简介
- **多源数据**: 整合IMDb、豆瓣等多个平台的信息
- **实时更新**: 确保获取最新的电影数据

### 2. AI分析引擎
- **深度理解**: 基于Kimi大模型理解电影内容和主题
- **多角度分析**: 从导演手法、演员表现、技术层面等维度分析
- **情感计算**: 分析电影的情感倾向和观众反应

### 3. 内容生成
- **个性化**: 根据用户需求调整内容深度和表达方式
- **专业质量**: 生成符合专业影评标准的文章
- **结构化**: 包含引言、剧情分析、评价、总结等完整结构

## 🐳 部署方案

### 开发环境
```bash
# 本地开发
./deploy.sh dev

# 或使用Docker
docker-compose up
```

### 生产环境
```bash
# 使用nginx反向代理
docker-compose -f docker-compose.prod.yml up -d

# 或使用部署脚本
./deploy.sh prod
```

### 云服务部署
项目支持部署到各种云平台：
- **阿里云**: 使用ECS + 容器服务
- **腾讯云**: 使用CVM + TKE
- **AWS**: 使用EC2 + ECS
- **Vercel**: 使用Docker部署

## 🔧 配置说明

### 环境变量
| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `KIMI_API_KEY` | Kimi API密钥 | - | ✅ |
| `KIMI_BASE_URL` | Kimi API地址 | `https://api.moonshot.cn/v1` | ❌ |
| `TMDB_API_KEY` | TMDB API密钥 | - | ✅ |
| `HOST` | 服务监听地址 | `0.0.0.0` | ❌ |
| `PORT` | FastAPI端口 | `8000` | ❌ |
| `STREAMLIT_SERVER_PORT` | Streamlit端口 | `8501` | ❌ |
| `DEBUG` | 调试模式 | `false` | ❌ |

### 影评参数
- **target_audience**: `普通观众`、`电影爱好者`、`专业影评人`、`学生群体`、`家庭观众`
- **review_style**: `professional`、`casual`、`academic`、`entertaining`、`brief`
- **max_length**: 500-2000字
- **include_spoilers**: `true`/`false`

## 📊 性能指标

### 响应时间
- **信息收集**: 5-10秒
- **AI分析**: 20-30秒
- **内容生成**: 5-10秒
- **总计**: 30-50秒

### 资源占用
- **内存**: 512MB - 1GB
- **CPU**: 单核心即可
- **网络**: 稳定的互联网连接

## 🛡️ 安全考虑

### API密钥安全
- 使用环境变量存储密钥
- 不在代码中硬编码密钥
- 定期轮换API密钥

### 数据安全
- 不存储用户生成内容
- 请求日志不包含敏感信息
- 支持HTTPS部署

## 🐛 常见问题

### Q: API密钥配置错误
**A**: 检查`.env`文件格式，确保密钥正确且有效

### Q: 电影搜索不到
**A**: 
- 尝试使用电影英文名
- 检查年份是否正确
- 确认电影在TMDB数据库中存在

### Q: 生成速度慢
**A**:
- 检查网络连接
- 减少字数限制
- 确认Kimi API服务正常

### Q: Docker部署失败
**A**:
- 确保Docker版本 >= 20.0
- 检查端口占用情况
- 查看容器日志排查问题

## 🤝 贡献指南

我们欢迎社区贡献！请遵循以下步骤：

1. **Fork项目**
2. **创建功能分支**: `git checkout -b feature/AmazingFeature`
3. **提交更改**: `git commit -m 'Add some AmazingFeature'`
4. **推送分支**: `git push origin feature/AmazingFeature`
5. **提交Pull Request**

### 开发环境设置
```bash
# 克隆项目
git clone https://github.com/sky113skt/Video_reviews.git
cd video_reviews

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境
cp .env.example .env

# 启动开发服务
./start.sh
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - 强大的AI应用框架
- [月之暗面](https://www.moonshot.cn) - 优秀的AI模型提供商
- [TMDB](https://www.themoviedb.org) - 丰富的电影数据库
- [Streamlit](https://streamlit.io) - 便捷的Web应用框架
- [FastAPI](https://fastapi.tiangolo.com) - 高性能的Web框架

## 📞 联系我们

- **问题反馈**: [GitHub Issues](https://github.com/sky113skt/Video_reviews/issues)
- **功能建议**: [GitHub Discussions](https://github.com/sky113skt/Video_reviews/discussions)
- **邮件联系**: [your-email@example.com](mailto:your-email@example.com)

## 🌟 Star History

如果这个项目对你有帮助，请给我们一个Star！

[![Star History Chart](https://api.star-history.com/svg?repos=sky113skt/Video_reviews&type=Date)](https://star-history.com/#sky113skt/Video_reviews&Date)

---

<div align="center">

**让AI为每一部电影提供专业解读** 🎬✨

[返回顶部](#-电影影评智能agent)

</div>