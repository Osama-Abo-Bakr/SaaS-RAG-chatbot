from enum import Enum
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None

class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None

class User(BaseModel):
    id: int
    username: str
    email: str | None = None
    role: str = "user"
    disabled: bool = False

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserInDB(User):
    hashed_password: str
    role: UserRole

class UserCreate(BaseModel):
    username: str
    email: str | None = None
    password: str
    role: str = "user"