"""
Summarizer Agent - Creates intelligent summaries with different modes
"""
from typing import Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from loguru import logger

from app.agents.base import BaseAgent
from app.config import settings


class SummarizerAgent(BaseAgent):
    """Agent specialized in creating intelligent summaries"""

    def __init__(self, **kwargs):
        super().__init__(agent_name="summarizer", **kwargs)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    async def summarize_quick(
        self,
        transcript: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Create a quick summary (bullet points)

        Args:
            transcript: Video transcript
            metadata: Video metadata

        Returns:
            Quick summary string
        """
        prompt = f"""Create a quick summary of this YouTube video.

Video Title: {metadata.get('title', 'Unknown')}
Duration: {metadata.get('length', 0)} seconds

Transcript:
{transcript[:4000]}  # Limit for quick mode

Create a concise summary with 5-7 bullet points highlighting the key takeaways.
Focus on main topics only. Be brief and scannable.

Format:
• Key point 1
• Key point 2
...
"""

        summary = await self.invoke(prompt)
        return summary

    async def summarize_standard(
        self,
        transcript: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Create a standard summary (detailed sections)

        Args:
            transcript: Video transcript
            metadata: Video metadata

        Returns:
            Standard summary string
        """
        prompt = f"""Create a comprehensive summary of this YouTube video.

Video Title: {metadata.get('title', 'Unknown')}
Author: {metadata.get('author', 'Unknown')}
Duration: {self._format_duration(metadata.get('length', 0))}

Transcript:
{transcript[:8000]}  # More content for standard mode

Create a well-structured summary with:
1. Introduction paragraph (what the video is about)
2. 3-5 main sections with clear headers
3. Key points under each section
4. Brief conclusion

Use markdown formatting for headers and structure.
"""

        summary = await self.invoke(prompt)
        return summary

    async def summarize_research(
        self,
        transcript: str,
        metadata: Dict[str, Any],
        research_context: Optional[str] = None
    ) -> str:
        """
        Create a research-grade summary (comprehensive analysis)

        Args:
            transcript: Video transcript
            metadata: Video metadata
            research_context: Optional research findings

        Returns:
            Research summary string
        """
        context_section = ""
        if research_context:
            context_section = f"""

Research Context:
{research_context}
"""

        prompt = f"""Create a comprehensive, research-grade summary of this YouTube video.

Video Title: {metadata.get('title', 'Unknown')}
Author: {metadata.get('author', 'Unknown')}
Duration: {self._format_duration(metadata.get('length', 0))}
Published: {metadata.get('publish_date', 'Unknown')}
{context_section}

Transcript:
{transcript}

Create a detailed summary including:
1. Executive Summary (2-3 paragraphs)
2. Background and Context
3. Main Topics (detailed sections with sub-points)
4. Key Arguments and Evidence
5. Implications and Conclusions
6. Notable Quotes or Statistics

Use markdown formatting. Be thorough and analytical.
"""

        summary = await self.invoke(prompt)
        return summary

    async def summarize_educational(
        self,
        transcript: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Create an educational summary (learning-focused)

        Args:
            transcript: Video transcript
            metadata: Video metadata

        Returns:
            Educational summary string
        """
        prompt = f"""Create an educational summary of this YouTube video optimized for learning.

Video Title: {metadata.get('title', 'Unknown')}
Duration: {self._format_duration(metadata.get('length', 0))}

Transcript:
{transcript}

Create a learning-focused summary with:
1. Learning Objectives (what you'll learn)
2. Key Concepts Explained (define important terms)
3. Main Content (organized by topic)
4. Step-by-Step Explanations (if applicable)
5. Practice Questions or Discussion Points
6. Additional Resources Mentioned

Format for easy studying and reference.
Use clear explanations suitable for learners.
"""

        summary = await self.invoke(prompt)
        return summary

    async def create_summary_chunks(self, transcript: str) -> list[str]:
        """
        Split long transcripts into manageable chunks

        Args:
            transcript: Full transcript

        Returns:
            List of text chunks
        """
        chunks = self.text_splitter.split_text(transcript)
        self.log_execution("Split transcript", f"{len(chunks)} chunks")
        return chunks

    async def summarize_chunks(self, chunks: list[str], mode: str) -> str:
        """
        Summarize multiple chunks and combine

        Args:
            chunks: List of text chunks
            mode: Summary mode

        Returns:
            Combined summary
        """
        summaries = []

        for i, chunk in enumerate(chunks):
            self.log_execution("Summarizing chunk", f"{i+1}/{len(chunks)}")

            prompt = f"""Summarize this section of a video transcript:

Section {i+1} of {len(chunks)}:
{chunk}

Create a concise summary of the main points in this section.
"""

            chunk_summary = await self.invoke(prompt)
            summaries.append(chunk_summary)

        # Combine chunk summaries
        combined_prompt = f"""Combine these section summaries into a cohesive final summary:

{chr(10).join([f'Section {i+1}: {s}' for i, s in enumerate(summaries)])}

Create a unified, well-structured summary that flows naturally.
"""

        final_summary = await self.invoke(combined_prompt)
        return final_summary

    def _format_duration(self, seconds: int) -> str:
        """Format duration in human-readable format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the summarizer agent

        Args:
            input_data: {
                "transcript": str,
                "metadata": Dict[str, Any],
                "mode": str (quick, standard, research, educational),
                "research_context": Optional[str]
            }

        Returns:
            Dictionary with summary
        """
        try:
            transcript = input_data.get("transcript", "")
            metadata = input_data.get("metadata", {})
            mode = input_data.get("mode", "standard")
            research_context = input_data.get("research_context")

            if not transcript:
                return self.format_output(
                    success=False,
                    data=None,
                    error="No transcript provided"
                )

            self.log_execution("Starting summarization", f"Mode: {mode}")

            # Check if transcript needs chunking (> 10000 chars)
            if len(transcript) > 10000 and mode != "quick":
                chunks = await self.create_summary_chunks(transcript)
                summary = await self.summarize_chunks(chunks, mode)
            else:
                # Summarize based on mode
                if mode == "quick":
                    summary = await self.summarize_quick(transcript, metadata)
                elif mode == "standard":
                    summary = await self.summarize_standard(transcript, metadata)
                elif mode == "research":
                    summary = await self.summarize_research(
                        transcript, metadata, research_context
                    )
                elif mode == "educational":
                    summary = await self.summarize_educational(transcript, metadata)
                else:
                    summary = await self.summarize_standard(transcript, metadata)

            self.log_execution("Summarization complete", f"{len(summary)} characters")

            return self.format_output(
                success=True,
                data={
                    "summary": summary,
                    "mode": mode,
                    "summary_length": len(summary),
                },
                metadata={
                    "mode": mode,
                    "video_title": metadata.get("title", "Unknown")
                }
            )

        except Exception as e:
            logger.error(f"Summarizer agent error: {e}")
            return self.format_output(
                success=False,
                data=None,
                error=str(e)
            )
