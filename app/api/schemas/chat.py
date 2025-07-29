from pydantic import BaseModel # type: ignore
from datetime import datetime
from typing import List, Optional, Dict, Any


class ChatMessageBase(BaseModel):
    content: str


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageResponse(ChatMessageBase):
    id: int
    role: str
    sources: Optional[List[Dict[str, Any]]] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ChatSessionBase(BaseModel):
    title: Optional[str] = "New Chat"


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionResponse(ChatSessionBase):
    id: int
    user_id: int
    created_at: datetime
    messages: List[ChatMessageResponse] = []
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    context_documents: Optional[List[int]] = None


class ChatResponse(BaseModel):
    message: str
    sources: List[Dict[str, Any]]
    session_id: int