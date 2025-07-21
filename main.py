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

from src.agents.movie_review_agent import MovieReviewAgent
from src.models.review_models import (
    ReviewRequest, 
    ReviewResponse, 
    BatchReviewRequest, 
    BatchReviewResponse,
    ErrorResponse
)

# 加载环境变量
load_dotenv()

# 全局变量
review_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global review_agent
    
    # 启动时初始化Agent
    openai_api_key = os.getenv("OPENAI_API_KEY")
    tmdb_api_key = os.getenv("TMDB_API_KEY")
    
    if not openai_api_key or not tmdb_api_key:
        print("警告: API密钥未配置，请检查.env文件")
        review_agent = None
    else:
        review_agent = MovieReviewAgent(
            openai_api_key=openai_api_key,
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


@app.post("/api/review", response_model=ReviewResponse)
async def generate_review(request: ReviewRequest):
    """生成单部电影影评"""
    if not review_agent:
        raise HTTPException(
            status_code=503,
            detail="Agent服务未初始化，请检查API密钥配置"
        )
    
    try:
        response = await review_agent.generate_review(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


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
        log_level="info"
    )