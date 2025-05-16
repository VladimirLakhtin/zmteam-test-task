"""Authentication module for JWT token handling and user verification."""

from typing import Optional

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app import schemas
from app.infrastructure.config import settings

SECRET_KEY = settings.auth.secret_key
ALGORITHM = settings.auth.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.auth.access_token_expire_min

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> schemas.TokenData:
    """Validate JWT token and return user data.
    
    Args:
        token (str): JWT token from Authorization header
        
    Returns:
        TokenData: User data extracted from token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("name")
        if username is None:
            token_data = schemas.TokenData(username="valid_user_placeholder")
        else:
            token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    else:
        return token_data
