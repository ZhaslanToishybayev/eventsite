import logging
from typing import List, Dict, Any
from .vector_store import VectorStoreService

logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    """
    Service for retrieving knowledge base articles using Vector Search (RAG).
    """
    
    def __init__(self):
        self.vector_store = VectorStoreService()

    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search for articles matching the query using semantic search.
        """
        results = []
        
        # Search Help Docs
        help_results = self.vector_store.query(
            collection_name='help_docs',
            query_text=query,
            n_results=limit
        )
        
        if help_results and help_results['documents']:
            for i, doc in enumerate(help_results['documents'][0]):
                results.append({
                    'title': help_results['metadatas'][0][i]['title'],
                    'content': doc,
                    'source': help_results['metadatas'][0][i]['source'],
                    'type': 'help_doc',
                    'score': 1.0 # Placeholder, Chroma returns distances
                })

        # Search Clubs
        club_results = self.vector_store.query(
            collection_name='clubs',
            query_text=query,
            n_results=limit
        )
        
        if club_results and club_results['documents']:
            for i, doc in enumerate(club_results['documents'][0]):
                results.append({
                    'title': club_results['metadatas'][0][i]['title'],
                    'content': doc,
                    'source': 'Club Database',
                    'type': 'club',
                    'score': 1.0
                })
        
        return results[:limit]

    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results for the AI.
        """
        if not results:
            return "No relevant information found in the knowledge base."
            
        formatted = "📚 **Knowledge Base Search Results:**\n\n"
        for article in results:
            formatted += f"**{article['title']}** ({article['type']})\n"
            formatted += f"{article['content']}\n\n"
            
        return formatted
