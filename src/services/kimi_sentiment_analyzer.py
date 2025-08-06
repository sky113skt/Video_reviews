"""
基于Kimi API的情感分析服务
兼容OpenAI接口规范
"""

import os
import openai
from typing import Dict, List, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)

class KimiSentimentAnalyzer:
    """基于Kimi API的情感分析器"""
    
    def __init__(self):
        self.api_key = os.getenv('KIMI_API_KEY')
        self.base_url = os.getenv('KIMI_BASE_URL', 'https://api.moonshot.cn/v1')
        
        # 初始化OpenAI客户端（兼容Kimi）
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # Kimi API参数限制
        self.temperature = 0.3  # 推荐值，避免使用0
        self.max_tokens = 1000
        self.model = "moonshot-v1-8k"  # Kimi支持的模型
    
    def analyze(self, text: str) -> float:
        """
        使用Kimi API分析文本情感倾向
        
        Args:
            text: 待分析的文本
            
        Returns:
            情感分数 (-1.0 到 1.0)
        """
        if not text or not text.strip():
            return 0.0
        
        try:
            prompt = f"""
            请分析以下文本的情感倾向，并给出一个-1.0到1.0的情感分数：
            -1.0表示极度负面，1.0表示极度正面，0.0表示中性
            
            文本："{text}"
            
            请仅返回一个数字，不要添加其他解释。
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=10,
                n=1  # Kimi API要求temperature=0.3时n必须为1
            )
            
            # 解析返回的情感分数
            result = response.choices[0].message.content.strip()
            try:
                score = float(result)
                return max(-1.0, min(1.0, score))  # 确保在范围内
            except ValueError:
                logger.error(f"无法解析Kimi返回的情感分数: {result}")
                return 0.0
                
        except Exception as e:
            logger.error(f"Kimi情感分析失败: {e}")
            return 0.0
    
    def analyze_detailed(self, text: str) -> Dict[str, Any]:
        """
        使用Kimi API进行详细情感分析
        
        Args:
            text: 待分析的文本
            
        Returns:
            详细分析结果
        """
        if not text or not text.strip():
            return {
                "sentiment_score": 0.0,
                "intensity": 0.0,
                "sentiment": "neutral",
                "keywords": [],
                "confidence": 0.0,
                "explanation": ""
            }
        
        try:
            prompt = f"""
            请对以下文本进行详细的情感分析，返回JSON格式：
            
            文本："{text}"
            
            请返回以下格式的JSON：
            {{
                "sentiment_score": -1.0到1.0之间的数字,
                "sentiment": "positive|negative|neutral",
                "keywords": ["关键词1", "关键词2", ...],
                "intensity": 0.0到1.0之间的情感强度,
                "confidence": 0.0到1.0之间的置信度,
                "explanation": "简要的情感分析解释"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=200,
                n=1
            )
            
            import json
            result = response.choices[0].message.content.strip()
            
            # 清理可能的markdown格式
            result = result.replace('```json', '').replace('```', '').strip()
            
            try:
                analysis = json.loads(result)
                return {
                    "sentiment_score": float(analysis.get("sentiment_score", 0.0)),
                    "sentiment": analysis.get("sentiment", "neutral"),
                    "keywords": analysis.get("keywords", []),
                    "intensity": float(analysis.get("intensity", 0.0)),
                    "confidence": float(analysis.get("confidence", 0.0)),
                    "explanation": analysis.get("explanation", "")
                }
            except json.JSONDecodeError:
                logger.error(f"无法解析Kimi返回的JSON: {result}")
                return self._fallback_analysis(text)
                
        except Exception as e:
            logger.error(f"Kimi详细情感分析失败: {e}")
            return self._fallback_analysis(text)
    
    def _fallback_analysis(self, text: str) -> Dict[str, Any]:
        """Kimi API失败时的备选方案"""
        # 使用简单的基于词典的方法
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
        
        # 简单分析
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total = positive_count + negative_count
        if total == 0:
            score = 0.0
        else:
            score = (positive_count - negative_count) / total
        
        return {
            "sentiment_score": score,
            "sentiment": "positive" if score > 0.1 else "negative" if score < -0.1 else "neutral",
            "keywords": [word for word in (positive_words | negative_words) if word in text_lower][:5],
            "intensity": abs(score),
            "confidence": 0.5,
            "explanation": "基于词典的简单分析"
        }
    
    def batch_analyze(self, texts: List[str]) -> List[float]:
        """批量分析情感倾向"""
        return [self.analyze(text) for text in texts]
    
    def analyze_reviews(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析一组影评"""
        if not reviews:
            return {
                "average_sentiment": 0.0,
                "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "keywords": [],
                "confidence": 0.0,
                "summary": "无评论数据"
            }
        
        sentiments = []
        detailed_results = []
        
        for review in reviews:
            content = review.get('content', '')
            if content:
                detailed = self.analyze_detailed(content)
                sentiments.append(detailed['sentiment_score'])
                detailed_results.append(detailed)
        
        if not sentiments:
            return {
                "average_sentiment": 0.0,
                "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "keywords": [],
                "confidence": 0.0,
                "summary": "无有效评论"
            }
        
        # 计算情感分布
        positive = sum(1 for s in sentiments if s > 0.1)
        neutral = sum(1 for s in sentiments if -0.1 <= s <= 0.1)
        negative = sum(1 for s in sentiments if s < -0.1)
        
        # 提取关键词
        all_keywords = []
        for result in detailed_results:
            all_keywords.extend(result.get('keywords', []))
        
        keyword_counts = {}
        for keyword in all_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "average_sentiment": sum(sentiments) / len(sentiments),
            "sentiment_distribution": {
                "positive": positive,
                "neutral": neutral,
                "negative": negative
            },
            "keywords": [kw[0] for kw in top_keywords],
            "confidence": sum(r.get('confidence', 0.5) for r in detailed_results) / len(detailed_results),
            "summary": f"共分析了{len(reviews)}条评论，整体情感倾向: {'正面' if sum(sentiments)/len(sentiments) > 0.1 else '负面' if sum(sentiments)/len(sentiments) < -0.1 else '中性'}",
            "detailed_results": detailed_results
        }
    
    def test_connection(self) -> bool:
        """测试Kimi API连接"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "你好"}],
                max_tokens=10,
                temperature=0.3,
                n=1
            )
            return response.choices[0].message.content is not None
        except Exception as e:
            logger.error(f"Kimi API连接测试失败: {e}")
            return False