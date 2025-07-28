from app.api.routes.endpoints import auth, chat, documents, knowledge_base, study_sessions, users
from fastapi import APIRouter # type: ignore

router = APIRouter()

router.include_router(
    auth.router, 
    prefix="/api/v1/auth", 
    tags=["auth"]
)

router.include_router(
    users.router, 
    prefix="/api/v1/users", 
    tags=["users"]
)

router.include_router(
    documents.router, 
    prefix="/api/v1/documents", 
    tags=["documents"]
)

router.include_router(
    chat.router, 
    prefix="/api/v1/chat", 
    tags=["chat"]
)

router.include_router(
    study_sessions.router, 
    prefix="/api/v1/study-sessions", 
    tags=["study-sessions"]
)

router.include_router(
    knowledge_base.router, 
    prefix="/api/v1/knowledge-base", 
    tags=["knowledge-base"]
)