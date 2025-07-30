import chromadb # type: ignore
from chromadb.config import Settings # type: ignore
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer # type: ignore
from app.core.config import settings
from app.core.exceptions import VectorStoreError


class VectorStoreService:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=False)
        )
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.collection_name = "study_documents"
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        try:
            return self.client.get_collection(name=self.collection_name)
        except:
            return self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
    
    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        user_id: int
    ) -> bool:
        try:
            texts = []
            metadatas = []
            ids = []
            
            for doc in documents:
                content = doc["content"].strip()
                if not content:
                    continue

                texts.append(content)
                metadatas.append({
                    "user_id": user_id,
                    "document_id": doc["document_id"],
                    "title": doc["title"],
                    "chunk_index": doc.get("chunk_index", 0)
                })
                ids.append(f"user_{user_id}_doc_{doc['document_id']}_chunk_{doc.get('chunk_index', 0)}")

                if not texts:
                    raise VectorStoreError("No valid document chunks to embed. Texts list is empty.")

            
            embeddings = self.embedding_model.encode(texts).tolist()
            
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            return True
        except Exception as e:
            raise VectorStoreError(f"Error adding documents to vector store: {str(e)}")
    
    async def similarity_search(
        self,
        query: str,
        user_id: int,
        document_ids: Optional[List[int]] = None,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        try:
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            where_clause = {"user_id": user_id}
            if document_ids:
                where_clause["document_id"] = {"$in": document_ids}
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=where_clause
            )
            
            documents = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i]
                    distance = results["distances"][0][i]
                    
                    documents.append({
                        "content": doc,
                        "document_id": metadata["document_id"],
                        "title": metadata["title"],
                        "score": 1 - distance,  # Convert distance to similarity
                        "chunk_index": metadata.get("chunk_index", 0)
                    })
            
            return documents
        except Exception as e:
            raise VectorStoreError(f"Error performing similarity search: {str(e)}")
    
    async def delete_user_documents(self, user_id: int) -> bool:
        try:
            self.collection.delete(where={"user_id": user_id})
            return True
        except Exception as e:
            raise VectorStoreError(f"Error deleting user documents: {str(e)}")