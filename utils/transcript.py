from youtube_transcript_api import YouTubeTranscriptApi
import re

def extract_video_id(url: str) -> str:
    """Extract the 11-character video ID from a YouTube URL."""
    patterns = [r'(?:v=|\/|embed\/|shorts\/)([0-9A-Za-z_-]{11})']
    for p in patterns:
        match = re.search(p, url)
        if match: return match.group(1)
    return url if len(url) == 11 else None

def get_transcript(video_id: str, max_words: int = 4000) -> str:
    """Fetch transcript from YouTube captions (standard API only)."""
    try:
        # Standard API attempt
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([item['text'] for item in transcript_list])
        
        # Word-count limit
        words = full_text.split()
        if len(words) > max_words:
            full_text = " ".join(words[:max_words])
            
        return full_text
        
    except Exception as e:
        # Re-raise clean error for better UI handling
        raise Exception("No captions available for this video.")
