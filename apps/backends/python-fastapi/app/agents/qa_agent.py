"""
Q&A Agent - Answers questions using RAG (Retrieval-Augmented Generation)
"""
from typing import Dict, Any, List, Optional
from loguru import logger

from app.agents.base import BaseAgent
from app.tools.vector_store import vector_store_manager


class QAAgent(BaseAgent):
    """Agent specialized in answering questions using RAG"""

    def __init__(self, **kwargs):
        super().__init__(agent_name="qa", **kwargs)

    async def answer_question(
        self,
        video_id: str,
        question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        k: int = 5
    ) -> Dict[str, Any]:
        """
        Answer a question about a video using RAG

        Args:
            video_id: YouTube video ID
            question: User's question
            conversation_history: Previous conversation messages
            k: Number of context chunks to retrieve

        Returns:
            Dictionary with answer and citations
        """
        try:
            # Retrieve relevant context
            relevant_docs = vector_store_manager.similarity_search_with_score(
                video_id=video_id,
                query=question,
                k=k,
                score_threshold=0.3
            )

            if not relevant_docs:
                return {
                    "answer": "I couldn't find relevant information in the video to answer this question. "
                              "The video might not cover this topic, or it may need to be re-indexed.",
                    "citations": [],
                    "confidence": "low"
                }

            # Format context from retrieved documents
            context = self._format_context(relevant_docs)

            # Build conversation context
            conversation_context = self._build_conversation_context(conversation_history)

            # Generate answer
            answer = await self._generate_answer(
                question=question,
                context=context,
                conversation_context=conversation_context
            )

            # Extract citations from relevant docs
            citations = self._extract_citations(relevant_docs)

            return {
                "answer": answer,
                "citations": citations,
                "confidence": self._calculate_confidence(relevant_docs),
                "sources": [doc.metadata.get("source", "") for doc, _ in relevant_docs]
            }

        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "citations": [],
                "confidence": "error"
            }

    def _format_context(self, relevant_docs: List[tuple]) -> str:
        """Format retrieved documents into context string"""
        context_parts = []

        for i, (doc, score) in enumerate(relevant_docs, 1):
            context_parts.append(
                f"[Context {i}] (Relevance: {score:.2f})\n{doc.page_content}\n"
            )

        return "\n".join(context_parts)

    def _build_conversation_context(
        self,
        conversation_history: Optional[List[Dict[str, str]]]
    ) -> str:
        """Build conversation context from history"""
        if not conversation_history:
            return ""

        context_parts = ["Previous conversation:"]

        for msg in conversation_history[-5:]:  # Last 5 messages
            role = msg.get("role", "user")
            content = msg.get("content", "")
            context_parts.append(f"{role.capitalize()}: {content}")

        return "\n".join(context_parts)

    async def _generate_answer(
        self,
        question: str,
        context: str,
        conversation_context: str
    ) -> str:
        """Generate answer using LLM with context"""
        prompt = f"""Answer the following question based ONLY on the provided context from the video.

{conversation_context}

Context from video:
{context}

Question: {question}

Instructions:
1. Base your answer entirely on the context provided
2. Cite specific parts of the context when possible
3. If the context doesn't contain enough information, say so
4. Be concise and direct
5. Use timestamps if mentioned in context
6. Acknowledge if you're uncertain

Answer:"""

        answer = await self.invoke(prompt)
        return answer

    def _extract_citations(self, relevant_docs: List[tuple]) -> List[Dict[str, str]]:
        """Extract citations from relevant documents"""
        citations = []

        for doc, score in relevant_docs[:3]:  # Top 3 most relevant
            # Try to extract timestamp from content
            content = doc.page_content
            timestamp = self._extract_timestamp_from_text(content)

            citation = {
                "text": content[:150] + "..." if len(content) > 150 else content,
                "relevance": round(score, 2),
                "chunk_index": doc.metadata.get("chunk_index", 0)
            }

            if timestamp:
                citation["time"] = timestamp

            citations.append(citation)

        return citations

    def _extract_timestamp_from_text(self, text: str) -> Optional[str]:
        """Extract timestamp from text if present"""
        import re

        # Look for timestamp patterns [MM:SS] or [HH:MM:SS]
        patterns = [
            r'\[(\d{1,2}:\d{2})\]',
            r'\[(\d{1,2}:\d{2}:\d{2})\]',
            r'(\d{1,2}:\d{2})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return None

    def _calculate_confidence(self, relevant_docs: List[tuple]) -> str:
        """Calculate confidence level based on relevance scores"""
        if not relevant_docs:
            return "none"

        avg_score = sum(score for _, score in relevant_docs) / len(relevant_docs)

        if avg_score >= 0.7:
            return "high"
        elif avg_score >= 0.5:
            return "medium"
        else:
            return "low"

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the Q&A agent

        Args:
            input_data: {
                "video_id": str,
                "question": str,
                "conversation_history": Optional[List[Dict]],
                "k": Optional[int]
            }

        Returns:
            Dictionary with answer and metadata
        """
        try:
            video_id = input_data.get("video_id")
            question = input_data.get("question")
            conversation_history = input_data.get("conversation_history")
            k = input_data.get("k", 5)

            if not video_id or not question:
                return self.format_output(
                    success=False,
                    data=None,
                    error="Missing video_id or question"
                )

            self.log_execution("Answering question", f"Video: {video_id}")

            # Answer question
            result = await self.answer_question(
                video_id=video_id,
                question=question,
                conversation_history=conversation_history,
                k=k
            )

            self.log_execution(
                "Answer generated",
                f"Confidence: {result['confidence']}"
            )

            return self.format_output(
                success=True,
                data=result,
                metadata={
                    "video_id": video_id,
                    "confidence": result["confidence"]
                }
            )

        except Exception as e:
            logger.error(f"Q&A agent error: {e}")
            return self.format_output(
                success=False,
                data=None,
                error=str(e)
            )
