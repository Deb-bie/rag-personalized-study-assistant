from app.api.dependencies import get_db
from fastapi import APIRouter, Depends, HTTPException, status # type: ignore
from fastapi.security import OAuth2PasswordRequestForm # type: ignore
from sqlalchemy.orm import Session # type: ignore
from datetime import timedelta
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.models.user import User
from app.api.schemas.user import AuthResponse, UserCreate

router = APIRouter()

@router.post("/register", response_model=AuthResponse)
async def register(
    user_data: UserCreate, 
    db: Session = Depends(get_db)
):
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    
    return {
        "email": db_user.email,
        "username": db_user.username,
        "access_token": access_token, 
        "token_type": "bearer"
    }
    
    # return db_user


@router.post("/login", response_model=AuthResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "email": user.email,
        "username": user.username,
        "access_token": access_token, 
        "token_type": "bearer"
    }
