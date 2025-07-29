from app.core.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean # type: ignore
from sqlalchemy.orm import relationship # type: ignore
from sqlalchemy.sql import func # type: ignore

class User(Base):
    __tablename__ = "users"
    
    id = Column(
        Integer, 
        primary_key=True, 
        index=True
    )
    
    email = Column(
        String, 
        unique=True, 
        index=True, 
        nullable=False
    )
    
    username = Column(
        String, 
        index=True, 
        nullable=False
    )
    
    password = Column(
        String, 
        nullable=False
    )
    
    is_active = Column(
        Boolean, 
        default=True
    )
    
    is_verified = Column(
        Boolean, 
        default=False
    )
    
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    updated_at = Column(
        DateTime(timezone=True), 
        onupdate=func.now()
    )
    
    # Relationships
    documents = relationship(
        "Document", 
        back_populates="owner"
    )
    
    study_sessions = relationship(
        "StudySession", 
        back_populates="user"
    )
    
    chat_sessions = relationship(
        "ChatSession", 
        back_populates="user"
    )