from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import models, schemas, security
from .db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=schemas.UserPublic)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(
        email=user_in.email,
        hashed_password=security.hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=schemas.TokenPair)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form.username).first()
    if not user or not security.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access = security.create_token(
        {"sub": str(user.id), "ver": user.token_version, "type": "access"},
        expires_delta=timedelta(minutes=security.ACCESS_MIN),
    )
    refresh = security.create_token(
        {"sub": str(user.id), "ver": user.token_version, "type": "refresh"},
        expires_delta=timedelta(days=security.REFRESH_DAYS),
    )
    return schemas.TokenPair(
        access_token=access,
        refresh_token=refresh,
        expires_in=security.ACCESS_MIN * 60,
    )
from .deps import get_current_user

@router.post("/logout", status_code=204)
def logout(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Invalidate all existing tokens by incrementing token_version
    current_user.token_version += 1
    db.add(current_user)
    db.commit()
    return
