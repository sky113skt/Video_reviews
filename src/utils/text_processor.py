"""
文本处理工具
"""

import re
import jieba
from typing import List, Dict, Any
import html
import unicodedata


class TextProcessor:
    """文本处理器"""
    
    def __init__(self):
        # 初始化jieba分词
        jieba.initialize()
    
    def clean_text(self, text: str) -> str:
        """
        清理文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # HTML解码
        text = html.unescape(text)
        
        # Unicode规范化
        text = unicodedata.normalize('NFKC', text)
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 移除特殊字符，但保留中文、英文、数字和基本标点
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s，。！？：；""''（）【】《》…—]', '', text)
        
        return text
    
    def extract_movie_title(self, text: str) -> str:
        """
        从文本中提取电影标题
        
        Args:
            text: 包含电影名的文本
            
        Returns:
            提取的电影标题
        """
        # 移除常见的前后缀
        patterns = [
            r'《([^》]+)》',
            r'电影[:：]\s*([^，。！？\n]+)',
            r'影片[:：]\s*([^，。！？\n]+)',
            r'([^《》]+?)\s*(电影|影片)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return text.strip()
    
    def extract_year(self, text: str) -> int:
        """
        从文本中提取年份
        
        Args:
            text: 包含年份的文本
            
        Returns:
            提取的年份，如果找不到返回None
        """
        year_match = re.search(r'(19|20)\d{2}', text)
        if year_match:
            return int(year_match.group())
        return None
    
    def split_sentences(self, text: str) -> List[str]:
        """
        将文本分割成句子
        
        Args:
            text: 原始文本
            
        Returns:
            句子列表
        """
        # 中文句子分割
        sentences = re.split(r'[。！？\n]+', text)
        
        # 清理和过滤
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        提取关键词
        
        Args:
            text: 文本
            top_k: 返回的关键词数量
            
        Returns:
            关键词列表
        """
        if not text:
            return []
        
        # 分词
        words = jieba.lcut(text)
        
        # 过滤停用词和短词
        stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没', '看', '好',
            '自己', '这', '那', '这个', '那个', '一个', '一些', '电影', '影片', '这部',
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没', '看', '好',
            '自己', '这', '那', '这个', '那个', '一个', '一些', '电影', '影片', '这部'
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
        
        # 统计词频
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 返回前top_k个关键词
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_k]]
    
    def summarize_text(self, text: str, max_length: int = 100) -> str:
        """
        文本摘要
        
        Args:
            text: 原始文本
            max_length: 摘要最大长度
            
        Returns:
            摘要文本
        """
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        # 简单的基于句子位置的摘要
        sentences = self.split_sentences(text)
        if not sentences:
            return text[:max_length] + "..."
        
        # 取前几个句子
        summary = ""
        for sentence in sentences:
            if len(summary + sentence) <= max_length:
                summary += sentence + "。"
            else:
                break
        
        if not summary:
            return text[:max_length] + "..."
        
        return summary.strip()
    
    def count_words(self, text: str) -> int:
        """
        计算文本字数
        
        Args:
            text: 文本
            
        Returns:
            字数
        """
        if not text:
            return 0
        
        # 中文按字符计数，英文按单词计数
        chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', text))
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        
        return chinese_chars + english_words
    
    def detect_language(self, text: str) -> str:
        """
        检测文本语言
        
        Args:
            text: 文本
            
        Returns:
            语言代码 (zh, en, etc.)
        """
        if not text:
            return "unknown"
        
        # 简单的语言检测
        chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if chinese_chars > english_chars:
            return "zh"
        elif english_chars > chinese_chars:
            return "en"
        else:
            return "mixed"
    
    def extract_quotes(self, text: str) -> List[str]:
        """
        提取引用或重要语句
        
        Args:
            text: 文本
            
        Returns:
            引用列表
        """
        quotes = []
        
        # 提取引号内的内容
        quote_patterns = [
            r'"([^"]+)"',
            r'"([^"]+)"',
            r'『([^』]+)』',
            r'「([^」]+)」'
        ]
        
        for pattern in quote_patterns:
            matches = re.findall(pattern, text)
            quotes.extend(matches)
        
        # 提取重要句子（包含评价性词汇的句子）
        sentences = self.split_sentences(text)
        evaluative_words = [
            '精彩', '优秀', '出色', '震撼', '感动', '经典', '推荐',
            '糟糕', '失望', '无聊', '难看', '雷人', '狗血', '老套',
            '创新', '突破', '惊喜', '惊艳', '完美', '失败'
        ]
        
        for sentence in sentences:
            for word in evaluative_words:
                if word in sentence and sentence not in quotes:
                    quotes.append(sentence)
                    break
        
        return quotes[:5]  # 返回前5个引用
    
    def format_review(self, content: str, title: str, rating: float) -> str:
        """
        格式化影评内容
        
        Args:
            content: 影评内容
            title: 电影标题
            rating: 评分
            
        Returns:
            格式化后的影评
        """
        formatted = f"# 《{title}》影评\n\n"
        formatted += f"**综合评分：{rating}/10**\n\n"
        formatted += f"{content}"
        
        return formatted