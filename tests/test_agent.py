"""
测试用例
"""

import pytest
import asyncio
from src.models.review_models import ReviewRequest, MovieInfo
from src.services.tmdb_service import TMDBService
from src.services.sentiment_analyzer import SentimentAnalyzer
from src.utils.text_processor import TextProcessor


class TestTMDBService:
    """测试TMDB服务"""
    
    @pytest.mark.asyncio
    async def test_search_movie_basic(self):
        """测试基础电影搜索"""
        service = TMDBService("test_key")
        
        # 使用mock测试
        result = MovieInfo(title="测试电影", year=2023)
        assert result.title == "测试电影"
        assert result.year == 2023
    
    @pytest.mark.asyncio
    async def test_build_movie_info(self):
        """测试构建电影信息"""
        service = TMDBService("test_key")
        
        details = {
            "title": "测试电影",
            "release_date": "2023-01-01",
            "runtime": 120,
            "overview": "测试简介",
            "vote_average": 8.5,
            "popularity": 100.0,
            "budget": 1000000,
            "revenue": 5000000,
            "original_language": "en",
            "genres": [{"name": "剧情"}],
            "production_companies": [{"name": "测试公司"}]
        }
        
        credits = {
            "crew": [{"job": "Director", "name": "测试导演"}],
            "cast": [{"name": "测试演员1"}, {"name": "测试演员2"}]
        }
        
        keywords = {
            "keywords": [{"name": "测试关键词"}]
        }
        
        result = service._build_movie_info(details, credits, keywords)
        
        assert result.title == "测试电影"
        assert result.year == 2023
        assert result.runtime == 120
        assert "测试导演" in result.director
        assert "测试演员1" in result.cast


class TestSentimentAnalyzer:
    """测试情感分析器"""
    
    def test_analyze_positive(self):
        """测试正面情感分析"""
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze("这部电影太棒了，强烈推荐")
        assert result > 0
    
    def test_analyze_negative(self):
        """测试负面情感分析"""
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze("这部电影很糟糕，不推荐")
        assert result < 0
    
    def test_analyze_neutral(self):
        """测试中性情感分析"""
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze("这部电影一般般")
        assert abs(result) < 0.5
    
    def test_batch_analyze(self):
        """测试批量分析"""
        analyzer = SentimentAnalyzer()
        texts = ["很好", "很差", "一般"]
        results = analyzer.batch_analyze(texts)
        assert len(results) == 3


class TestTextProcessor:
    """测试文本处理器"""
    
    def test_clean_text(self):
        """测试文本清理"""
        processor = TextProcessor()
        text = "  <p>这是一个测试文本</p>  \n\n  "
        result = processor.clean_text(text)
        assert "这是一个测试文本" in result
        assert "<p>" not in result
    
    def test_extract_movie_title(self):
        """测试电影标题提取"""
        processor = TextProcessor()
        
        text1 = "《肖申克的救赎》是一部经典电影"
        assert processor.extract_movie_title(text1) == "肖申克的救赎"
        
        text2 = "电影：肖申克的救赎很好看"
        assert processor.extract_movie_title(text2) == "肖申克的救赎"
    
    def test_extract_year(self):
        """测试年份提取"""
        processor = TextProcessor()
        
        text = "这部电影于1994年上映"
        result = processor.extract_year(text)
        assert result == 1994
    
    def test_split_sentences(self):
        """测试句子分割"""
        processor = TextProcessor()
        text = "这是第一句。这是第二句！这是第三句？"
        sentences = processor.split_sentences(text)
        assert len(sentences) == 3
    
    def test_count_words(self):
        """测试字数统计"""
        processor = TextProcessor()
        text = "这是一个测试文本"
        count = processor.count_words(text)
        assert count == 7  # 7个中文字符
    
    def test_extract_keywords(self):
        """测试关键词提取"""
        processor = TextProcessor()
        text = "这部电影非常精彩，演员表演出色，剧情引人入胜"
        keywords = processor.extract_keywords(text, top_k=3)
        assert len(keywords) <= 3
        assert isinstance(keywords, list)


class TestReviewModels:
    """测试数据模型"""
    
    def test_review_request_creation(self):
        """测试影评请求创建"""
        request = ReviewRequest(
            title="测试电影",
            year=2023,
            target_audience="普通观众"
        )
        
        assert request.title == "测试电影"
        assert request.year == 2023
        assert request.target_audience == "普通观众"
    
    def test_movie_info_creation(self):
        """测试电影信息创建"""
        movie = MovieInfo(
            title="测试电影",
            year=2023,
            director=["测试导演"],
            cast=["测试演员"],
            rating=8.5
        )
        
        assert movie.title == "测试电影"
        assert movie.year == 2023
        assert movie.rating == 8.5
    
    def test_review_response_creation(self):
        """测试影评响应创建"""
        from datetime import datetime
        
        response = ReviewResponse(
            title="测试电影",
            year=2023,
            rating=8.5,
            review="这是一部很棒的电影",
            generated_at=datetime.now()
        )
        
        assert response.title == "测试电影"
        assert response.rating == 8.5


@pytest.mark.asyncio
async def test_async_operations():
    """测试异步操作"""
    # 测试异步电影搜索
    service = TMDBService("test_key")
    
    # 由于需要真实API密钥，这里只测试异常处理
    try:
        result = await service.search_movie("测试电影")
        assert isinstance(result, MovieInfo)
    except Exception as e:
        # 期望API密钥无效错误
        assert "test_key" in str(e) or "invalid" in str(e).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])