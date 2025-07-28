from app.core.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON # type: ignore
from sqlalchemy.orm import relationship # type: ignore
from sqlalchemy.sql import func # type: ignore



class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(
        Integer, 
        primary_key=True, 
        index=True
    )
    
    title = Column(
        String, 
        default="New Chat"
    )
    
    user_id = Column(
        Integer, 
        ForeignKey("users.id")
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
    user = relationship(
        "User", 
        back_populates="chat_sessions"
    )
    
    messages = relationship(
        "ChatMessage", 
        back_populates="session"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(
        Integer, 
        primary_key=True, 
        index=True
    )
    
    session_id = Column(
        Integer, 
        ForeignKey("chat_sessions.id")
    )
    
    role = Column(
        String, 
        nullable=False
    )  # 'user' or 'assistant'
    
    content = Column(
        Text, 
        nullable=False
    )
    
    sources = Column(JSON)  # Referenced documents/chunks
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")