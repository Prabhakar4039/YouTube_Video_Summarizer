from youtube_transcript_api import YouTubeTranscriptApi
import re

def extract_video_id(url: str) -> str:
    """
    Extract the 11-character video ID from a YouTube URL.
    Handles standard URLs, shorts, embeds, and URLs with parameters like playlists.
    """
    # 1. First, check for common patterns and take exactly 11 chars
    patterns = [
        r'(?:v=|\/|embed\/|shorts\/|watch\?v=)([0-9A-Za-z_-]{11})',
    ]
    for p in patterns:
        match = re.search(p, url)
        if match: 
            return match.group(1)
            
    # 2. If nothing matched, but we have an 11-char string, try it
    if len(url) == 11 and re.match(r'^[0-9A-Za-z_-]{11}$', url):
        return url
        
    return None

def get_transcript(video_id: str, max_words: int = 4000) -> str:
    """
    Fetch transcript from YouTube captions with multi-stage fallback.
    1. Try preferred English transcript.
    2. Try list of all transcripts (manual -> auto-generated).
    """
    print(f"DEBUG: Processing Video ID: {video_id}")
    
    try:
        # Strategy 1: Direct fetch for English (fastest)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        
    except Exception as e:
        print(f"DEBUG: Initial fetch failed. Trying list_transcripts fallback. Error: {str(e)}")
        
        try:
            # Strategy 2: List transcripts and pick manual then generated
            transcript_list_obj = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Prefer manual English
            try:
                transcript_obj = transcript_list_obj.find_manually_created_transcript(['en'])
                print("DEBUG: Found manually created English transcript.")
            except:
                # Fallback to generated English
                try:
                    transcript_obj = transcript_list_obj.find_generated_transcript(['en'])
                    print("DEBUG: Found auto-generated English transcript.")
                except:
                    # Final fallback: Look for ANY transcript and translate it or just pick first
                    # We'll just pick the first available and try to fetch it
                    transcript_obj = next(iter(transcript_list_obj))
                    print(f"DEBUG: Found non-English/other transcript ({transcript_obj.language})")
            
            transcript_list = transcript_obj.fetch()
            
        except Exception as final_error:
            # Re-raise actual detailed message
            print(f"DEBUG: Final Strategy failed for {video_id}: {str(final_error)}")
            raise Exception(f"Failed to fetch transcript: {str(final_error)}")

    # Combine text properly
    full_text = " ".join([item['text'] for item in transcript_list])
    
    # Word-count limit
    words = full_text.split()
    if len(words) > max_words:
        full_text = " ".join(words[:max_words])
        
    return full_text
