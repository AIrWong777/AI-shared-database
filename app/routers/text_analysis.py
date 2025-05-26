"""
文本分析相关的API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.text_chunk import TextChunk
from ..models.literature import Literature
from ..utils.text_analyzer import TextAnalyzer
from ..utils.auth import get_current_user
from ..models.user import User

router = APIRouter(
    prefix="/text-analysis",
    tags=["text-analysis"]
)

# 创建文本分析器实例
text_analyzer = TextAnalyzer()

@router.get("/{literature_id}/stats")
async def analyze_literature_text(
    literature_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取文献文本的统计分析"""
    # 验证文献是否存在且用户有权限访问
    literature = db.query(Literature).filter(
        Literature.id == literature_id,
        Literature.status == 'active'
    ).first()
    
    if not literature:
        raise HTTPException(status_code=404, detail="Literature not found")
    
    # 获取所有文本块
    chunks = db.query(TextChunk).filter(
        TextChunk.literature_id == literature_id
    ).order_by(TextChunk.chunk_index).all()
    
    if not chunks:
        raise HTTPException(status_code=404, detail="No text chunks found")
    
    # 合并所有文本块
    full_text = "\n\n".join(chunk.text for chunk in chunks)
    
    # 获取文本统计信息
    stats = text_analyzer.get_text_stats(full_text)
    
    # 提取关键词
    keywords = text_analyzer.extract_keywords(full_text, top_k=10)
    
    # 检测质量问题
    quality_issues = text_analyzer.detect_text_quality_issues(full_text)
    
    return {
        "literature_id": literature_id,
        "statistics": stats,
        "keywords": [{"word": word, "weight": weight} for word, weight in keywords],
        "quality_issues": quality_issues,
        "analyzed_at": datetime.utcnow()
    }

@router.get("/{literature_id}/keywords")
async def get_literature_keywords(
    literature_id: str,
    top_k: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取文献的关键词"""
    # 验证文献是否存在且用户有权限访问
    literature = db.query(Literature).filter(
        Literature.id == literature_id,
        Literature.status == 'active'
    ).first()
    
    if not literature:
        raise HTTPException(status_code=404, detail="Literature not found")
    
    # 获取所有文本块
    chunks = db.query(TextChunk).filter(
        TextChunk.literature_id == literature_id
    ).order_by(TextChunk.chunk_index).all()
    
    if not chunks:
        raise HTTPException(status_code=404, detail="No text chunks found")
    
    # 合并所有文本块
    full_text = "\n\n".join(chunk.text for chunk in chunks)
    
    # 提取关键词
    keywords = text_analyzer.extract_keywords(full_text, top_k=top_k)
    
    return {
        "literature_id": literature_id,
        "keywords": [{"word": word, "weight": weight} for word, weight in keywords],
        "total": len(keywords),
        "analyzed_at": datetime.utcnow()
    }

@router.get("/{literature_id}/quality-check")
async def check_text_quality(
    literature_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """检查文献文本质量"""
    # 验证文献是否存在且用户有权限访问
    literature = db.query(Literature).filter(
        Literature.id == literature_id,
        Literature.status == 'active'
    ).first()
    
    if not literature:
        raise HTTPException(status_code=404, detail="Literature not found")
    
    # 获取所有文本块
    chunks = db.query(TextChunk).filter(
        TextChunk.literature_id == literature_id
    ).order_by(TextChunk.chunk_index).all()
    
    if not chunks:
        raise HTTPException(status_code=404, detail="No text chunks found")
    
    # 分别检查每个文本块
    chunk_issues = []
    for chunk in chunks:
        issues = text_analyzer.detect_text_quality_issues(chunk.text)
        if issues:
            chunk_issues.append({
                "chunk_index": chunk.chunk_index,
                "chunk_type": chunk.chunk_type,
                "issues": issues
            })
    
    return {
        "literature_id": literature_id,
        "total_chunks": len(chunks),
        "chunks_with_issues": len(chunk_issues),
        "issues_by_chunk": chunk_issues,
        "analyzed_at": datetime.utcnow()
    }

@router.post("/{literature_id}/normalize")
async def normalize_literature_text(
    literature_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """标准化文献文本"""
    # 验证文献是否存在且用户有权限访问
    literature = db.query(Literature).filter(
        Literature.id == literature_id,
        Literature.status == 'active'
    ).first()
    
    if not literature:
        raise HTTPException(status_code=404, detail="Literature not found")
    
    # 获取所有文本块
    chunks = db.query(TextChunk).filter(
        TextChunk.literature_id == literature_id
    ).order_by(TextChunk.chunk_index).all()
    
    if not chunks:
        raise HTTPException(status_code=404, detail="No text chunks found")
    
    # 标准化每个文本块
    normalized_count = 0
    for chunk in chunks:
        normalized_text = text_analyzer.normalize_text(chunk.text)
        if normalized_text != chunk.text:
            chunk.text = normalized_text
            chunk.updated_at = datetime.utcnow()
            normalized_count += 1
    
    if normalized_count > 0:
        db.commit()
    
    return {
        "literature_id": literature_id,
        "total_chunks": len(chunks),
        "normalized_chunks": normalized_count,
        "normalized_at": datetime.utcnow()
    } 