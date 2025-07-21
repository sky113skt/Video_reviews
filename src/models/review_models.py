"""
影评相关的数据模型
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class MovieInfo(BaseModel):
    """电影基本信息"""
    title: str = Field(..., description="电影标题")
    year: Optional[int] = Field(None, description="上映年份")
    director: List[str] = Field(default_factory=list, description="导演")
    cast: List[str] = Field(default_factory=list, description="主要演员")
    genre: List[str] = Field(default_factory=list, description="电影类型")
    runtime: Optional[int] = Field(None, description="片长(分钟)")
    plot: Optional[str] = Field(None, description="剧情简介")
    rating: Optional[float] = Field(None, description="评分(0-10)")
    poster_url: Optional[str] = Field(None, description="海报URL")
    release_date: Optional[str] = Field(None, description="上映日期")
    budget: Optional[float] = Field(None, description="预算")
    revenue: Optional[float] = Field(None, description="票房")
    popularity: Optional[float] = Field(None, description="受欢迎程度")
    vote_count: Optional[int] = Field(None, description="评分人数")
    original_language: Optional[str] = Field(None, description="原始语言")
    production_companies: List[str] = Field(default_factory=list, description="制作公司")
    keywords: List[str] = Field(default_factory=list, description="关键词")


class ReviewRequest(BaseModel):
    """影评生成请求"""
    title: str = Field(..., description="电影标题")
    year: Optional[int] = Field(None, description="上映年份")
    target_audience: Optional[str] = Field(None, description="目标观众类型")
    review_style: Optional[str] = Field("professional", description="影评风格")
    focus_areas: List[str] = Field(default_factory=list, description="重点关注领域")
    language: str = Field("zh", description="输出语言")
    max_length: int = Field(1000, description="最大字数")
    include_spoilers: bool = Field(False, description="是否包含剧透")


class ReviewResponse(BaseModel):
    """影评生成响应"""
    title: str = Field(..., description="电影标题")
    year: Optional[int] = Field(None, description="上映年份")
    rating: float = Field(..., description="综合评分(0-10)")
    review: str = Field(..., description="影评内容")
    pros: List[str] = Field(default_factory=list, description="优点")
    cons: List[str] = Field(default_factory=list, description="缺点")
    sources: List[str] = Field(default_factory=list, description="信息来源")
    generated_at: datetime = Field(..., description="生成时间")
    word_count: int = Field(0, description="字数统计")
    review_style: str = Field("professional", description="影评风格")


class ReviewAnalysis(BaseModel):
    """影评分析结果"""
    title: str = Field(..., description="电影标题")
    sentiment_score: float = Field(..., description="情感分数(-1到1)")
    key_themes: List[str] = Field(default_factory=list, description="关键主题")
    positive_points: List[str] = Field(default_factory=list, description="正面观点")
    negative_points: List[str] = Field(default_factory=list, description="负面观点")
    controversial_points: List[str] = Field(default_factory=list, description="争议点")
    target_audience: str = Field(..., description="推荐观众")
    technical_score: float = Field(0.0, description="技术层面评分")
    story_score: float = Field(0.0, description="故事层面评分")
    acting_score: float = Field(0.0, description="表演层面评分")
    overall_score: float = Field(0.0, description="综合评分")


class SearchResult(BaseModel):
    """搜索结果"""
    source: str = Field(..., description="信息来源")
    url: Optional[str] = Field(None, description="链接")
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    relevance_score: float = Field(0.0, description="相关度分数")
    published_date: Optional[datetime] = Field(None, description="发布日期")


class BatchReviewRequest(BaseModel):
    """批量影评请求"""
    movies: List[ReviewRequest] = Field(..., description="电影列表")
    comparison_mode: bool = Field(False, description="是否生成对比分析")
    output_format: str = Field("json", description="输出格式")


class BatchReviewResponse(BaseModel):
    """批量影评响应"""
    reviews: List[ReviewResponse] = Field(..., description="影评列表")
    comparison_analysis: Optional[str] = Field(None, description="对比分析")
    generated_at: datetime = Field(..., description="生成时间")
    total_movies: int = Field(..., description="总电影数")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="详细错误信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")