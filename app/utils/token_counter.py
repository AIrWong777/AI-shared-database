"""
Token计数工具
提供多种方式来估算文本的token数量
"""

import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class TokenCounter:
    @staticmethod
    def estimate_tokens_by_chars(text: str) -> int:
        """
        使用字符数估算token数量（粗略估算）
        中文：每个字符约1个token
        英文：每4个字符约1个token
        
        Args:
            text: 输入文本
            
        Returns:
            int: 估算的token数量
        """
        if not text:
            return 0
            
        # 分离中文和非中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        other_chars = len(re.sub(r'[\u4e00-\u9fff]', '', text))
        
        # 中文字符算1个token，其他字符每4个算1个token
        estimated_tokens = chinese_chars + (other_chars // 4)
        return max(1, estimated_tokens)  # 至少返回1

    @staticmethod
    def estimate_tokens_by_words(text: str) -> int:
        """
        使用分词结果估算token数量
        
        Args:
            text: 输入文本
            
        Returns:
            int: 估算的token数量
        """
        if not text:
            return 0
            
        import jieba
        
        # 分词
        words = list(jieba.cut(text))
        
        # 统计中文词和英文词
        chinese_words = len([w for w in words if re.search(r'[\u4e00-\u9fff]', w)])
        english_words = len([w for w in words if re.search(r'[a-zA-Z]', w)])
        
        # 中文词算1.5个token（考虑到分词可能不准确），英文词算1个token
        estimated_tokens = int(chinese_words * 1.5 + english_words)
        return max(1, estimated_tokens)  # 至少返回1

    @staticmethod
    def estimate_tokens_by_tiktoken(text: str, model_name: Optional[str] = None) -> int:
        """
        使用tiktoken准确计算token数量（如果可用）
        
        Args:
            text: 输入文本
            model_name: 模型名称，如果不指定则使用默认编码器
            
        Returns:
            int: 计算的token数量
        """
        try:
            import tiktoken
            
            # 如果没有指定模型，使用cl100k_base编码器（最通用）
            if model_name:
                encoding = tiktoken.encoding_for_model(model_name)
            else:
                encoding = tiktoken.get_encoding("cl100k_base")
                
            return len(encoding.encode(text))
            
        except Exception as e:
            logger.warning(f"Tiktoken计算失败: {e}，使用字符数估算")
            return TokenCounter.estimate_tokens_by_chars(text)

    @classmethod
    def estimate_tokens(cls, text: str, method: str = "auto") -> int:
        """
        估算文本的token数量
        
        Args:
            text: 输入文本
            method: 估算方法，可选值：
                   - "auto": 自动选择最佳方法
                   - "chars": 使用字符数估算
                   - "words": 使用分词结果估算
                   - "tiktoken": 使用tiktoken计算
            
        Returns:
            int: 估算的token数量
        """
        if method == "chars":
            return cls.estimate_tokens_by_chars(text)
        elif method == "words":
            return cls.estimate_tokens_by_words(text)
        elif method == "tiktoken":
            return cls.estimate_tokens_by_tiktoken(text)
        else:  # auto
            # 优先使用tiktoken，如果失败则回退到分词方法
            try:
                return cls.estimate_tokens_by_tiktoken(text)
            except:
                return cls.estimate_tokens_by_words(text) 