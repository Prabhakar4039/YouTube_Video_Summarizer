from youtube_transcript_api import YouTubeTranscriptApi
import re

def extract_video_id(url: str) -> str:
    """
    Extract the 11-character video ID from a YouTube URL.
    Handles standard URLs, shorts, embeds, and URLs with parameters like playlists.
    """
    # Pattern designed to capture exactly 11 chars after common YouTube URL indicators
    patterns = [
        r'(?:v=|\/|embed\/|shorts\/|watch\?v=)([0-9A-Za-z_-]{11})',
    ]
    for p in patterns:
        match = re.search(p, url)
        if match: 
            return match.group(1)
            
    # Fallback for just the ID if it's already extracted but contains extra garbage
    if len(url) >= 11 and re.match(r'^[0-9A-Za-z_-]{11}', url):
        return url[:11]
        
    return None

def get_transcript(video_id: str, max_words: int = 4000) -> str:
    """
    Fetch transcript from YouTube captions.
    Specifically requests English ['en'] to include auto-generated transcripts.
    """
    try:
        # Standard API attempt requesting specifically English
        # This will include both manually created and auto-generated transcripts.
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        full_text = " ".join([item['text'] for item in transcript_list])
        
        # Word-count limit
        words = full_text.split()
        if len(words) > max_words:
            full_text = " ".join(words[:max_words])
            
        return full_text
        
    except Exception as e:
        # Re-raise clean error for better UI handling
        raise Exception("This video does not have captions. Try another video.")
