import os
from fastapi import FastAPI, HTTPException # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from contextlib import asynccontextmanager
from app.api.routes.api_router import router as api_router
from app.core.config import settings
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass


app = FastAPI(
    title="RAG-Based Personal Study Assistant API",
    description="A personal study assistant with RAG capabilities",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": "RAG Study Assistant API", 
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }


if __name__ == "__main__":
    import uvicorn # type: ignore

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
