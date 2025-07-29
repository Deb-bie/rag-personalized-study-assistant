from pydantic import BaseModel # type: ignore
from datetime import datetime
from typing import Optional, List, Dict, Any


class StudySessionBase(BaseModel):
    title: str
    description: Optional[str] = None


class StudySessionCreate(StudySessionBase):
    pass


class StudySessionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class StudySessionResponse(StudySessionBase):
    id: int
    user_id: int
    duration_minutes: Optional[int]
    topics_covered: Optional[List[str]]
    performance_metrics: Optional[Dict[str, Any]]
    notes: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True