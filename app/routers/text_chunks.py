"""
文本块相关的API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.text_chunk import TextChunk
from ..models.literature import Literature
from ..schemas.text_chunk import TextChunkCreate, TextChunkResponse, TextChunkUpdate
from ..utils.auth import get_current_user
from ..models.user import User

router = APIRouter(
    prefix="/text-chunks",
    tags=["text-chunks"]
)

@router.get("/{literature_id}", response_model=List[TextChunkResponse])
async def get_text_chunks(
    literature_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    chunk_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定文献的文本块列表"""
    # 验证文献是否存在且用户有权限访问
    literature = db.query(Literature).filter(
        Literature.id == literature_id,
        Literature.status == 'active'
    ).first()
    
    if not literature:
        raise HTTPException(status_code=404, detail="Literature not found")
    
    # 构建查询
    query = db.query(TextChunk).filter(TextChunk.literature_id == literature_id)
    
    # 如果指定了chunk_type，添加过滤条件
    if chunk_type:
        query = query.filter(TextChunk.chunk_type == chunk_type)
    
    # 按chunk_index排序，分页
    chunks = query.order_by(TextChunk.chunk_index).offset(skip).limit(limit).all()
    
    return chunks

@router.get("/{literature_id}/stats")
async def get_text_chunks_stats(
    literature_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定文献的文本块统计信息"""
    # 验证文献是否存在且用户有权限访问
    literature = db.query(Literature).filter(
        Literature.id == literature_id,
        Literature.status == 'active'
    ).first()
    
    if not literature:
        raise HTTPException(status_code=404, detail="Literature not found")
    
    # 获取统计信息
    total_chunks = db.query(TextChunk).filter(TextChunk.literature_id == literature_id).count()
    total_chars = db.query(db.func.sum(TextChunk.char_length)).filter(
        TextChunk.literature_id == literature_id
    ).scalar() or 0
    total_tokens = db.query(db.func.sum(TextChunk.estimated_tokens)).filter(
        TextChunk.literature_id == literature_id
    ).scalar() or 0
    
    # 获取各种状态的数量
    status_counts = db.query(
        TextChunk.embedding_status,
        db.func.count(TextChunk.id)
    ).filter(
        TextChunk.literature_id == literature_id
    ).group_by(TextChunk.embedding_status).all()
    
    # 转换为字典
    status_dict = {status: count for status, count in status_counts}
    
    return {
        "total_chunks": total_chunks,
        "total_chars": total_chars,
        "total_tokens": total_tokens,
        "embedding_status": {
            "pending": status_dict.get("pending", 0),
            "processing": status_dict.get("processing", 0),
            "completed": status_dict.get("completed", 0),
            "failed": status_dict.get("failed", 0)
        }
    }

@router.put("/{chunk_id}", response_model=TextChunkResponse)
async def update_text_chunk(
    chunk_id: str,
    chunk_update: TextChunkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新文本块信息"""
    chunk = db.query(TextChunk).filter(TextChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="Text chunk not found")
    
    # 验证文献是否存在且用户有权限访问
    literature = db.query(Literature).filter(
        Literature.id == chunk.literature_id,
        Literature.status == 'active'
    ).first()
    
    if not literature:
        raise HTTPException(status_code=404, detail="Literature not found")
    
    # 更新文本块
    for field, value in chunk_update.dict(exclude_unset=True).items():
        setattr(chunk, field, value)
    
    chunk.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(chunk)
    
    return chunk 