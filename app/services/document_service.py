from typing import List, Optional
import os
import shutil
from pathlib import Path
from sqlalchemy.orm import Session # type: ignore
from fastapi import UploadFile # type: ignore

from app.models.document import Document, DocumentChunk
from app.rag.document_processor import DocumentProcessor
from app.rag.chunking import TextChunker
from app.services.vector_store_service import VectorStoreService
from app.services.llm_service import LLMService
from app.core.config import settings
from app.core.exceptions import DocumentProcessingError


class DocumentService:
    def __init__(self):
        self.processor = DocumentProcessor()
        self.chunker = TextChunker()
        self.vector_store = VectorStoreService()
        self.llm_service = LLMService()
    
    async def upload_document(
        self,
        file: UploadFile,
        user_id: int,
        db: Session
    ) -> Document:
        try:
            # Validate file
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in settings.ALLOWED_FILE_TYPES:
                raise DocumentProcessingError(f"File type {file_extension} not supported")
            
            # Create upload directory if it doesn't exist
            upload_dir = Path(settings.UPLOAD_DIR)
            upload_dir.mkdir(exist_ok=True)
            
            # Save file
            file_path = upload_dir / f"{user_id}_{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Create document record
            document = Document(
                title=file.filename,
                filename=file.filename,
                file_path=str(file_path),
                file_type=file_extension,
                file_size=file_path.stat().st_size,
                owner_id=user_id,
                processing_status="pending"
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            # Process document asynchronously (in a real app, use Celery)
            await self.process_document(document.id, db)
            
            return document
            
        except Exception as e:
            raise DocumentProcessingError(f"Error uploading document: {str(e)}")
    
    async def process_document(self, document_id: int, db: Session) -> bool:
        try:


            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise DocumentProcessingError("Document not found")
            
            # Update status
            document.processing_status = "processing"
            db.commit()
            
            # Extract text
            text_content = self.processor.extract_text(
                document.file_path,
                document.file_type
            )

            if not text_content.strip():
                document.processing_status = "failed"
                db.commit()
                raise DocumentProcessingError("Extracted document content is empty. Cannot proceed.")
            
            # Generate summary
            summary = await self.llm_service.generate_summary(text_content)
            
            # Update document with content and summary
            document.content = text_content
            document.summary = summary
            
            # Chunk the document
            chunks = self.chunker.chunk_text(text_content, document_id)
            
            # Save chunks to database
            for chunk_data in chunks:
                chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_text=chunk_data["text"],
                    chunk_index=chunk_data["chunk_index"]
                )
                db.add(chunk)
            
            # Add to vector store
            vector_docs = []
            for chunk_data in chunks:
                vector_docs.append({
                    "content": chunk_data["text"],
                    "document_id": document_id,
                    "title": document.title,
                    "chunk_index": chunk_data["chunk_index"]
                })
            
            await self.vector_store.add_documents(vector_docs, document.owner_id)
            
            # Update processing status
            document.is_processed = True
            document.processing_status = "completed"
            
            db.commit()
            return True
            
        except Exception as e:
            # Update status to failed
            if document:
                document.processing_status = "failed"
                db.commit()
            raise DocumentProcessingError(f"Error processing document: {str(e)}")
    
    def get_user_documents(
        self,
        user_id: int,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        return db.query(Document).filter(
            Document.owner_id == user_id
        ).offset(skip).limit(limit).all()
    
    def delete_document(self, document_id: int, user_id: int, db: Session) -> bool:
        try:
            document = db.query(Document).filter(
                Document.id == document_id,
                Document.owner_id == user_id
            ).first()
            
            if not document:
                return False
            
            # Delete file
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
            
            # Delete from database (cascades to chunks)
            db.delete(document)
            db.commit()
            
            return True
            
        except Exception as e:
            raise DocumentProcessingError(f"Error deleting document: {str(e)}")