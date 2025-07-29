from app.api.dependencies import get_active_user, get_db
from fastapi import APIRouter, Depends, HTTPException, status, Query # type: ignore
from sqlalchemy.orm import Session # type: ignore
from typing import List, Optional
from datetime import datetime
from app.models.user import User
from app.models.study_session import StudySession
from app.api.schemas.study_sessions import (
    StudySessionResponse, StudySessionCreate, StudySessionUpdate
)

router = APIRouter()


@router.post("/", response_model=StudySessionResponse)
async def create_study_session(
    session_data: StudySessionCreate,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    session = StudySession(
        title=session_data.title,
        description=session_data.description,
        user_id=current_user.id
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session


@router.get("/", response_model=List[StudySessionResponse])
async def get_study_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(StudySession).filter(
        StudySession.user_id == current_user.id
    ).order_by(StudySession.created_at.desc()).offset(skip).limit(limit).all()
    
    return sessions


@router.get("/{session_id}", response_model=StudySessionResponse)
async def get_study_session(
    session_id: int,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    return session


@router.put("/{session_id}", response_model=StudySessionResponse)
async def update_study_session(
    session_id: int,
    session_update: StudySessionUpdate,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    if session_update.title is not None:
        session.title = session_update.title
    if session_update.description is not None:
        session.description = session_update.description
    if session_update.notes is not None:
        session.notes = session_update.notes
    
    db.commit()
    db.refresh(session)
    
    return session


@router.post("/{session_id}/complete")
async def complete_study_session(
    session_id: int,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    session.completed_at = datetime.utcnow()
    
    # Calculate duration if not set
    if not session.duration_minutes and session.completed_at:
        duration = session.completed_at - session.created_at
        session.duration_minutes = int(duration.total_seconds() / 60)
    
    db.commit()
    
    return {"message": "Study session completed successfully"}


@router.delete("/{session_id}")
async def delete_study_session(
    session_id: int,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    db.delete(session)
    db.commit()
    
    return {"message": "Study session deleted successfully"}
