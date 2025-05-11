# RAG Weaviate Chatbot

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

The **RAG Weaviate Chatbot** is an AI-powered chatbot that leverages Retrieval-Augmented Generation (RAG) with Weaviate as the vector database to provide intelligent responses based on uploaded documents. Built with FastAPI, it includes user authentication, file ingestion, chat functionality, and chat history management, making it suitable for document-based question-answering applications.

---

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Authentication](#authentication)
- [Database Management](#database-management)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Features

- **User Authentication**: Secure registration and login with JWT tokens.
- **File Ingestion**: Supports multiple document types (PDF, DOCX, EPUB, TXT, PPTX, XLSX, CSV).
- **Chat Functionality**: Provides responses based on document content using RAG.
- **Chat History**: Stores and retrieves chat history per user and project.
- **Vector Database**: Utilizes Weaviate for efficient vector storage and retrieval.
- **Role-Based Access**: Basic support for user roles (e.g., admin, user).

---

## Technologies Used

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **Databases**:
  - [PostgreSQL](https://www.postgresql.org/) for user data and chat history
  - [Weaviate](https://weaviate.io/) for vector storage
- **Authentication**: JWT tokens with OAuth2
- **File Processing**: Libraries like `PyPDFLoader`, `Docx2txtLoader`, etc.
- **NLP and AI**:
  - [LangChain](https://langchain.com/)
  - [Cohere](https://cohere.ai/)
  - [Google Generative AI](https://cloud.google.com/ai/generative-ai)
- **Other**:
  - [SQLAlchemy](https://www.sqlalchemy.org/) for ORM
  - [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation

---

## Installation

Follow these steps to set up the project locally:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Osama-Abobakr/SaaS-RAG-chatbot.git
   cd SaaS-RAG-chatbot
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the root directory with the variables listed in the [Configuration](#configuration) section.

5. **Set Up Weaviate**:
   Ensure Weaviate is running locally or accessible:
   ```bash
   docker run -d -p 8080:8080 semitechnologies/weaviate:latest
   ```

6. **Set Up PostgreSQL**:
   Install and run PostgreSQL, then create a database:
   ```sql
   CREATE DATABASE rag_chatbot;
   ```

7. **Run the Application**:
   ```bash
   uvicorn main:app --reload
   ```

---

## Configuration

The project relies on environment variables. Create a `.env` file with the following:

```env
# Database Configuration
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=port
DB_NAME=rag_chatbot

# Authentication
AUTH_SECRET_KEY=your_secret_key
DEFAULT_ADMIN_PASSWORD=admin_password

# API Keys
COHERE_API_KEY=your_cohere_api_key
GOOGLE_API_KEY=your_google_api_key
PROCESS_FILE_API_KEY=your_process_file_api_key

# Weaviate
WEAVIATE_URL=http://localhost:8080
```

Ensure all variables are set correctly for your setup.

---

## Usage

The API provides endpoints for authentication, data ingestion, chatting, and database management. Below are examples:

### Authentication

- **Register a User**:
  ```bash
  curl -X POST http://localhost:8000/auth/register \
    -H "Content-Type: application/json" \
    -d '{"username": "john", "email": "john@example.com", "password": "secret"}'
  ```

- **Login to Get Token**:
  ```bash
  curl -X POST http://localhost:8000/auth/token \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=john&password=secret"
  ```

### Data Ingestion

- **Upload Files**:
  ```bash
  curl -X POST http://localhost:8000/data-ingest \
    -H "Authorization: Bearer <token>" \
    -F "project_name=project123" \
    -F "files_data=@example.pdf"
  ```

### Chat

- **Ask a Question**:
  ```bash
  curl -X POST http://localhost:8000/chat \
    -H "Authorization: Bearer <token>" \
    -F "user_query=What is in the document?" \
    -F "project_name=project123"
  ```

### Database Management

- **Delete Vector Database**:
  ```bash
  curl -X POST http://localhost:8000/delete-vector-db \
    -H "Authorization: Bearer <token>" \
    -F "project_name=project123"
  ```

- **Get User Chats**:
  ```bash
  curl -X GET http://localhost:8000/get_chats \
    -H "Authorization: Bearer <token>"
  ```

For more examples, see `test.ipynb` or access the API docs at `http://localhost:8000/docs`.

---

## Authentication

Authentication uses JWT tokens. Register a user, log in to obtain a token, and include it in the `Authorization` header (`Bearer <token>`) for protected endpoints.

---

## Database Management

- **PostgreSQL**: Stores user data and chat history in tables like `users` and `chat_history`.
- **Weaviate**: Manages vector embeddings for document retrieval.

Tables are created automatically on startup, and an initial admin user is set up with the password from `DEFAULT_ADMIN_PASSWORD`.

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a branch for your changes.
3. Submit a pull request with a clear description.

Ensure your code adheres to the project's standards and includes tests.

---

## License

This project is licensed under the MIT License. See the [LICENSE]("./LLICENSE") file for details.

---

## Contact

For inquiries or issues, contact the team at [osamaoabobakr12@gmail.com](mailto:osamaoabobakr12@gmail.com).

---