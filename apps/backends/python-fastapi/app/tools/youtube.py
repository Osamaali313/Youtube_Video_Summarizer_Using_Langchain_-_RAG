"""
YouTube utility functions
"""
import re
from typing import Optional
from urllib.parse import urlparse, parse_qs


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from various URL formats

    Supported formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID

    Args:
        url: YouTube video URL

    Returns:
        Video ID or None if invalid
    """
    if not url:
        return None

    # Pattern for video ID (11 characters, alphanumeric + dash/underscore)
    video_id_pattern = r'[a-zA-Z0-9_-]{11}'

    # Try different URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
        r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    # Try parsing as URL with query parameters
    try:
        parsed = urlparse(url)
        if 'youtube.com' in parsed.netloc:
            query_params = parse_qs(parsed.query)
            if 'v' in query_params:
                video_id = query_params['v'][0]
                if re.match(video_id_pattern, video_id):
                    return video_id
    except:
        pass

    return None


def is_valid_youtube_url(url: str) -> bool:
    """
    Check if URL is a valid YouTube video URL

    Args:
        url: URL to validate

    Returns:
        True if valid YouTube URL
    """
    return extract_video_id(url) is not None


def get_thumbnail_url(video_id: str, quality: str = "maxresdefault") -> str:
    """
    Get YouTube thumbnail URL for a video

    Args:
        video_id: YouTube video ID
        quality: Thumbnail quality (maxresdefault, hqdefault, mqdefault, sddefault, default)

    Returns:
        Thumbnail URL
    """
    return f"https://img.youtube.com/vi/{video_id}/{quality}.jpg"


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to HH:MM:SS or MM:SS

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def parse_duration(duration_str: str) -> int:
    """
    Parse duration string to seconds

    Args:
        duration_str: Duration string (HH:MM:SS or MM:SS)

    Returns:
        Duration in seconds
    """
    parts = duration_str.split(':')

    if len(parts) == 3:
        # HH:MM:SS
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        # MM:SS
        return int(parts[0]) * 60 + int(parts[1])
    else:
        return 0
