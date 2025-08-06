"""
情感分析服务
"""

from typing import Dict, List, Any
import re
import random


class SentimentAnalyzer:
    """情感分析器"""
    
    def __init__(self):
        # 简单的情感分析器，不依赖外部模型
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
        """极简情感分析器 - 基于关键词统计"""
        # 增强的情感词典 - 添加中英文情感词
        positive_keywords = {
            # 中文情感词
            '好', '棒', '精彩', '完美', '经典', '出色', '优秀', '感人', '震撼',
            '好看', '不错', '喜欢', '推荐', '值得', '满意', '开心', '快乐',
            '享受', '自然', '真实', '生动', '紧凑', '巧妙', '用心', '推荐',
            '爱', '最爱', '最佳', '杰作', '神作', '超赞', '牛逼', '厉害',
            '优美', '深刻', '精彩绝伦', '无与伦比', '叹为观止', '拍手叫好',
            '过瘾', '爽', '好看', '美丽', '华丽', '精致', '精彩纷呈',
            # 强烈中文情感词
            '太精彩了', '真的很好', '非常精彩', '特别棒', '强烈推荐', '太棒了',
            '非常好', '特别精彩', '非常棒', '太赞了', '真的很棒', '非常出色',
            '极为精彩', '相当精彩', '极为出色', '非常优秀', '特别优秀',
            # 英文情感词
            'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'brilliant',
            'perfect', 'masterpiece', 'superb', 'outstanding', 'magnificent',
            'beautiful', 'love', 'loved', 'best', 'incredible', 'awesome',
            'good', 'nice', 'enjoyed', 'enjoyable', 'impressed', 'impressive',
            'touching', 'moving', 'powerful', 'strong', 'remarkable',
            # 强烈英文情感词
            'absolutely', 'really', 'very', 'highly', 'truly', 'genuinely',
            'changed', 'life', 'greatest', 'ever', 'stand', 'time', 'test', 'time'
        }
        
        negative_keywords = {
            # 中文负面词
            '差', '烂', '糟糕', '垃圾', '失望', '后悔', '无聊', '难看', '不行',
            '不好', '一般', '普通', '尴尬', '做作', '夸张', '生硬', '老套',
            '俗套', '拖沓', '混乱', '牵强', '空洞', '乏味', '单调', '失望',
            '讨厌', '恶心', '垃圾', '垃圾片', '烂片', '难看', '看不下去',
            '浪费时间', '毁三观', '催眠', '平庸', '拙劣', '粗糙', '低劣',
            '无趣', '枯燥', '冗长', '拖沓', '松散', '混乱不堪',
            # 强烈中文负面情感词
            '真的很差', '非常糟糕', '特别差', '太烂了', '完全浪费时间', '非常失望',
            '特别糟糕', '极为糟糕', '相当差', '非常差', '极差', '太差了', '完全不推荐',
            '非常难看', '特别难看', '极为失望', '相当糟糕', '非常后悔',
            # 英文负面词
            'bad', 'terrible', 'awful', 'horrible', 'disappointing', 'disappointed',
            'waste', 'boring', 'bored', 'poor', 'worst', 'hate', 'hated',
            'dislike', 'disliked', 'mediocre', 'predictable', 'ridiculous',
            'stupid', 'dumb', 'sucks', 'sucked', 'crap', 'trash', 'garbage',
            'overrated', 'disgusting', 'annoying', 'frustrating', 'weak',
            # 强烈英文负面词
            'absolutely', 'terrible', 'completely', 'waste', 'time', 'money', 'dont', "don't",
            'bother', 'watching', 'understand', 'why', 'people', 'love'
        }
        
        # 强化程度副词 - 中英文
        intensifiers = {
            # 中文程度副词
            '非常', '特别', '极其', '太', '真的', '很', '相当', '十分', '相当',
            '超级', '极度', '十分', '非常', '相当', '真的', '确实', '实在',
            '过于', '太过', '尤其', '格外', '特别', '十分', '相当', '非常',
            # 英文程度副词
            'very', 'really', 'so', 'extremely', 'absolutely', 'completely',
            'totally', 'quite', 'rather', 'pretty', 'fairly', 'highly',
            'truly', 'genuinely', 'quite', 'really', 'very', 'so'
        }
        
        # 强化否定词 - 中英文
        negations = {
            # 中文否定词
            '不', '没', '无', '别', '未', '毫无', '完全没有',
            # 英文否定词
            'not', 'no', 'never', 'none', 'nothing', 'nobody', 'nowhere',
            'neither', 'nor', "don't", "dont", "doesn't", "doesnt", 
            "didn't", "didnt", "won't", "wont", "wouldn't", "wouldnt",
            "can't", "cant", "couldn't", "couldnt", "shouldn't", "shouldnt"
        }
        
        text_lower = text.lower()
        
        # 计算正面分数
        positive_score = 0
        for keyword in positive_keywords:
            if keyword in text_lower:
                # 检查否定词
                keyword_pos = text_lower.find(keyword)
                start_pos = max(0, keyword_pos - 8)  # 扩大搜索范围
                preceding_text = text_lower[start_pos:keyword_pos]
                
                # 只有当否定词直接修饰情感词时才算否定
                negation_found = False
                for neg in negations:
                    if neg in preceding_text and len(preceding_text.strip()) <= len(neg) + 2:
                        negation_found = True
                        break
                
                if negation_found:
                    positive_score -= 1  # 被否定的正面词
                else:
                    positive_score += 1
                    
                    # 检查程度副词
                    for intensifier in intensifiers:
                        if intensifier in preceding_text:
                            positive_score += 0.5
                            break
        
        # 计算负面分数
        negative_score = 0
        for keyword in negative_keywords:
            if keyword in text_lower:
                # 检查否定词
                keyword_pos = text_lower.find(keyword)
                start_pos = max(0, keyword_pos - 8)  # 扩大搜索范围
                preceding_text = text_lower[start_pos:keyword_pos]
                
                # 只有当否定词直接修饰情感词时才算否定
                negation_found = False
                for neg in negations:
                    if neg in preceding_text and len(preceding_text.strip()) <= len(neg) + 2:
                        negation_found = True
                        break
                
                if negation_found:
                    negative_score -= 1  # 被否定的负面词
                else:
                    negative_score += 1
                    
                    # 检查程度副词
                    for intensifier in intensifiers:
                        if intensifier in preceding_text:
                            negative_score += 0.5
                            break
        
        # 计算总分
        total_score = positive_score - negative_score
        
        # 如果没有情感词，返回中性
        if total_score == 0:
            return 0.0
        
        # 标准化到[-1, 1]范围 - 大幅增强敏感性
        max_score = len(positive_keywords) + len(negative_keywords)
        if max_score > 0:
            normalized = total_score / max_score
            # 极大增强敏感性，让情感表达更强烈
            enhanced_score = normalized * 12  # 从乘以8改为乘以12
            return max(min(enhanced_score, 1.0), -1.0)
        
        return 0.0
    
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