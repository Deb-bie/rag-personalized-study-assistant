from app.api.dependencies import get_active_user, get_db
from fastapi import APIRouter, Depends, HTTPException, status # type: ignore
from sqlalchemy.orm import Session # type: ignore
from typing import List, Dict, Any
from app.models.user import User
from app.services.llm_service import LLMService
from app.services.document_service import DocumentService
from app.models.document import Document

router = APIRouter()
llm_service = LLMService()
document_service = DocumentService()


@router.post("/generate-quiz")
async def generate_quiz(
    document_id: int,
    num_questions: int = 5,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    # Get document content
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if not document.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has no content"
        )
    
    try:
        questions = await llm_service.generate_quiz_questions(
            document.content,
            num_questions
        )
        
        return {
            "document_title": document.title,
            "questions": questions
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating quiz: {str(e)}"
        )


@router.post("/summarize")
async def summarize_document(
    document_id: int,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    from app.models.document import Document
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.summary:
        return {"summary": document.summary}
    
    if not document.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has no content"
        )
    
    try:
        summary = await llm_service.generate_summary(document.content)
        
        # Save summary to database
        document.summary = summary
        db.commit()
        
        return {"summary": summary}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating summary: {str(e)}"
        )