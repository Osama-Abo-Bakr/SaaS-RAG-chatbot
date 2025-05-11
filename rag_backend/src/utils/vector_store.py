import re
import logging
import weaviate
from typing import Tuple
from ..config import settings
from langchain_core.documents import Document
from langchain_weaviate import WeaviateVectorStore
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings

logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.GOOGLE_API_KEY
        )

    def _sanitize_property_name(self, name: str) -> str:
        """Convert property names to Weaviate-compatible format."""
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        if not re.match(r'^[_a-zA-Z]', name):
            name = '_' + name
        return name

    def _clean_metadata(self, metadata: dict) -> dict:
        """Recursively clean all metadata keys."""
        cleaned = {}
        for key, value in metadata.items():
            new_key = self._sanitize_property_name(key)
            if isinstance(value, dict):
                cleaned[new_key] = self._clean_metadata(value)
            else:
                cleaned[new_key] = value
        return cleaned

    def load_vector_db(self, vector_store_id: str) -> Tuple[WeaviateVectorStore, weaviate.Client]:
        """
        Load a Weaviate vector store by ID.

        Args:
            vector_store_id: The ID of the vector store to load.

        Returns:
            A tuple containing the loaded WeaviateVectorStore and the weaviate.Client.

        Raises:
            Exception: If the vector store cannot be loaded.
        """
        try:
            logger.info(f"🔃 Loading vector store: {vector_store_id}")
            client = weaviate.connect_to_local()
            vector_db = WeaviateVectorStore(
                client=client,
                index_name=vector_store_id,
                text_key='text',
                embedding=self.embeddings
            )
            return vector_db, client
        except Exception as e:
            logger.error(f"❌ Failed to load vector store: {str(e)}")
            raise 

    def add_documents(self, vector_store_id: str, documents: list[Document]) -> WeaviateVectorStore:
        """
        Adds documents to a Weaviate vector store.

        This method cleans the metadata of the provided documents, checks if the vector store
        exists in Weaviate, and either creates a new vector store or adds the documents to the
        existing vector store.

        Args:
            vector_store_id (str): The ID of the vector store to which documents are added.
            documents (list[Document]): A list of Document objects to be added to the vector store.

        Returns:
            WeaviateVectorStore: The Weaviate vector store containing the added documents.

        Raises:
            Exception: If there is an error adding the documents to the vector store.
        """
        try:
            # Clean all documents' metadata before processing
            for doc in documents:
                if hasattr(doc, 'metadata') and doc.metadata:
                    doc.metadata = self._clean_metadata(doc.metadata)

            client = weaviate.connect_to_local()
            
            if not client.collections.exists(vector_store_id):
                logger.info(f"🚩Creating new vector store: {vector_store_id}")
                vector_db = WeaviateVectorStore.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    client=client,
                    index_name=vector_store_id,
                    by_text=False
                )
            else:
                logger.info(f"➕ Adding to existing vector store: {vector_store_id}")
                vector_db = WeaviateVectorStore(
                    client=client,
                    index_name=vector_store_id,
                    text_key="text",
                    embedding=self.embeddings
                )
                vector_db.add_documents(documents=documents)
            
            return vector_db
        except Exception as e:
            logger.error(f"❌ Failed to add documents to vector store: {str(e)}")
            raise 
        finally:
            client.close()

    def delete_vector_db(self, vector_store_id: str) -> None:
        """
        Deletes a vector store from the Weaviate database.

        Args:
            vector_store_id (str): The ID of the vector store to delete.

        Raises:
            Exception: If the vector store cannot be deleted.
        """
        try:
            logger.info(f"🕳️ Deleting vector store: {vector_store_id}")
            client = weaviate.connect_to_local()
            client.collections.delete(vector_store_id)
        except Exception as e:
            logger.error(f"❌ Failed to delete vector store: {str(e)}")
            raise 
        finally:
            client.close()

vector_store_service = VectorStoreService()