import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, ConfigDict
from typing import ClassVar
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAG Weaviate Chatbot"
    DEBUG: bool = bool(os.getenv("DEBUG", False))
    
    DATABASE_URL: PostgresDsn = Field(
        default=f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
                f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    
    SECRET_KEY: str = os.getenv("AUTH_SECRET_KEY", "secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    WEAVIATE_URL: str = os.getenv("WEAVIATE_URL", "http://localhost:8080")
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    PROCESS_FILE_API_KEY: str = os.getenv("PROCESS_FILE_API_KEY")
    
    pwd_context: ClassVar[CryptContext] = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme: ClassVar[OAuth2PasswordBearer] = OAuth2PasswordBearer(tokenUrl="auth/token")
    api_key_header: ClassVar[APIKeyHeader] = APIKeyHeader(name="X-API-Key")
    
    model_config = ConfigDict(case_sensitive=True)

settings = Settings()