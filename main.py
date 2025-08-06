"""
电影影评Agent FastAPI服务
"""

import os
import asyncio
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import time
import uuid

from src.agents.movie_review_agent import MovieReviewAgent
from src.models.review_models import (
    ReviewRequest, 
    ReviewResponse, 
    BatchReviewRequest, 
    BatchReviewResponse,
    ErrorResponse
)

# 实时生成状态模型
class GenerationStatus(BaseModel):
    task_id: str
    status: str
    progress: int
    message: str
    current_step: str
    estimated_time_left: Optional[int] = None
    result: Optional[ReviewResponse] = None
    error: Optional[str] = None

# 加载环境变量
load_dotenv()

# 全局变量
review_agent = None
review_tasks = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global review_agent
    
    # 启动时初始化Agent
    kimi_api_key = os.getenv("KIMI_API_KEY")
    tmdb_api_key = os.getenv("TMDB_API_KEY")
    
    if not kimi_api_key or not tmdb_api_key:
        print("警告: API密钥未配置，请检查.env文件")
        review_agent = None
    else:
        review_agent = MovieReviewAgent(
            kimi_api_key=kimi_api_key,
            tmdb_api_key=tmdb_api_key
        )
    
    yield
    
    # 关闭时清理资源
    if review_agent:
        pass  # 可以在这里添加清理逻辑


# 创建FastAPI应用
app = FastAPI(
    title="电影影评智能Agent",
    description="基于LangChain的电影影评生成系统",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "电影影评智能Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "agent_ready": review_agent is not None
    }


@app.post("/api/review")
async def generate_review(request: ReviewRequest):
    """生成单部电影影评 - 返回任务ID"""
    if not review_agent:
        raise HTTPException(
            status_code=503,
            detail="Agent服务未初始化，请检查API密钥配置"
        )
    
    # 创建任务ID
    task_id = str(uuid.uuid4())
    
    # 初始化任务状态
    review_tasks[task_id] = GenerationStatus(
        task_id=task_id,
        status="pending",
        progress=0,
        message="正在初始化...",
        current_step="初始化"
    )
    
    # 在后台启动任务
    asyncio.create_task(_generate_review_with_progress(task_id, request))
    
    return {"task_id": task_id, "message": "影评生成已开始"}


async def _generate_review_with_progress(task_id: str, request: ReviewRequest):
    """带进度更新的影评生成"""
    try:
        task = review_tasks[task_id]
        
        # 步骤1: 获取电影信息
        task.status = "processing"
        task.progress = 10
        task.current_step = "搜索电影信息"
        task.message = f"正在搜索《{request.title}》的电影信息..."
        
        movie_info = await review_agent._get_movie_info(request.title, request.year)
        
        # 步骤2: 收集评论和上下文
        task.progress = 25
        task.current_step = "收集观众评论"
        task.message = "正在收集TMDB观众评论..."
        
        context = await review_agent._collect_context(movie_info, request)
        
        # 步骤3: 情感分析
        task.progress = 40
        task.current_step = "情感分析"
        task.message = "正在分析评论情感倾向..."
        
        if context.get("existing_reviews"):
            sentiments = [review_agent.sentiment_analyzer.analyze(review["content"]) 
                         for review in context["existing_reviews"][:10]]
            
        # 步骤4: 计算评分
        task.progress = 55
        task.current_step = "计算评分"
        task.message = "基于评论计算客观评分..."
        
        rating = await review_agent._calculate_rating(movie_info, context)
        
        # 步骤5: 生成影评内容
        task.progress = 70
        task.current_step = "生成影评"
        task.message = "AI正在撰写专业影评..."
        
        review_content = await review_agent._generate_review_content(movie_info, context, request)
        
        # 步骤6: 最终处理
        task.progress = 90
        task.current_step = "最终处理"
        task.message = "正在完善细节..."
        
        # 计算字数统计
        word_count = len(review_content.replace(' ', '').replace('\\n', ''))
        
        # 创建响应
        from datetime import datetime
        response = ReviewResponse(
            title=movie_info.title,
            year=movie_info.year,
            rating=rating,
            review=review_content,
            sources=context.get("sources", []),
            generated_at=datetime.now(),
            word_count=word_count,
            review_style=request.review_style
        )
        
        # 完成
        task.progress = 100
        task.status = "completed"
        task.current_step = "完成"
        task.message = "影评生成完成！"
        task.result = response
        
    except Exception as e:
        # 错误处理
        task.status = "error"
        task.current_step = "错误"
        task.message = f"生成失败: {str(e)}"
        task.error = str(e)


@app.get("/api/review/status/{task_id}")
async def get_review_status(task_id: str):
    """获取影评生成状态"""
    if task_id not in review_tasks:
        raise HTTPException(
            status_code=404,
            detail="任务不存在"
        )
    
    return review_tasks[task_id]


@app.get("/api/review/result/{task_id}", response_model=ReviewResponse)
async def get_review_result(task_id: str):
    """获取影评生成结果"""
    if task_id not in review_tasks:
        raise HTTPException(
            status_code=404,
            detail="任务不存在"
        )
    
    task = review_tasks[task_id]
    
    if task.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"任务未完成，当前状态: {task.status}"
        )
    
    return task.result


@app.post("/api/review/batch", response_model=BatchReviewResponse)
async def generate_batch_reviews(request: BatchReviewRequest):
    """批量生成影评"""
    if not review_agent:
        raise HTTPException(
            status_code=503,
            detail="Agent服务未初始化，请检查API密钥配置"
        )
    
    try:
        reviews = []
        
        # 异步处理所有请求
        tasks = [review_agent.generate_review(movie) for movie in request.movies]
        reviews = await asyncio.gather(*tasks)
        
        # 生成对比分析（如果需要）
        comparison_analysis = None
        if request.comparison_mode and len(reviews) > 1:
            comparison_analysis = await _generate_comparison_analysis(reviews)
        
        return BatchReviewResponse(
            reviews=reviews,
            comparison_analysis=comparison_analysis,
            generated_at=__import__('datetime').datetime.now(),
            total_movies=len(reviews)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/api/search")
async def search_movies(query: str, year: Optional[int] = None):
    """搜索电影信息"""
    if not review_agent:
        raise HTTPException(
            status_code=503,
            detail="Agent服务未初始化"
        )
    
    try:
        from src.services.tmdb_service import TMDBService
        tmdb_service = TMDBService(os.getenv("TMDB_API_KEY"))
        
        async with tmdb_service:
            movie_info = await tmdb_service.search_movie(query, year)
            return movie_info.dict()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/api/popular")
async def get_popular_movies(page: int = 1):
    """获取热门电影"""
    if not review_agent:
        raise HTTPException(
            status_code=503,
            detail="Agent服务未初始化"
        )
    
    try:
        from src.services.tmdb_service import TMDBService
        tmdb_service = TMDBService(os.getenv("TMDB_API_KEY"))
        
        async with tmdb_service:
            movies = await tmdb_service.get_popular_movies(page)
            return [movie.dict() for movie in movies]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


async def _generate_comparison_analysis(reviews: List[ReviewResponse]) -> str:
    """生成对比分析"""
    if not reviews:
        return ""
    
    # 简单的对比分析逻辑
    ratings = [review.rating for review in reviews]
    avg_rating = sum(ratings) / len(ratings)
    
    best_movie = max(reviews, key=lambda r: r.rating)
    worst_movie = min(reviews, key=lambda r: r.rating)
    
    analysis = f"""
## 电影对比分析

本次分析了{len(reviews)}部电影，平均评分为{avg_rating:.1f}/10。

**最佳推荐**：《{best_movie.title}》(评分：{best_movie.rating}/10)
{getattr(best_movie, 'review', '')[:200]}...

**相对较弱**：《{worst_movie.title}》(评分：{worst_movie.rating}/10)
{getattr(worst_movie, 'review', '')[:200]}...

**总结**：
- 最佳影片比最差影片高出{abs(best_movie.rating - worst_movie.rating):.1f}分
- 整体质量{('较高' if avg_rating >= 7 else '中等' if avg_rating >= 5 else '偏低')}
"""
    
    return analysis.strip()


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info",
        access_log=True
    )