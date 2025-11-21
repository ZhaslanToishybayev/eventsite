import logging
from .vector_store import VectorStoreService
from clubs.models import Club

logger = logging.getLogger(__name__)

class DocumentIndexer:
    """
    Service for indexing documents into the vector store.
    Handles chunking and ingestion of different data sources.
    """
    
    def __init__(self):
        self.vector_store = VectorStoreService()

    def index_help_docs(self, docs: list):
        """
        Index a list of help documents.
        Each doc should be a dict with 'title', 'content', and 'source'.
        """
        documents = []
        metadatas = []
        ids = []
        
        for i, doc in enumerate(docs):
            # Simple chunking (can be improved)
            chunks = self._chunk_text(doc['content'])
            
            for j, chunk in enumerate(chunks):
                documents.append(chunk)
                metadatas.append({
                    'title': doc['title'],
                    'source': doc.get('source', 'help_doc'),
                    'type': 'help_doc'
                })
                ids.append(f"help_{i}_{j}")
        
        if documents:
            self.vector_store.add_documents(
                collection_name='help_docs',
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Indexed {len(documents)} chunks from {len(docs)} help docs.")

    def index_clubs(self):
        """
        Index all active clubs from the database.
        """
        clubs = Club.objects.filter(is_active=True)
        documents = []
        metadatas = []
        ids = []
        
        for club in clubs:
            # Create a descriptive text representation of the club
            content = f"Club: {club.name}\n"
            content += f"Category: {club.category.name if club.category else 'Uncategorized'}\n"
            content += f"City: {club.city.name if club.city else 'Unknown'}\n"
            content += f"Description: {club.description}\n"
            content += f"Address: {club.address}"
            
            documents.append(content)
            metadatas.append({
                'title': club.name,
                'source': f"club_{club.id}",
                'type': 'club',
                'club_id': str(club.id)
            })
            ids.append(f"club_{club.id}")
            
        if documents:
            self.vector_store.add_documents(
                collection_name='clubs',
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Indexed {len(documents)} clubs.")

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> list:
        """
        Split text into chunks with overlap.
        """
        if not text:
            return []
            
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
            
        return chunks
