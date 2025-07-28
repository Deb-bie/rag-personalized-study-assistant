from pydantic import BaseModel # type: ignore
from datetime import datetime
from typing import Optional, List


class DocumentBase(BaseModel):
    title: str
    filename: str
    file_type: str


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: Optional[str] = None


class DocumentResponse(DocumentBase):
    id: int
    file_size: Optional[int]
    summary: Optional[str]
    is_processed: bool
    processing_status: str
    owner_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentChunkResponse(BaseModel):
    id: int
    chunk_text: str
    chunk_index: int
    
    class Config:
        from_attributes = True