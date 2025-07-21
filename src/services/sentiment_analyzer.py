"""
情感分析服务
"""

from typing import Dict, List, Any
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
import re


class SentimentAnalyzer:
    """情感分析器"""
    
    def __init__(self):
        self.model_name = "uer/chinese_roberta_L-2_H-128"  # 中文情感分析模型
        self.classifier = None
        self._load_model()
    
    def _load_model(self):
        """加载预训练模型"""
        try:
            # 尝试加载中文情感分析模型
            self.classifier = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
                device=-1  # 使用CPU
            )
        except Exception as e:
            print(f"加载模型失败: {e}")
            # 使用简单的基于词典的方法作为备选
            self.classifier = None
    
    def analyze(self, text: str) -> float:
        """
        分析文本情感倾向
        
        Args:
            text: 待分析的文本
            
        Returns:
            情感分数 (-1.0 到 1.0)
        """
        if not text or not text.strip():
            return 0.0
        
        if self.classifier:
            try:
                result = self.classifier(text[:512])[0]  # 限制文本长度
                if result['label'] == 'positive':
                    return result['score']
                elif result['label'] == 'negative':
                    return -result['score']
                else:
                    return 0.0
            except Exception as e:
                print(f"模型分析失败: {e}")
                return self._simple_sentiment_analysis(text)
        else:
            return self._simple_sentiment_analysis(text)
    
    def _simple_sentiment_analysis(self, text: str) -> float:
        """简单的情感分析作为备选"""
        # 中文情感词典
        positive_words = {
            '好', '棒', '优秀', '精彩', '出色', '喜欢', '推荐', '经典', '震撼', '感动',
            '好看', '不错', '给力', '完美', '优秀', '卓越', '杰出', '令人惊叹',
            '精彩绝伦', '引人入胜', '感人至深', '回味无穷', '值得一看'
        }
        
        negative_words = {
            '差', '烂', '糟糕', '失望', '无聊', '难看', '垃圾', '浪费时间', '后悔',
            '差评', '不行', '不好', '失望', '无语', '无力吐槽', '毁三观',
            '烂片', '雷人', '狗血', '老套', '俗套', '尴尬', '出戏'
        }
        
        # 文本预处理
        text = text.lower()
        text = re.sub(r'[^一-龥a-zA-Z0-9]', '', text)
        
        # 计算情感分数
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        return (positive_count - negative_count) / total
    
    def batch_analyze(self, texts: List[str]) -> List[float]:
        """批量分析情感倾向"""
        return [self.analyze(text) for text in texts]
    
    def analyze_detailed(self, text: str) -> Dict[str, Any]:
        """详细情感分析"""
        sentiment_score = self.analyze(text)
        
        # 提取关键词
        keywords = self._extract_keywords(text)
        
        # 分析情感强度
        intensity = abs(sentiment_score)
        
        return {
            "sentiment_score": sentiment_score,
            "intensity": intensity,
            "sentiment": "positive" if sentiment_score > 0.1 else "negative" if sentiment_score < -0.1 else "neutral",
            "keywords": keywords,
            "confidence": min(intensity + 0.3, 1.0)  # 简单置信度
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取
        words = re.findall(r'[一-龥a-zA-Z]+', text.lower())
        
        # 过滤停用词
        stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没', '看', '好',
            '自己', '这', '那', '这个', '那个', '一个', '一些', '电影', '影片', '这部'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 1]
        
        # 统计词频并返回前10个
        word_count = {}
        for word in keywords:
            word_count[word] = word_count.get(word, 0) + 1
        
        return [word for word, count in sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]]
    
    def analyze_reviews(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析一组影评"""
        if not reviews:
            return {
                "average_sentiment": 0.0,
                "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "keywords": [],
                "most_positive": None,
                "most_negative": None
            }
        
        sentiments = []
        keywords_counter = {}
        
        for review in reviews:
            content = review.get('content', '')
            if content:
                sentiment = self.analyze(content)
                sentiments.append(sentiment)
                
                # 提取关键词
                review_keywords = self._extract_keywords(content)
                for keyword in review_keywords:
                    keywords_counter[keyword] = keywords_counter.get(keyword, 0) + 1
        
        if not sentiments:
            return {
                "average_sentiment": 0.0,
                "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "keywords": [],
                "most_positive": None,
                "most_negative": None
            }
        
        # 计算情感分布
        positive = sum(1 for s in sentiments if s > 0.1)
        neutral = sum(1 for s in sentiments if -0.1 <= s <= 0.1)
        negative = sum(1 for s in sentiments if s < -0.1)
        
        # 找出最正面和最负面的评论
        most_positive = max(reviews, key=lambda r: self.analyze(r.get('content', ''))) if reviews else None
        most_negative = min(reviews, key=lambda r: self.analyze(r.get('content', ''))) if reviews else None
        
        return {
            "average_sentiment": sum(sentiments) / len(sentiments),
            "sentiment_distribution": {
                "positive": positive,
                "neutral": neutral,
                "negative": negative
            },
            "keywords": [word for word, count in sorted(keywords_counter.items(), key=lambda x: x[1], reverse=True)[:20]],
            "most_positive": most_positive,
            "most_negative": most_negative,
            "total_reviews": len(reviews)
        }