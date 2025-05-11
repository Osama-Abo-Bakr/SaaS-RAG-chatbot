from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from ..config import settings
from src.db.db_connection import get_user_by_username
from src.schemas.auth import TokenData, User, UserInDB

# Security setups
pwd_context = settings.pwd_context
oauth2_scheme = settings.oauth2_scheme
api_key_header = settings.api_key_header

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate a user by verifying their username and password.

    Args:
        username (str): The username of the user attempting to authenticate.
        password (str): The password provided by the user for authentication.

    Returns:
        Optional[UserInDB]: The authenticated UserInDB object if authentication is successful,
        otherwise None if authentication fails.
    """

    user = get_user_by_username(username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create an access token for a user.

    Args:
        data (dict): The data to be encoded in the token.
        expires_delta (timedelta | None, optional): The time delta for the token to expire.
            If not provided, the token will expire in 15 minutes. Defaults to None.

    Returns:
        str: The access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """
    Get the current user based on the provided Bearer token.

    Args:
        token (Annotated[str, Depends(oauth2_scheme)]]): The Bearer token to authenticate.

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: When the token is invalid or the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def require_role(required_role: str):
    """
    Requires the user to have a certain role to access the endpoint.

    Args:
        required_role (str): The required role.

    Returns:
        A dependency that checks the role of the user and raises an HTTPException if the user's role does not match the required role.
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker