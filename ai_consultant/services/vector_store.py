import os
import logging
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from django.conf import settings

logger = logging.getLogger(__name__)

class VectorStoreService:
    """
    Service for interacting with the ChromaDB vector store.
    Handles initialization, collection management, and basic add/query operations.
    """
    
    _instance = None
    _client = None
    _embedding_function = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStoreService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._initialize_client()

    def _initialize_client(self):
        """
        Initialize the ChromaDB client and embedding function.
        """
        try:
            # Persist data in a 'chroma_db' directory within the project
            persist_directory = os.path.join(settings.BASE_DIR, 'chroma_db')
            
            self._client = chromadb.PersistentClient(path=persist_directory)
            
            # Use a lightweight, high-performance model
            self._embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            
            logger.info(f"VectorStoreService initialized. Persisting to: {persist_directory}")
            
        except Exception as e:
            logger.error(f"Failed to initialize VectorStoreService: {e}")
            raise

    def get_collection(self, name: str):
        """
        Get or create a collection by name.
        """
        try:
            return self._client.get_or_create_collection(
                name=name,
                embedding_function=self._embedding_function
            )
        except Exception as e:
            logger.error(f"Error getting collection '{name}': {e}")
            raise

    def add_documents(self, collection_name: str, documents: list, metadatas: list, ids: list):
        """
        Add documents to a specific collection.
        """
        try:
            collection = self.get_collection(collection_name)
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to collection '{collection_name}'")
        except Exception as e:
            logger.error(f"Error adding documents to '{collection_name}': {e}")
            raise

    def query(self, collection_name: str, query_text: str, n_results: int = 3):
        """
        Query a collection for similar documents.
        """
        try:
            collection = self.get_collection(collection_name)
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"Error querying collection '{collection_name}': {e}")
            return None

    def delete_collection(self, name: str):
        """
        Delete a collection.
        """
        try:
            self._client.delete_collection(name)
            logger.info(f"Deleted collection '{name}'")
        except Exception as e:
            logger.error(f"Error deleting collection '{name}': {e}")
