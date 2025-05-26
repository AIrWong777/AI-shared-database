"""
文本块模型
用于存储从文献中提取和分块的文本内容
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .research_group import Base

class TextChunk(Base):
    __tablename__ = 'text_chunks'
    
    # 基本信息
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    literature_id = Column(String, ForeignKey('literature.id'), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # 块在文献中的顺序
    chunk_type = Column(String, nullable=False)  # 块类型：title/abstract/content等
    text = Column(Text, nullable=False)  # 文本内容
    
    # 块特征
    char_length = Column(Integer, nullable=False)  # 字符长度
    estimated_tokens = Column(Integer, nullable=False)  # 估算的token数量
    metadata = Column(JSON, nullable=True)  # 其他元数据（如页码、章节等）
    
    # 嵌入向量状态
    embedding_status = Column(String, default='pending', nullable=False)  # pending/processing/completed/failed
    embedding_error = Column(Text, nullable=True)  # 如果嵌入失败，记录错误信息
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    literature = relationship("Literature", back_populates="text_chunks")
    
    def __init__(self, literature_id, chunk_index, chunk_type, text, char_length, estimated_tokens, metadata=None):
        self.id = str(uuid.uuid4())
        self.literature_id = literature_id
        self.chunk_index = chunk_index
        self.chunk_type = chunk_type
        self.text = text
        self.char_length = char_length
        self.estimated_tokens = estimated_tokens
        self.metadata = metadata or {}
        self.embedding_status = 'pending'
        self.embedding_error = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<TextChunk(literature_id='{self.literature_id}', index={self.chunk_index}, type='{self.chunk_type}', status='{self.embedding_status}')>" 