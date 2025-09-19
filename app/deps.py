from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from .db import get_db
from . import models, security

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.decode_token(token)
        user_id = int(payload.get("sub"))
        token_ver = int(payload.get("ver"))
    except (JWTError, ValueError):
        raise credentials_exc

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or user.token_version != token_ver:
        raise credentials_exc
    return user
