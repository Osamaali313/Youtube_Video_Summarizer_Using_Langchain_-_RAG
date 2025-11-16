"""
Citation Agent - Adds timestamps and source references to summaries
"""
from typing import Dict, Any, List
import re
from loguru import logger

from app.agents.base import BaseAgent


class CitationAgent(BaseAgent):
    """Agent specialized in adding citations and timestamps"""

    def __init__(self, **kwargs):
        super().__init__(agent_name="citation", **kwargs)

    async def add_citations(
        self,
        summary: str,
        transcript_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Add timestamp citations to summary

        Args:
            summary: The summary text
            transcript_data: Raw transcript with timestamps

        Returns:
            Dictionary with cited summary and timestamp list
        """
        # Extract key points from summary
        key_points = self._extract_key_points(summary)

        # Find relevant timestamps for each point
        citations = await self._find_citations(key_points, transcript_data)

        # Generate cited version
        cited_summary = await self._generate_cited_summary(summary, citations)

        # Create timestamp summary
        timestamp_summary = self._create_timestamp_summary(citations)

        return {
            "cited_summary": cited_summary,
            "timestamps": citations,
            "timestamp_summary": timestamp_summary
        }

    def _extract_key_points(self, summary: str) -> List[str]:
        """Extract key points from summary"""
        # Split by paragraphs and bullet points
        points = []

        # Find bullet points
        bullet_pattern = r'[•\-\*]\s+(.+?)(?=\n[•\-\*]|\n\n|$)'
        bullets = re.findall(bullet_pattern, summary, re.DOTALL)
        points.extend(bullets)

        # Find numbered lists
        numbered_pattern = r'\d+\.\s+(.+?)(?=\n\d+\.|\n\n|$)'
        numbered = re.findall(numbered_pattern, summary, re.DOTALL)
        points.extend(numbered)

        # If no structured points, split by sentences
        if not points:
            sentences = re.split(r'[.!?]\s+', summary)
            points = [s.strip() for s in sentences if len(s.strip()) > 30]

        return points[:15]  # Top 15 points

    async def _find_citations(
        self,
        key_points: List[str],
        transcript_data: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """
        Find timestamps for key points

        Args:
            key_points: List of key points from summary
            transcript_data: Raw transcript with timestamps

        Returns:
            List of citation dictionaries
        """
        citations = []

        # Create searchable transcript
        full_transcript = " ".join([seg["text"] for seg in transcript_data])

        for point in key_points:
            # Extract keywords from point
            keywords = self._extract_keywords(point)

            # Find best matching segment
            best_match = self._find_best_match(
                keywords,
                transcript_data,
                full_transcript
            )

            if best_match:
                citations.append({
                    "time": self._seconds_to_timestamp(best_match["start"]),
                    "text": point[:150],  # Truncate long points
                    "confidence": best_match.get("confidence", 0.5)
                })

        return citations

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Remove common words
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'this', 'that', 'these', 'those'
        }

        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if w not in common_words and len(w) > 3]

        return keywords[:10]  # Top 10 keywords

    def _find_best_match(
        self,
        keywords: List[str],
        transcript_data: List[Dict[str, Any]],
        full_transcript: str
    ) -> Optional[Dict[str, Any]]:
        """Find best matching transcript segment"""
        best_segment = None
        best_score = 0

        for segment in transcript_data:
            score = sum(1 for kw in keywords if kw in segment["text"].lower())

            if score > best_score:
                best_score = score
                best_segment = segment
                best_segment["confidence"] = min(score / len(keywords), 1.0)

        return best_segment

    async def _generate_cited_summary(
        self,
        summary: str,
        citations: List[Dict[str, str]]
    ) -> str:
        """
        Generate summary with inline citations

        Args:
            summary: Original summary
            citations: List of citations

        Returns:
            Summary with citations
        """
        prompt = f"""Add timestamp citations to this summary using the provided timestamps.

Summary:
{summary}

Available Timestamps:
{self._format_citations_for_prompt(citations)}

Instructions:
1. Add timestamp references inline where relevant [MM:SS]
2. Place citations after key statements
3. Don't over-cite - only for important claims
4. Preserve the original structure and flow

Return the summary with citations added.
"""

        cited = await self.invoke(prompt)
        return cited

    def _format_citations_for_prompt(self, citations: List[Dict[str, str]]) -> str:
        """Format citations for the prompt"""
        return "\n".join([
            f"[{c['time']}] {c['text']}"
            for c in citations
        ])

    def _create_timestamp_summary(
        self,
        citations: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Create a structured timestamp summary"""
        return [
            {
                "time": c["time"],
                "description": c["text"]
            }
            for c in citations
        ]

    def _seconds_to_timestamp(self, seconds: float) -> str:
        """Convert seconds to timestamp format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the citation agent

        Args:
            input_data: {
                "summary": str,
                "transcript_data": List[Dict],
                "video_id": str
            }

        Returns:
            Dictionary with cited summary and timestamps
        """
        try:
            summary = input_data.get("summary", "")
            transcript_data = input_data.get("transcript_data", [])
            video_id = input_data.get("video_id", "")

            if not summary or not transcript_data:
                return self.format_output(
                    success=False,
                    data=None,
                    error="Missing summary or transcript data"
                )

            self.log_execution("Starting citation", f"Video: {video_id}")

            # Add citations
            result = await self.add_citations(summary, transcript_data)

            self.log_execution(
                "Citation complete",
                f"{len(result['timestamps'])} timestamps added"
            )

            return self.format_output(
                success=True,
                data=result,
                metadata={
                    "video_id": video_id,
                    "citation_count": len(result["timestamps"])
                }
            )

        except Exception as e:
            logger.error(f"Citation agent error: {e}")
            return self.format_output(
                success=False,
                data=None,
                error=str(e)
            )
