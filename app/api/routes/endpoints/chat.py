from app.api.dependencies import get_active_user, get_db
from fastapi import APIRouter, Depends, HTTPException, status # type: ignore
from sqlalchemy.orm import Session # type: ignore
from typing import List
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.api.schemas.chat import (
    ChatSessionResponse, ChatSessionCreate, ChatRequest, ChatResponse,
    ChatMessageResponse
)
from app.services.rag_service import RAGService
from app.core.exceptions import StudyAssistantException

router = APIRouter()

rag_service = RAGService()


@router.post("/", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    try:
        # Get or create chat session
        if chat_request.session_id:
            session = db.query(ChatSession).filter(
                ChatSession.id == chat_request.session_id,
                ChatSession.user_id == current_user.id
            ).first()
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat session not found"
                )
        else:
            session = ChatSession(user_id=current_user.id)
            db.add(session)
            db.commit()
            db.refresh(session)
        
        # Save user message
        user_message = ChatMessage(
            session_id=session.id,
            role="user",
            content=chat_request.message
        )
        db.add(user_message)
        
        # Generate RAG response
        rag_response = await rag_service.generate_response(
            query=chat_request.message,
            user_id=current_user.id,
            context_documents=chat_request.context_documents
        )
        
        # Save assistant message
        assistant_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=rag_response["response"],
            sources=rag_response["sources"]
        )
        db.add(assistant_message)
        
        db.commit()
        
        return ChatResponse(
            message=rag_response["response"],
            sources=rag_response["sources"],
            session_id=session.id
        )
        
    except StudyAssistantException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.updated_at.desc()).all()
    
    return sessions


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return session


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    session = ChatSession(
        title=session_data.title,
        user_id=current_user.id
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    db.delete(session)
    db.commit()
    
    return {"message": "Chat session deleted successfully"}
