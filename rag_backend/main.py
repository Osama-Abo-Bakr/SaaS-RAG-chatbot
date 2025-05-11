import os
import hashlib
from datetime import timedelta
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, Form, File, APIRouter, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from src.utils.rag_chain import RAG_Chain
from src.utils.file_processing import FileProcessor
from src.utils.vector_store import vector_store_service
from src.db.db_connection import create_user, get_user_chats, create_initial_admin, delete_chat_history
from src.schemas.auth import Token, UserCreate
from src.auth.auth import (
    User, UserInDB, get_current_user, 
    create_access_token, authenticate_user
)

_ = load_dotenv(override=True)

app = FastAPI(
    debug=True,
    title="RAG - Weaviate Chatbot",
    version="1.0.0",
    description="Building SaaS App about RAG - Weaviate Chatbot"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create auth router
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

def generate_vector_store_id(user_id: str, project_id: str) -> str:
    """
    Generate a unique vector store ID based on user ID and project ID.
    """
    unique_string = f"{user_id}_{project_id}"
    return f"RAG_{hashlib.sha256(unique_string.encode()).hexdigest()}"

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/data-ingest")
async def add_data_weaviate(files_data: List[UploadFile] = File(...), 
                            project_name: str = Form(...),
                            current_user: User = Depends(get_current_user)
                            ):
    """
    API endpoint to ingest data into Weaviate vector store.

    This endpoint accepts a list of files and a project name, and ingests the data into the
    Weaviate vector store. The vector store ID is generated based on the username and project name.
    The data is processed using the FileProcessor class, and the resulting documents are added
    to the vector store using the VectorStoreService class.

    Args:
        files_data (List[UploadFile]): A list of files to be ingested.
        project_name (str): The name of the project to which the data belongs.
        current_user (User): The currently logged-in user.

    Returns:
        A JSON response with a message indicating whether the data ingestion was successful or not.

    Raises:
        HTTPException: If there is an error during data ingestion.
    """
    temp_file_paths = []
    try:
        vector_store_id = generate_vector_store_id(current_user.username, project_name)
        
        for uploaded_file in files_data:
            temp_file_path = os.path.join(os.getcwd(), uploaded_file.filename)
            temp_file_paths.append(temp_file_path)
            
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(await uploaded_file.read())

        if len(temp_file_paths) >=30:
            _ = [os.remove(path) for path in temp_file_paths if os.path.exists(path)]
            raise Exception("❌ You can't upload more than 30 files at a time")
        
        documents = FileProcessor().load_files(temp_file_paths)
        _ = vector_store_service.add_documents(vector_store_id=vector_store_id, documents=documents)
        
        _ = [os.remove(path) for path in temp_file_paths if os.path.exists(path)]
        return {"message": f"✅ {len(files_data)} Files Ingested Successfully!"}
    
    except Exception as e:
        _ = [os.remove(path) for path in temp_file_paths if os.path.exists(path)]
        raise HTTPException(status_code=500, detail=f"Error In Data Ingestion {str(e)}")

@app.post("/chat")
async def chatbot_response(user_query: str = Form(...),  
                           project_name: str = Form(...),
                           current_user: User = Depends(get_current_user)
                           ):
    
    """
    Endpoint to get a response from the chatbot.

    Args:
        user_query (str): The user's query to the chatbot.
        project_name (str): The name of the project that the chatbot should respond with respect to.
        current_user (User): The currently authenticated user making the request.

    Returns:
        dict: A dictionary containing the chatbot's response as a string, and some additional metadata.

    Raises:
        HTTPException: If an error occurs during the chatbot response generation process.
    """
    try:
        vector_store_id = generate_vector_store_id(current_user.username, project_name)
        response = RAG_Chain.get_response(
            question=user_query,
            vector_store_id=vector_store_id,
            user_name=current_user.username,
            project_name=project_name
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error In Chatting Part: {str(e)}")
    
@app.post("/delete-vector-db")
async def delete_vector_db_endpoint(project_name: str = Form(...),
                                    current_user: User = Depends(get_current_user)
                                    ):
    
    """
    Endpoint to delete a vector database for a specified project.

    Args:
        project_name (str): The name of the project whose vector database is to be deleted.
        current_user (User): The current authenticated user making the request.

    Returns:
        dict: A message indicating the successful deletion of the vector database.

    Raises:
        HTTPException: If an error occurs during the deletion process.
    """
    try:
        vector_store_id = generate_vector_store_id(current_user.username, project_name)
        vector_store_service.delete_vector_db(vector_store_id=vector_store_id)
        if delete_chat_history(vector_id=vector_store_id):
            return {"message": "✅ Chat History Deleted Successfully!"}
        else: return {"message": "❌ Chat History Deletion Failed!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_chats")
async def get_user_chats_endpoint(current_user: User = Depends(get_current_user)):
    """Endpoint to retrieve all chats for the current user."""
    try:
        chats = get_user_chats(current_user.username)
        return {"chats": chats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chats: {str(e)}")

## ========================================================================================================##
## ===================================Authentication=======================================================##
## ========================================================================================================##

# Authentication endpoints
@auth_router.post("/register", response_model=UserInDB, status_code=201)
async def register_user(user_create: UserCreate):
    """Register a new user."""
    return create_user(user_create)

@auth_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Generate an access token for a user after they have provided their login credentials.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the username and password.

    Returns:
        dict: A dictionary containing the access token and token type.

    Raises:
        HTTPException: If the user is not found or the password is incorrect.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30.0)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Include the auth router
app.include_router(auth_router)

# Add initial admin creation on startup
@app.on_event("startup")
async def startup_event():
    create_initial_admin()