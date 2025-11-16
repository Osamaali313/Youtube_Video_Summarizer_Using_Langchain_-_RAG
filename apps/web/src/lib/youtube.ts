/**
 * YouTube URL validation and extraction utilities
 */

export interface YouTubeVideoInfo {
  videoId: string;
  url: string;
  isValid: boolean;
  error?: string;
}

/**
 * Extracts YouTube video ID from various URL formats
 * Supports:
 * - https://www.youtube.com/watch?v=VIDEO_ID
 * - https://youtu.be/VIDEO_ID
 * - https://www.youtube.com/embed/VIDEO_ID
 * - https://m.youtube.com/watch?v=VIDEO_ID
 */
export function extractVideoId(url: string): string | null {
  if (!url) return null;

  // Remove whitespace
  url = url.trim();

  // Standard watch URL
  const watchMatch = url.match(/[?&]v=([^&]+)/);
  if (watchMatch) return watchMatch[1];

  // Short URL
  const shortMatch = url.match(/youtu\.be\/([^?]+)/);
  if (shortMatch) return shortMatch[1];

  // Embed URL
  const embedMatch = url.match(/youtube\.com\/embed\/([^?]+)/);
  if (embedMatch) return embedMatch[1];

  // If it's just the video ID
  if (/^[a-zA-Z0-9_-]{11}$/.test(url)) return url;

  return null;
}

/**
 * Validates YouTube URL and extracts video information
 */
export function validateYouTubeUrl(url: string): YouTubeVideoInfo {
  const videoId = extractVideoId(url);

  if (!videoId) {
    return {
      videoId: '',
      url,
      isValid: false,
      error: 'Invalid YouTube URL. Please provide a valid YouTube video link.',
    };
  }

  // Validate video ID format (11 characters, alphanumeric plus - and _)
  if (!/^[a-zA-Z0-9_-]{11}$/.test(videoId)) {
    return {
      videoId,
      url,
      isValid: false,
      error: 'Invalid video ID format.',
    };
  }

  return {
    videoId,
    url: `https://www.youtube.com/watch?v=${videoId}`,
    isValid: true,
  };
}

/**
 * Generates YouTube thumbnail URL
 */
export function getThumbnailUrl(videoId: string, quality: 'default' | 'hq' | 'maxres' = 'hq'): string {
  const qualityMap = {
    default: 'default',
    hq: 'hqdefault',
    maxres: 'maxresdefault',
  };

  return `https://img.youtube.com/vi/${videoId}/${qualityMap[quality]}.jpg`;
}

/**
 * Generates YouTube embed URL
 */
export function getEmbedUrl(videoId: string, options?: {
  autoplay?: boolean;
  start?: number;
  end?: number;
}): string {
  const params = new URLSearchParams();

  if (options?.autoplay) params.set('autoplay', '1');
  if (options?.start) params.set('start', options.start.toString());
  if (options?.end) params.set('end', options.end.toString());

  const queryString = params.toString();
  return `https://www.youtube.com/embed/${videoId}${queryString ? '?' + queryString : ''}`;
}

/**
 * Converts timestamp string (HH:MM:SS or MM:SS) to seconds
 */
export function timestampToSeconds(timestamp: string): number {
  const parts = timestamp.split(':').map(Number);

  if (parts.length === 2) {
    // MM:SS
    return parts[0] * 60 + parts[1];
  } else if (parts.length === 3) {
    // HH:MM:SS
    return parts[0] * 3600 + parts[1] * 60 + parts[2];
  }

  return 0;
}

/**
 * Converts seconds to timestamp string (HH:MM:SS or MM:SS)
 */
export function secondsToTimestamp(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Generates YouTube URL with timestamp
 */
export function getTimestampUrl(videoId: string, timestamp: string | number): string {
  const seconds = typeof timestamp === 'string' ? timestampToSeconds(timestamp) : timestamp;
  return `https://www.youtube.com/watch?v=${videoId}&t=${seconds}s`;
}
