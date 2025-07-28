from app.api.dependencies import get_active_user, get_db
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query # type: ignore
from sqlalchemy.orm import Session # type: ignore
from typing import List
from app.models.user import User
from app.models.document import Document
from app.api.schemas.document import DocumentResponse, DocumentUpdate
from app.services.document_service import DocumentService
from app.core.exceptions import DocumentProcessingError

router = APIRouter()
document_service = DocumentService()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    try:
        document = await document_service.upload_document(file, current_user.id, db)
        return document
    except DocumentProcessingError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    documents = document_service.get_user_documents(
        current_user.id, db, skip, limit
    )
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document_update.title is not None:
        document.title = document_update.title
    
    db.commit()
    db.refresh(document)
    return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    try:
        success = document_service.delete_document(document_id, current_user.id, db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        return {"message": "Document deleted successfully"}
    except DocumentProcessingError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))