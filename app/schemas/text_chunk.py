"""
文本块的Pydantic模型
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class TextChunkBase(BaseModel):
    """文本块基础模型"""
    chunk_type: str = Field(..., description="块类型：title/abstract/content等")
    text: str = Field(..., description="文本内容")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="其他元数据")

class TextChunkCreate(TextChunkBase):
    """创建文本块时使用的模型"""
    literature_id: str = Field(..., description="所属文献ID")
    chunk_index: int = Field(..., description="块在文献中的顺序")
    char_length: int = Field(..., description="字符长度")
    estimated_tokens: int = Field(..., description="估算的token数量")

class TextChunkUpdate(BaseModel):
    """更新文本块时使用的模型"""
    text: Optional[str] = Field(None, description="文本内容")
    metadata: Optional[Dict[str, Any]] = Field(None, description="其他元数据")
    embedding_status: Optional[str] = Field(None, description="嵌入状态")
    embedding_error: Optional[str] = Field(None, description="嵌入错误信息")

class TextChunkResponse(TextChunkBase):
    """返回文本块信息时使用的模型"""
    id: str
    literature_id: str
    chunk_index: int
    char_length: int
    estimated_tokens: int
    embedding_status: str
    embedding_error: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 