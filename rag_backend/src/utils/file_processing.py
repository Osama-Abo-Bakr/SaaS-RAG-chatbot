import os
import logging
from ..config import settings
from typing import List
from google import genai
from google.genai import types
from langchain_core.documents import Document
from unstructured.partition.auto import partition
from unstructured.partition.pptx import partition_pptx
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader, 
    Docx2txtLoader, 
    UnstructuredEPubLoader, 
    TextLoader
)

logger = logging.getLogger(__name__)

class FileProcessor:
    def __init__(self):
        """
        Initializes a FileProcessor instance.

        Sets up a RecursiveCharacterTextSplitter to split documents into chunks of 2500
        characters, with a chunk overlap of 200 characters, and using double and single
        newlines as the separators.
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=2500,
            chunk_overlap=200,
            separators=["\n\n", "\n"]
        )
        
    def generate_tables_figures_summary(self, document_path):
        client = genai.Client(api_key=settings.PROCESS_FILE_API_KEY)
        files = [client.files.upload(file=document_path)]
        model = "gemini-2.0-flash"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(
                        file_uri=files[0].uri,
                        mime_type=files[0].mime_type,
                    ),
                    types.Part.from_text(text="""Explain All Figures and Tables in the document with Details and References"""),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(response_mime_type="text/plain")

        full_text = ""
        for chunk in client.models.generate_content_stream(model=model, contents=contents, config=generate_content_config):
            full_text += chunk.text + ""
            
        return full_text

    def load_files(self, file_paths: List[str]) -> List[Document]:
        """
        Load and process a list of files into documents.

        This function reads files from specified paths, processes them according
        to their file type, and returns a list of Document objects. Supported file
        types include PDF, DOCX, EPUB, TXT, PPTX, XLSX, and CSV. Unsupported file
        formats will raise a ValueError.

        Args:
            file_paths (List[str]): A list of file paths to load and process.

        Returns:
            List[Document]: A list of Document objects created from the loaded files.

        Raises:
            FileNotFoundError: If any file in the list does not exist.
            ValueError: If a file format is unsupported.
            Exception: If there is an error processing a file.
        """
        documents = []
        tables_figures_summary = []
        logger.info("Starting file processing")
        
        for path in file_paths:
            try:
                if not os.path.exists(path):
                    raise FileNotFoundError(f"File not found: {path}")
                
                filename = os.path.basename(path)
                ext = os.path.splitext(path)[1].lower()
                
                if ext == '.pdf':
                    loader = PyPDFLoader(file_path=path)
                    docs = loader.load()
                    
                    ## Add tables and figures summary
                    metadata = docs[0].metadata
                    metadata.pop("page", None)
                    metadata.pop("page_label", None)
                    tables_figures_summary = [Document(page_content=self.generate_tables_figures_summary(path), 
                                                       metadata=metadata)]
                                        
                elif ext == '.docx':
                    loader = Docx2txtLoader(file_path=path)
                    docs = loader.load()
                elif ext == '.epub':
                    loader = UnstructuredEPubLoader(file_path=path)
                    docs = loader.load()
                elif ext == '.txt':
                    loader = TextLoader(file_path=path)
                    docs = loader.load()
                elif ext == '.pptx':
                    parts = partition_pptx(path, include_slide_notes=True, chunking_strategy="by_title")
                    content = " ".join([str(part) for part in parts])
                    docs = [Document(page_content=content, metadata={"filename": filename})]
                elif ext in ['.xlsx', '.csv']:
                    parts = partition(path)
                    content = " ".join([part.metadata.text_as_html + "\n----\n" for part in parts])
                    docs = [Document(page_content=content, metadata={"filename": filename})]
                else:
                    raise ValueError(f"Unsupported file format: {ext}")
                
                documents.extend(docs)
                logger.info(f"Processed file: {filename}")
                
            except Exception as e:
                logger.error(f"Error processing file {path}: {str(e)}")
                raise 
        
        doc_splitter = self._split_documents(documents)
        doc_splitter.extend(tables_figures_summary)
        return doc_splitter

    def _split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split a list of documents into smaller chunks using a TextSplitter.

        Args:
        documents (List[Document]): The list of documents to be split.

        Returns:
        List[Document]: The list of split documents.

        Raises:
        Exception: If splitting fails.
        """
        try:
            return self.splitter.split_documents(documents)
        except Exception as e:
            logger.error(f"Error splitting documents: {str(e)}")
            raise