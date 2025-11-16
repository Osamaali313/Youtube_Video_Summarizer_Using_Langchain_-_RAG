"""
Extractor Agent - Fetches YouTube transcripts and metadata
"""
from typing import Dict, Any, Optional, List
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)
from pytube import YouTube
import re
from loguru import logger

from app.agents.base import BaseAgent


class ExtractorAgent(BaseAgent):
    """Agent specialized in extracting YouTube video transcripts"""

    def __init__(self, **kwargs):
        super().__init__(agent_name="extractor", **kwargs)

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'^([0-9A-Za-z_-]{11})$'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    async def get_video_metadata(self, video_url: str) -> Dict[str, Any]:
        """
        Get video metadata using pytube

        Args:
            video_url: YouTube video URL

        Returns:
            Dictionary with video metadata
        """
        try:
            yt = YouTube(video_url)

            metadata = {
                "title": yt.title,
                "author": yt.author,
                "length": yt.length,
                "views": yt.views,
                "description": yt.description[:500] if yt.description else "",
                "publish_date": str(yt.publish_date) if yt.publish_date else None,
                "thumbnail_url": yt.thumbnail_url,
            }

            self.log_execution("Metadata extracted", f"Title: {metadata['title']}")
            return metadata

        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {
                "title": "Unknown",
                "author": "Unknown",
                "length": 0,
                "error": str(e)
            }

    async def get_transcript(
        self,
        video_id: str,
        languages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get transcript for a video

        Args:
            video_id: YouTube video ID
            languages: Preferred languages (default: ['en'])

        Returns:
            Dictionary with transcript and metadata
        """
        languages = languages or ['en']

        try:
            # Get available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # Try to get transcript in preferred language
            transcript = None
            is_auto_generated = False

            for lang in languages:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    is_auto_generated = transcript.is_generated
                    break
                except NoTranscriptFound:
                    continue

            # If no preferred language, get first available
            if transcript is None:
                available = list(transcript_list)
                if available:
                    transcript = available[0]
                    is_auto_generated = transcript.is_generated
                else:
                    raise NoTranscriptFound(video_id, languages, None)

            # Fetch the transcript
            transcript_data = transcript.fetch()

            # Format transcript
            formatted_transcript = self._format_transcript(transcript_data)

            result = {
                "transcript": formatted_transcript,
                "raw_transcript": transcript_data,
                "language": transcript.language_code,
                "is_auto_generated": is_auto_generated,
                "total_segments": len(transcript_data),
            }

            self.log_execution(
                "Transcript extracted",
                f"{len(transcript_data)} segments in {transcript.language_code}"
            )

            return result

        except TranscriptsDisabled:
            logger.error(f"Transcripts disabled for video {video_id}")
            raise ValueError("Transcripts are disabled for this video")

        except NoTranscriptFound:
            logger.error(f"No transcript found for video {video_id}")
            raise ValueError(f"No transcript available in languages: {languages}")

        except VideoUnavailable:
            logger.error(f"Video {video_id} is unavailable")
            raise ValueError("Video is unavailable or private")

        except Exception as e:
            logger.error(f"Error getting transcript: {e}")
            raise ValueError(f"Failed to get transcript: {str(e)}")

    def _format_transcript(self, transcript_data: List[Dict]) -> str:
        """
        Format transcript with timestamps

        Args:
            transcript_data: Raw transcript data

        Returns:
            Formatted transcript string
        """
        formatted_lines = []

        for segment in transcript_data:
            timestamp = self._seconds_to_timestamp(segment['start'])
            text = segment['text'].strip()
            formatted_lines.append(f"[{timestamp}] {text}")

        return "\n".join(formatted_lines)

    def _seconds_to_timestamp(self, seconds: float) -> str:
        """Convert seconds to MM:SS or HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def extract_timestamps(self, transcript_data: List[Dict]) -> List[Dict[str, str]]:
        """
        Extract key timestamps from transcript

        Args:
            transcript_data: Raw transcript data

        Returns:
            List of timestamp dictionaries
        """
        timestamps = []

        # Sample every ~30 seconds for key moments
        sample_interval = 30
        last_sample = 0

        for segment in transcript_data:
            if segment['start'] - last_sample >= sample_interval:
                timestamps.append({
                    "time": self._seconds_to_timestamp(segment['start']),
                    "text": segment['text'][:100]  # First 100 chars
                })
                last_sample = segment['start']

        return timestamps

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the extractor agent

        Args:
            input_data: {
                "video_url": str,
                "languages": Optional[List[str]]
            }

        Returns:
            Dictionary with video data and transcript
        """
        try:
            video_url = input_data.get("video_url")
            languages = input_data.get("languages", ["en"])

            if not video_url:
                return self.format_output(
                    success=False,
                    data=None,
                    error="No video URL provided"
                )

            self.log_execution("Starting extraction", video_url)

            # Extract video ID
            video_id = self.extract_video_id(video_url)
            if not video_id:
                return self.format_output(
                    success=False,
                    data=None,
                    error="Invalid YouTube URL"
                )

            # Get metadata
            metadata = await self.get_video_metadata(video_url)

            # Get transcript
            transcript_result = await self.get_transcript(video_id, languages)

            # Extract key timestamps
            timestamps = self.extract_timestamps(transcript_result["raw_transcript"])

            # Combine results
            result = {
                "video_id": video_id,
                "video_url": video_url,
                **metadata,
                **transcript_result,
                "key_timestamps": timestamps[:20],  # First 20 key moments
            }

            self.log_execution("Extraction complete", f"Success for {video_id}")

            return self.format_output(
                success=True,
                data=result,
                metadata={
                    "video_id": video_id,
                    "duration": metadata.get("length", 0),
                    "language": transcript_result["language"]
                }
            )

        except Exception as e:
            logger.error(f"Extractor agent error: {e}")
            return self.format_output(
                success=False,
                data=None,
                error=str(e)
            )
