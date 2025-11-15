"""
Vector Store Management for RAG System
Supports Chroma, Qdrant, and FAISS
"""
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from loguru import logger
import hashlib

from app.config import settings


class VectorStoreManager:
    """Manage vector storage for video transcripts"""

    def __init__(self):
        """Initialize vector store manager"""
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.DEFAULT_EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        # Vector store instance (lazy loaded)
        self._vector_store = None

        logger.info("Vector store manager initialized")

    def _get_collection_name(self, video_id: str) -> str:
        """Generate collection name for video"""
        return f"video_{video_id}"

    def create_video_collection(
        self,
        video_id: str,
        transcript: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Create vector collection for a video

        Args:
            video_id: YouTube video ID
            transcript: Video transcript text
            metadata: Video metadata

        Returns:
            Collection name
        """
        try:
            logger.info(f"Creating vector collection for video {video_id}")

            # Split transcript into chunks
            documents = self._create_documents(transcript, video_id, metadata)

            # Create collection name
            collection_name = self._get_collection_name(video_id)

            # Create vector store
            vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=collection_name,
                persist_directory=settings.CHROMA_PERSIST_DIR
            )

            logger.info(
                f"Created collection {collection_name} with {len(documents)} chunks"
            )

            return collection_name

        except Exception as e:
            logger.error(f"Error creating vector collection: {e}")
            raise

    def _create_documents(
        self,
        transcript: str,
        video_id: str,
        metadata: Dict[str, Any]
    ) -> List[Document]:
        """Create documents from transcript"""
        # Split text
        chunks = self.text_splitter.split_text(transcript)

        # Create documents with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "video_id": video_id,
                    "video_title": metadata.get("title", "Unknown"),
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "source": f"youtube:{video_id}"
                }
            )
            documents.append(doc)

        return documents

    def get_vector_store(self, video_id: str) -> Optional[Chroma]:
        """
        Get vector store for a video

        Args:
            video_id: YouTube video ID

        Returns:
            Chroma vector store or None
        """
        try:
            collection_name = self._get_collection_name(video_id)

            vector_store = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=settings.CHROMA_PERSIST_DIR
            )

            # Test if collection exists by trying to get count
            try:
                vector_store._collection.count()
                return vector_store
            except Exception:
                logger.warning(f"Collection {collection_name} not found")
                return None

        except Exception as e:
            logger.error(f"Error getting vector store: {e}")
            return None

    def similarity_search(
        self,
        video_id: str,
        query: str,
        k: int = 5
    ) -> List[Document]:
        """
        Perform similarity search on video transcript

        Args:
            video_id: YouTube video ID
            query: Search query
            k: Number of results to return

        Returns:
            List of relevant documents
        """
        try:
            vector_store = self.get_vector_store(video_id)

            if not vector_store:
                logger.warning(f"No vector store found for video {video_id}")
                return []

            # Perform similarity search
            results = vector_store.similarity_search(query, k=k)

            logger.info(f"Found {len(results)} relevant chunks for query")
            return results

        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []

    def similarity_search_with_score(
        self,
        video_id: str,
        query: str,
        k: int = 5,
        score_threshold: float = 0.5
    ) -> List[tuple[Document, float]]:
        """
        Perform similarity search with relevance scores

        Args:
            video_id: YouTube video ID
            query: Search query
            k: Number of results
            score_threshold: Minimum relevance score

        Returns:
            List of (document, score) tuples
        """
        try:
            vector_store = self.get_vector_store(video_id)

            if not vector_store:
                return []

            # Perform search with scores
            results = vector_store.similarity_search_with_relevance_scores(
                query, k=k
            )

            # Filter by threshold
            filtered_results = [
                (doc, score) for doc, score in results
                if score >= score_threshold
            ]

            logger.info(
                f"Found {len(filtered_results)} chunks above threshold {score_threshold}"
            )

            return filtered_results

        except Exception as e:
            logger.error(f"Error in similarity search with score: {e}")
            return []

    def delete_collection(self, video_id: str) -> bool:
        """
        Delete vector collection for a video

        Args:
            video_id: YouTube video ID

        Returns:
            Success status
        """
        try:
            collection_name = self._get_collection_name(video_id)

            vector_store = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=settings.CHROMA_PERSIST_DIR
            )

            vector_store.delete_collection()

            logger.info(f"Deleted collection {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False

    def get_retriever(self, video_id: str, k: int = 5):
        """
        Get retriever for RAG

        Args:
            video_id: YouTube video ID
            k: Number of documents to retrieve

        Returns:
            Retriever instance
        """
        vector_store = self.get_vector_store(video_id)

        if not vector_store:
            raise ValueError(f"No vector store found for video {video_id}")

        return vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )


# Global instance
vector_store_manager = VectorStoreManager()
