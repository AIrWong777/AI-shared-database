"""
文本处理工具
实现文本分块等高级文本处理功能
"""

import logging
from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .token_counter import TokenCounter

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def split_text_into_chunks(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    token_count_method: str = "auto"
) -> List[Dict[str, Any]]:
    """
    将文本分割成适合处理的小块
    
    Args:
        text: 要分割的文本
        chunk_size: 每个块的目标大小（字符数）
        chunk_overlap: 块之间的重叠大小（字符数）
        token_count_method: token计数方法，可选值：
                          - "auto": 自动选择最佳方法
                          - "chars": 使用字符数估算
                          - "words": 使用分词结果估算
                          - "tiktoken": 使用tiktoken计算
        
    Returns:
        List[Dict[str, Any]]: 包含文本块及其元数据的列表
    """
    try:
        # 创建文本分割器
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )
        
        # 分割文本
        chunks = text_splitter.split_text(text)
        
        # 为每个文本块添加元数据
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            # 清理块中的空白字符
            chunk = chunk.strip()
            if not chunk:  # 跳过空块
                continue
                
            # 估算token数量
            token_count = TokenCounter.estimate_tokens(chunk, method=token_count_method)
            
            # 创建块的元数据
            chunk_data = {
                "chunk_index": i,
                "text": chunk,
                "char_length": len(chunk),
                "estimated_tokens": token_count,
                "start_char": text.find(chunk),  # 在原文中的起始位置
            }
            
            processed_chunks.append(chunk_data)
        
        logger.info(f"文本已分割成 {len(processed_chunks)} 个块")
        return processed_chunks
        
    except Exception as e:
        logger.error(f"文本分块失败: {e}")
        return []

def prepare_chunks_for_embedding(
    chunks: List[Dict[str, Any]],
    literature_id: str,
    group_id: str
) -> List[Dict[str, Any]]:
    """
    为文本块添加文献相关的元数据，准备进行embedding
    
    Args:
        chunks: 文本块列表
        literature_id: 文献ID
        group_id: 研究组ID
        
    Returns:
        List[Dict[str, Any]]: 添加了元数据的文本块列表
    """
    try:
        enriched_chunks = []
        for chunk in chunks:
            # 复制原始数据
            enriched_chunk = chunk.copy()
            
            # 添加文献和研究组信息
            enriched_chunk.update({
                "literature_id": literature_id,
                "group_id": group_id,
                "chunk_type": "literature_text",  # 用于区分不同类型的文本块
                "embedding_status": "pending"  # 标记尚未生成embedding
            })
            
            enriched_chunks.append(enriched_chunk)
        
        logger.info(f"已为 {len(enriched_chunks)} 个文本块添加元数据")
        return enriched_chunks
        
    except Exception as e:
        logger.error(f"为文本块添加元数据失败: {e}")
        return []

def process_literature_text(
    text: str,
    literature_id: str,
    group_id: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    token_count_method: str = "auto"
) -> Optional[List[Dict[str, Any]]]:
    """
    处理文献文本：分块并准备embedding
    
    Args:
        text: 文献文本
        literature_id: 文献ID
        group_id: 研究组ID
        chunk_size: 块大小
        chunk_overlap: 块重叠大小
        token_count_method: token计数方法
        
    Returns:
        Optional[List[Dict[str, Any]]]: 处理后的文本块列表，失败时返回None
    """
    try:
        # 1. 分割文本
        chunks = split_text_into_chunks(text, chunk_size, chunk_overlap, token_count_method)
        if not chunks:
            logger.error("文本分块失败")
            return None
            
        # 2. 添加元数据
        enriched_chunks = prepare_chunks_for_embedding(chunks, literature_id, group_id)
        if not enriched_chunks:
            logger.error("添加元数据失败")
            return None
            
        # 3. 返回处理后的文本块
        logger.info(f"文献 {literature_id} 处理完成，生成了 {len(enriched_chunks)} 个文本块")
        return enriched_chunks
        
    except Exception as e:
        logger.error(f"处理文献文本失败: {e}")
        return None 