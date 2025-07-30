from typing import List, Dict, Any, Optional
from app.services.vector_store_service import VectorStoreService
from app.services.llm_service import LLMService
from app.services.document_service import DocumentService
from app.core.exceptions import StudyAssistantException


class RAGService:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.llm_service = LLMService()
        self.document_service = DocumentService()
    
    async def generate_response(
        self,
        query: str,
        user_id: int,
        context_documents: Optional[List[int]] = None,
        max_sources: int = 5
    ) -> Dict[str, Any]:
        try:
            # Retrieve relevant documents
            relevant_docs = await self.vector_store.similarity_search(
                query=query,
                user_id=user_id,
                document_ids=context_documents,
                k=max_sources
            )
            
            # Prepare context for LLM
            context = self._prepare_context(relevant_docs)
            
            # Generate response
            response = await self.llm_service.generate_chat_response(
                query=query,
                context=context
            )
            
            # Prepare sources information
            sources = self._prepare_sources(relevant_docs)
            
            return {
                "response": response,
                "sources": sources,
                "context_used": len(relevant_docs) > 0
            }
            
        except Exception as e:
            raise StudyAssistantException(f"Error generating RAG response: {str(e)}")
    
    def _prepare_context(self, documents: List[Dict[str, Any]]) -> str:
        if not documents:
            return ""
        
        context_parts = []
        for doc in documents:
            context_parts.append(f"Source: {doc['title']}\nContent: {doc['content']}\n")
        
        return "\n---\n".join(context_parts)
    
    def _prepare_sources(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sources = []
        for doc in documents:
            sources.append({
                "document_id": doc.get("document_id"),
                "title": doc.get("title"),
                "relevance_score": doc.get("score", 0.0),
                "chunk_text": doc.get("content", "")[:200] + "..."
            })
        return sources