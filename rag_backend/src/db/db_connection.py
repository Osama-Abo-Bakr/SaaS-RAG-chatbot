import os
import logging
import json
from typing import Optional, List
from ..config import settings
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from fastapi import HTTPException, status
from src.schemas.auth import UserInDB, UserCreate

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_database_url():
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    if None in [db_user, db_password, db_host, db_port, db_name]:
        raise ValueError("❌ Missing database environment variables!")

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Database configuration
DATABASE_URL = get_database_url()

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# Create session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db_connection():
    """
    Provides a new database session from the connection pool.
    """
    try:
        db = SessionLocal()
        logging.info("✅ PostgreSQL database session acquired")
        return db
    except Exception as e:
        logging.error(f"❌ Error acquiring database session: {e}")
        return None

def get_chat_history(vector_id):
    """
    Retrieve the chat history for a given vector_id.
    """
    db = get_db_connection()
    if not db:
        logging.error("❌ Database session failed. Cannot retrieve chat history.")
        return []
    try:
        result = db.execute(
            text("""
                SELECT chat_history
                FROM chat_history
                WHERE vector_id = :vector_id
                ORDER BY timestamp DESC
            """),
            {"vector_id": vector_id}
        ).fetchone()
        return result[0] if result else []
    except Exception as e:
        logging.error(f"❌ Error retrieving chat history: {e}")
        return []
    finally:
        db.close()
        

def delete_chat_history(vector_id: str) -> bool:
    """
    Delete the chat history for a given vector_id from the database.

    Args:
        vector_id (str): The ID of the vector whose chat history is to be deleted.

    Returns:
        bool: True if the chat history was successfully deleted, False otherwise.
    """
    db = get_db_connection()
    if not db:
        logging.error("❌ Database session failed. Cannot delete chat history.")
        return False
    try:
        db.execute(text("DELETE FROM chat_history WHERE vector_id = :vector_id"), {"vector_id": vector_id})
        db.commit()
        logging.info("✅ Chat history deleted successfully (PostgreSQL).")
        return True
    except Exception as e:
        logging.error(f"❌ Error deleting chat history: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def get_user_chats(user_id: str) -> List[dict]:
    """
    Retrieve all chats for a given user.
    
    Args:
        user_id (str): The ID of the user whose chats are to be retrieved.
    
    Returns:
        List[dict]: List of chat records containing project_name, vector_id, and timestamp.
    """
    db = get_db_connection()
    if not db:
        logging.error("❌ Database session failed. Cannot retrieve user chats.")
        return []
    try:
        result = db.execute(
            text("""
                SELECT project_name, vector_id, chat_history, timestamp
                FROM chat_history
                WHERE user_name = :user_id
                ORDER BY timestamp DESC
            """),
            {"user_id": user_id}
        ).fetchall()
        return [
            {
                "project_name": row.project_name,
                "vector_id": row.vector_id,
                "chat_history": row.chat_history,
                "timestamp": row.timestamp.isoformat()
            } for row in result
        ]
    except Exception as e:
        logging.error(f"❌ Error retrieving user chats: {e}")
        return []
    finally:
        db.close()

def save_chat_history(chat_history, user_name, project_name, vector_id):
    """
    Save or update the chat history for a given vector_id in the database.
    """
    db = get_db_connection()
    if not db:
        logging.error("❌ Database session failed. Chat history not saved.")
        return
    try:        
        db.execute(
            text("""
                INSERT INTO chat_history (user_name, project_name, vector_id, chat_history)
                VALUES (:user_name, :project_name, :vector_id, :chat_history)
                ON CONFLICT (vector_id) 
                DO UPDATE SET chat_history = EXCLUDED.chat_history
            """),
            {"user_name": user_name, "project_name": project_name, "vector_id": vector_id, "chat_history": json.dumps(chat_history)}
        )
        db.commit()
        logging.info("✅ Chat history saved successfully (PostgreSQL with JSONB).")
    except Exception as e:
        logging.error(f"❌ Error saving chat history: {e}")
        db.rollback()
    finally:
        db.close()

def get_user_by_username(username: str) -> Optional[UserInDB]:
    """
    Retrieve a user from the database by their username.
    """
    db = get_db_connection()
    try:
        result = db.execute(
            text("SELECT * FROM users WHERE username = :username"),
            {"username": username}
        ).fetchone()
        
        if result:
            return UserInDB(
                id=result.id,
                username=result.username,
                email=result.email,
                role=result.role,
                disabled=result.disabled,
                hashed_password=result.hashed_password
            )
        return None
    finally:
        db.close()

def create_user(user: UserCreate) -> UserInDB:
    """
    Create a new user in the database.
    """
    db = get_db_connection()
    try:
        pwd_context = settings.pwd_context
        hashed_password = pwd_context.hash(user.password)
        result = db.execute(
            text("""
                INSERT INTO users (username, email, hashed_password, role)
                VALUES (:username, :email, :hashed_password, :role)
                RETURNING id, username, email, role, disabled, hashed_password
            """),
            {
                "username": user.username,
                "email": user.email,
                "hashed_password": hashed_password,
                "role": user.role
            }
        )
        db.commit()
        row_data = result.fetchone()
        return UserInDB(
            id=row_data[0],
            username=row_data[1],
            email=row_data[2],
            role=row_data[3], 
            disabled=row_data[4], 
            hashed_password=row_data[5]
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    finally:
        db.close()

def create_all_tables():
    """
    Creates all the tables required for the auth and chat history.
    """
    db = get_db_connection()
    try:
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT UNIQUE,
                hashed_password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                disabled BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                user_name TEXT NOT NULL,
                project_name TEXT NOT NULL,
                vector_id TEXT NOT NULL UNIQUE,
                chat_history JSONB NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        db.commit()
        logging.info("✅ `Authentication`, , `Refresh Tokens`, and `Chat History` tables created successfully")
    except Exception as e:
        logging.error(f"❌ Error creating auth tables: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def delete_all_tables():
    """
    Deletes all tables related to authentication and chat history if they exist.
    """
    db = get_db_connection()
    if not db:
        logging.error("❌ Database session failed. Cannot delete table.")
        return
    try:
        db.execute(text("DROP TABLE IF EXISTS chat_history"))
        db.execute(text("DROP TABLE IF EXISTS users"))
        db.commit()
        logging.info("✅ Table 'chat_history', 'users', 'api_keys', deleted successfully (PostgreSQL).")
    except Exception as e:
        logging.error(f"❌ Error deleting table: {e}")
    finally:
        db.close()

def create_initial_admin():
    """
    Create initial admin user if it doesn't exist.
    """
    db = get_db_connection()
    try:
        admin = db.execute(
            text("SELECT * FROM users WHERE username = 'admin'")
        ).fetchone()
        
        if not admin:
            hashed_password = settings.pwd_context.hash(os.getenv("DEFAULT_ADMIN_PASSWORD"))
            db.execute(
                text("""
                    INSERT INTO users (username, email, hashed_password, role)
                    VALUES ('admin', 'admin@admin.com', :password, 'admin')
                    RETURNING id, username, email, role, disabled
                """),
                {"password": hashed_password}
            )
            db.commit()
            logging.info("✅ Initial admin user created")
    except Exception as e:
        logging.error(f"❌ Startup error: {e}")
        db.rollback()
    finally:
        db.close()