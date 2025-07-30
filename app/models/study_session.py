from app.core.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Float # type: ignore
from sqlalchemy.orm import relationship # type: ignore
from sqlalchemy.sql import func # type: ignore

class StudySession(Base):
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    duration_minutes = Column(Integer)
    topics_covered = Column(JSON)  # List of topics
    performance_metrics = Column(JSON)  # Quiz scores, etc.
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="study_sessions")
    activities = relationship("StudyActivity", back_populates="session")


class StudyActivity(Base):
    __tablename__ = "study_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("study_sessions.id"))
    activity_type = Column(String, nullable=False)  # 'quiz', 'flashcard', 'reading'
    content = Column(JSON)  # Activity-specific data
    score = Column(Float)
    time_spent_minutes = Column(Integer)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("StudySession", back_populates="activities")