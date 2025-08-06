"""
TMDB电影数据库服务
提供电影信息查询功能
"""

import asyncio
import aiohttp
from typing import Optional, List, Dict, Any
import os
from ..models.review_models import MovieInfo


class TMDBService:
    """TMDB API服务"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"
        self.session = None
    
    async def __aenter__(self):
        """异步上下文管理器"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.session:
            await self.session.close()
    
    async def search_movie(self, title: str, year: Optional[int] = None) -> MovieInfo:
        """搜索电影信息"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # 搜索电影
            search_results = await self._search_movies(title, year)
            if not search_results.get('results'):
                return MovieInfo(title=title, year=year)
            
            # 获取最匹配的电影
            movie_data = search_results['results'][0]
            movie_id = movie_data['id']
            
            # 获取详细信息
            details = await self._get_movie_details(movie_id)
            credits = await self._get_movie_credits(movie_id)
            keywords = await self._get_movie_keywords(movie_id)
            
            # 构建MovieInfo对象
            return self._build_movie_info(details, credits, keywords)
            
        except Exception as e:
            print(f"TMDB搜索错误: {e}")
            # 返回基础信息，避免网络问题导致失败
            return MovieInfo(
                title=title,
                year=year,
                plot=f"无法获取{title}的详细信息，请检查网络连接或稍后重试。"
            )
    
    async def _search_movies(self, title: str, year: Optional[int] = None) -> Dict[str, Any]:
        """搜索电影列表"""
        params = {
            'api_key': self.api_key,
            'query': title,
            'language': 'zh-CN',
            'page': 1
        }
        
        if year:
            params['year'] = year
        
        async with self.session.get(f"{self.base_url}/search/movie", params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {'results': []}
    
    async def _get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """获取电影详细信息"""
        params = {
            'api_key': self.api_key,
            'language': 'zh-CN',
            'append_to_response': 'release_dates'
        }
        
        async with self.session.get(f"{self.base_url}/movie/{movie_id}", params=params) as response:
            if response.status == 200:
                return await response.json()
            return {}
    
    async def _get_movie_credits(self, movie_id: int) -> Dict[str, Any]:
        """获取电影演职员信息"""
        params = {
            'api_key': self.api_key,
            'language': 'zh-CN'
        }
        
        async with self.session.get(f"{self.base_url}/movie/{movie_id}/credits", params=params) as response:
            if response.status == 200:
                return await response.json()
            return {}
    
    async def _get_movie_keywords(self, movie_id: int) -> Dict[str, Any]:
        """获取电影关键词"""
        params = {
            'api_key': self.api_key,
            'language': 'zh-CN'
        }
        
        async with self.session.get(f"{self.base_url}/movie/{movie_id}/keywords", params=params) as response:
            if response.status == 200:
                return await response.json()
            return {}
    
    def _build_movie_info(self, details: Dict[str, Any], credits: Dict[str, Any], keywords: Dict[str, Any]) -> MovieInfo:
        """构建MovieInfo对象"""
        # 提取导演信息
        directors = []
        for crew_member in credits.get('crew', []):
            if crew_member.get('job') == 'Director':
                directors.append(crew_member.get('name', ''))
        
        # 提取主要演员
        cast = []
        for actor in credits.get('cast', [])[:10]:  # 取前10个演员
            cast.append(actor.get('name', ''))
        
        # 提取关键词
        keyword_list = []
        for keyword in keywords.get('keywords', []):
            keyword_list.append(keyword.get('name', ''))
        
        # 提取制作公司
        companies = []
        for company in details.get('production_companies', []):
            companies.append(company.get('name', ''))
        
        # 提取类型
        genres = []
        for genre in details.get('genres', []):
            genres.append(genre.get('name', ''))
        
        return MovieInfo(
            id=details.get('id'),
            title=details.get('title', ''),
            year=int(details.get('release_date', '').split('-')[0]) if details.get('release_date') else None,
            director=directors,
            cast=cast,
            genre=genres,
            runtime=details.get('runtime'),
            plot=details.get('overview'),
            rating=details.get('vote_average'),
            poster_url=f"{self.image_base_url}{details.get('poster_path')}" if details.get('poster_path') else None,
            release_date=details.get('release_date'),
            budget=details.get('budget'),
            revenue=details.get('revenue'),
            popularity=details.get('popularity'),
            vote_count=details.get('vote_count'),
            original_language=details.get('original_language'),
            production_companies=companies,
            keywords=keyword_list
        )
    
    async def get_popular_movies(self, page: int = 1) -> List[MovieInfo]:
        """获取热门电影"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        params = {
            'api_key': self.api_key,
            'language': 'zh-CN',
            'page': page
        }
        
        async with self.session.get(f"{self.base_url}/movie/popular", params=params) as response:
            if response.status == 200:
                data = await response.json()
                movies = []
                
                for movie_data in data.get('results', []):
                    movie = await self.search_movie(movie_data['title'])
                    movies.append(movie)
                
                return movies
        
        return []
    
    async def get_movie_reviews(self, movie_id: int, page: int = 1) -> List[Dict[str, Any]]:
        """获取电影评论"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        params = {
            'api_key': self.api_key,
            'language': 'zh-CN',
            'page': page
        }
        
        try:
            async with self.session.get(f"{self.base_url}/movie/{movie_id}/reviews", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    reviews = data.get('results', [])
                    
                    # 获取多页评论（最多5页）
                    total_pages = min(data.get('total_pages', 1), 5)
                    for page_num in range(2, total_pages + 1):
                        params['page'] = page_num
                        async with self.session.get(f"{self.base_url}/movie/{movie_id}/reviews", params=params) as page_response:
                            if page_response.status == 200:
                                page_data = await page_response.json()
                                reviews.extend(page_data.get('results', []))
                    
                    return reviews
        except Exception as e:
            print(f"获取评论失败: {e}")
        
        return []
    
    async def calculate_review_based_rating(self, movie_id: int) -> Dict[str, Any]:
        """基于评论计算评分 - 全新算法"""
        reviews = await self.get_movie_reviews(movie_id)
        
        if not reviews:
            return {
                "rating": 0.0,
                "review_count": 0,
                "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "average_sentiment": 0.0,
                "rating_breakdown": {},
                "confidence_level": "无数据"
            }
        
        # 使用情感分析器分析评论
        from .sentiment_analyzer import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        
        sentiment_results = []
        for review in reviews:
            content = review.get('content', '')
            if content:
                sentiment = analyzer.analyze(content)
                sentiment_results.append(sentiment)
        
        if not sentiment_results:
            return {
                "rating": 0.0,
                "review_count": len(reviews),
                "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "average_sentiment": 0.0,
                "rating_breakdown": {},
                "confidence_level": "无情感数据"
            }
        
        # 计算情感分布
        positive = sum(1 for s in sentiment_results if s > 0.1)
        neutral = sum(1 for s in sentiment_results if -0.1 <= s <= 0.1)
        negative = sum(1 for s in sentiment_results if s < -0.1)
        total_reviews = len(sentiment_results)
        
        # 新的评分算法 - 更贴合实际
        rating_components = self._calculate_comprehensive_rating(
            positive, neutral, negative, total_reviews, sentiment_results
        )
        
        return {
            "rating": rating_components["final_rating"],
            "review_count": len(reviews),
            "sentiment_distribution": {
                "positive": positive,
                "neutral": neutral,
                "negative": negative
            },
            "average_sentiment": round(sum(sentiment_results) / len(sentiment_results), 3),
            "rating_breakdown": rating_components["breakdown"],
            "confidence_level": rating_components["confidence"],
            "reviews_sample": reviews[:5]
        }
    
    def _calculate_comprehensive_rating(self, positive: int, neutral: int, negative: int, 
                                       total_reviews: int, sentiment_results: list) -> dict:
        """综合评分算法 - 基于观众喜好比例和多维度因素"""
        
        # 基础指标计算
        positive_ratio = positive / total_reviews if total_reviews > 0 else 0
        negative_ratio = negative / total_reviews if total_reviews > 0 else 0
        neutral_ratio = neutral / total_reviews if total_reviews > 0 else 0
        
        # 1. 观众喜好评分 (核心指标) - 重新设计
        # 更合理的评分映射：90%喜欢=9分，80%=8分，以此类推
        if positive_ratio >= 0.9:
            audience_score = 9.0 + (positive_ratio - 0.9) * 10  # 超过90%的部分给予额外奖励
        elif positive_ratio >= 0.8:
            audience_score = 8.0 + (positive_ratio - 0.8) * 10
        elif positive_ratio >= 0.7:
            audience_score = 7.0 + (positive_ratio - 0.7) * 10
        elif positive_ratio >= 0.6:
            audience_score = 6.0 + (positive_ratio - 0.6) * 10
        elif positive_ratio >= 0.5:
            audience_score = 5.0 + (positive_ratio - 0.5) * 10
        else:
            audience_score = positive_ratio * 10  # 低于50%的直接映射
        
        # 2. 口碑一致性评分 - 重新设计
        consistency_score = self._calculate_consistency_score(
            positive_ratio, negative_ratio, sentiment_results
        )
        
        # 3. 评论数量权重 - 增强影响
        quantity_weight = self._calculate_quantity_weight(total_reviews)
        
        # 4. 情感强度评分 - 重新设计
        intensity_score = self._calculate_intensity_score(sentiment_results)
        
        # 5. 综合计算 - 调整权重
        # 公式: (观众喜好评分 * 0.6 + 口碑一致性 * 0.25 + 情感强度 * 0.15) * 数量权重
        base_rating = (audience_score * 0.6 + consistency_score * 0.25 + intensity_score * 0.15)
        final_rating = min(max(base_rating * quantity_weight, 0), 10)
        
        # 置信度评估
        confidence = self._assess_confidence(total_reviews, positive_ratio, negative_ratio)
        
        # 详细评分分解
        breakdown = {
            "audience_score": round(audience_score, 2),
            "consistency_score": round(consistency_score, 2),
            "intensity_score": round(intensity_score, 2),
            "quantity_weight": round(quantity_weight, 2),
            "positive_ratio": round(positive_ratio * 100, 1),
            "negative_ratio": round(negative_ratio * 100, 1),
            "formula": f"(({audience_score:.1f}×0.6 + {consistency_score:.1f}×0.25 + {intensity_score:.1f}×0.15) × {quantity_weight:.2f})"
        }
        
        return {
            "final_rating": round(final_rating, 1),
            "breakdown": breakdown,
            "confidence": confidence
        }
    
    def _calculate_consistency_score(self, positive_ratio: float, negative_ratio: float, 
                                   sentiment_results: list) -> float:
        """计算口碑一致性评分"""
        # 如果正面评价占主导且负面评价很少，一致性高
        if positive_ratio >= 0.8 and negative_ratio <= 0.1:
            return 9.0
        elif positive_ratio >= 0.7 and negative_ratio <= 0.15:
            return 8.0
        elif positive_ratio >= 0.6 and negative_ratio <= 0.2:
            return 7.0
        elif positive_ratio >= 0.5:
            return 6.0
        elif positive_ratio >= 0.4:
            return 5.0
        else:
            # 负面评价较多，一致性较低
            return max(4.0 - negative_ratio * 5, 1.0)
    
    def _calculate_quantity_weight(self, total_reviews: int) -> float:
        """计算评论数量权重"""
        if total_reviews >= 100:
            return 1.0  # 足够多评论，完全可信
        elif total_reviews >= 50:
            return 0.95
        elif total_reviews >= 20:
            return 0.9
        elif total_reviews >= 10:
            return 0.85
        elif total_reviews >= 5:
            return 0.8
        else:
            return 0.7  # 评论太少，需要打折扣
    
    def _calculate_intensity_score(self, sentiment_results: list) -> float:
        """计算情感强度评分 - 重新设计"""
        if not sentiment_results:
            return 5.0
        
        # 计算平均情感强度
        avg_sentiment = abs(sum(sentiment_results) / len(sentiment_results))
        
        # 计算情感的标准差，反映评价的一致性
        import statistics
        if len(sentiment_results) > 1:
            sentiment_std = statistics.stdev(sentiment_results)
        else:
            sentiment_std = 0
        
        # 强度映射到评分 - 更敏感的映射
        if avg_sentiment >= 0.7:
            intensity = 9.0  # 情感非常强烈
        elif avg_sentiment >= 0.5:
            intensity = 8.0  # 情感强烈
        elif avg_sentiment >= 0.3:
            intensity = 7.0  # 情感中等
        elif avg_sentiment >= 0.15:
            intensity = 6.0  # 情感较弱
        else:
            intensity = 5.0  # 情感平淡
        
        # 如果评价非常一致（标准差小），给予额外奖励
        if sentiment_std < 0.2:
            intensity += 0.5
        
        return min(intensity, 10.0)
    
    def _assess_confidence(self, total_reviews: int, positive_ratio: float, negative_ratio: float) -> str:
        """评估评分置信度"""
        if total_reviews >= 50 and positive_ratio >= 0.7:
            return "高"
        elif total_reviews >= 20 and positive_ratio >= 0.6:
            return "中高"
        elif total_reviews >= 10:
            return "中等"
        elif total_reviews >= 5:
            return "中低"
        else:
            return "低"