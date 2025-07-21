"""
电影影评智能Agent
结合多种信息源生成真实、客观的影评
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain.memory import ConversationBufferMemory
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper

from ..services.tmdb_service import TMDBService
from ..services.sentiment_analyzer import SentimentAnalyzer
from ..models.review_models import MovieInfo, ReviewRequest, ReviewResponse
from ..utils.text_processor import TextProcessor


class MovieReviewAgent:
    """智能电影影评Agent"""
    
    def __init__(self, openai_api_key: str, tmdb_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=openai_api_key
        )
        
        self.tmdb_service = TMDBService(tmdb_api_key)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.text_processor = TextProcessor()
        self.search = DuckDuckGoSearchRun()
        self.wikipedia = WikipediaAPIWrapper()
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.tools = self._setup_tools()
        self.agent = self._create_agent()
    
    def _setup_tools(self) -> List[Tool]:
        """设置Agent工具"""
        return [
            Tool(
                name="search_movie_info",
                func=self._search_movie_info,
                description="搜索电影基本信息，包括剧情、导演、演员、评分等"
            ),
            Tool(
                name="search_reviews",
                func=self._search_existing_reviews,
                description="搜索现有影评和用户评价"
            ),
            Tool(
                name="analyze_sentiment",
                func=self._analyze_sentiment,
                description="分析文本情感倾向"
            ),
            Tool(
                name="search_web",
                func=self.search.run,
                description="网络搜索获取最新信息"
            ),
            Tool(
                name="wikipedia_search",
                func=self.wikipedia.run,
                description="搜索维基百科获取背景信息"
            )
        ]
    
    def _create_agent(self):
        """创建LangChain Agent"""
        system_prompt = """你是一个专业的电影评论家，能够基于多方面信息生成真实、客观、有深度的影评。
        
        你的能力包括：
        1. 综合分析电影的基本信息（剧情、导演、演员、制作背景）
        2. 收集和分析现有影评的观点和情感倾向
        3. 结合文化背景和社会影响进行深度分析
        4. 提供平衡的优缺点评价
        5. 给出客观的评分和建议
        
        请确保你的影评：
        - 基于真实数据和观点
        - 避免主观偏见
        - 提供具体的例子和分析
        - 考虑不同类型观众的需求
        - 语言生动但不浮夸
        """
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessage(content="{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        return create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
    
    async def generate_review(self, request: ReviewRequest) -> ReviewResponse:
        """生成电影影评"""
        try:
            # 获取电影基本信息
            movie_info = await self._get_movie_info(request.title, request.year)
            
            # 收集相关信息
            context = await self._collect_context(movie_info, request)
            
            # 生成影评
            review_content = await self._generate_review_content(movie_info, context, request)
            
            # 生成评分
            rating = await self._calculate_rating(movie_info, context)
            
            return ReviewResponse(
                title=movie_info.title,
                year=movie_info.year,
                rating=rating,
                review=review_content,
                sources=context.get("sources", []),
                generated_at=datetime.now()
            )
            
        except Exception as e:
            return ReviewResponse(
                title=request.title,
                year=request.year,
                rating=0.0,
                review=f"生成影评时出现错误: {str(e)}",
                sources=[],
                generated_at=datetime.now()
            )
    
    async def _get_movie_info(self, title: str, year: Optional[int] = None) -> MovieInfo:
        """获取电影详细信息"""
        return await self.tmdb_service.search_movie(title, year)
    
    async def _collect_context(self, movie_info: MovieInfo, request: ReviewRequest) -> Dict[str, Any]:
        """收集分析上下文"""
        context = {
            "movie_info": movie_info.dict(),
            "existing_reviews": [],
            "sentiment_analysis": {},
            "cultural_context": {},
            "box_office": {},
            "awards": [],
            "sources": []
        }
        
        # 搜索现有影评
        reviews = await self._search_existing_reviews(movie_info.title)
        context["existing_reviews"] = reviews
        
        # 情感分析
        if reviews:
            sentiments = [self.sentiment_analyzer.analyze(review["content"]) for review in reviews[:10]]
            context["sentiment_analysis"] = {
                "positive": sum(1 for s in sentiments if s > 0.1),
                "neutral": sum(1 for s in sentiments if -0.1 <= s <= 0.1),
                "negative": sum(1 for s in sentiments if s < -0.1),
                "average_score": sum(sentiments) / len(sentiments) if sentiments else 0
            }
        
        # 搜索文化背景
        cultural_info = await self._search_cultural_context(movie_info)
        context["cultural_context"] = cultural_info
        
        return context
    
    async def _generate_review_content(self, movie_info: MovieInfo, context: Dict[str, Any], request: ReviewRequest) -> str:
        """生成影评内容"""
        
        review_prompt = f"""
        基于以下信息，为电影《{movie_info.title}》({movie_info.year})生成一篇专业影评：
        
        基本信息：
        {json.dumps(movie_info.dict(), ensure_ascii=False, indent=2)}
        
        现有影评情感分析：
        {json.dumps(context.get('sentiment_analysis', {}), ensure_ascii=False, indent=2)}
        
        文化背景：
        {json.dumps(context.get('cultural_context', {}), ensure_ascii=False, indent=2)}
        
        要求：
        1. 从剧情、导演手法、演员表现、技术层面、主题深度等角度分析
        2. 结合现有影评观点，但要保持独立判断
        3. 语言生动但不浮夸，观点明确
        4. 适合{request.target_audience or '普通观众'}观看
        5. 字数在800-1200字之间
        
        请生成完整影评：
        """
        
        response = await self.llm.ainvoke(review_prompt)
        return response.content
    
    async def _calculate_rating(self, movie_info: MovieInfo, context: Dict[str, Any]) -> float:
        """计算综合评分"""
        base_score = movie_info.rating or 0
        
        # 考虑情感分析
        sentiment_score = context.get("sentiment_analysis", {}).get("average_score", 0)
        
        # 综合评分算法
        final_score = (base_score * 0.6 + 
                      (sentiment_score * 5 + 5) * 0.2 + 
                      min(movie_info.popularity or 0, 10) * 0.2)
        
        return min(max(final_score, 0), 10)
    
    def _search_movie_info(self, query: str) -> str:
        """搜索电影信息工具"""
        try:
            # 这里简化为返回字符串，实际应该调用具体服务
            return f"搜索到电影信息: {query}"
        except Exception as e:
            return f"搜索失败: {str(e)}"
    
    def _search_existing_reviews(self, query: str) -> List[Dict]:
        """搜索现有影评"""
        try:
            # 这里简化为返回空列表，实际应该调用具体服务
            return []
        except Exception:
            return []
    
    def _analyze_sentiment(self, text: str) -> str:
        """分析情感"""
        try:
            score = self.sentiment_analyzer.analyze(text)
            return f"情感分数: {score}"
        except Exception as e:
            return f"分析失败: {str(e)}"
    
    async def _search_cultural_context(self, movie_info: MovieInfo) -> Dict[str, Any]:
        """搜索文化背景信息"""
        try:
            search_query = f"{movie_info.title} {movie_info.year} 文化背景 社会影响"
            search_results = self.search.run(search_query)
            
            return {
                "cultural_significance": search_results[:500],
                "social_impact": "",
                "historical_context": ""
            }
        except Exception:
            return {}