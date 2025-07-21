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
            return MovieInfo(title=title, year=year)
    
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
        
        async with self.session.get(f"{self.base_url}/movie/{movie_id}/reviews", params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('results', [])
        
        return []