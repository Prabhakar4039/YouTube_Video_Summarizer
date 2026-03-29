from youtube_transcript_api import YouTubeTranscriptApi
import re
import os
import yt_dlp
import tempfile
from groq import Groq
from dotenv import load_dotenv

# Load env
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_video_id(url: str) -> str:
    """Extract the 11-character video ID from a YouTube URL."""
    patterns = [r'(?:v=|\/|embed\/|shorts\/|watch\?v=)([0-9A-Za-z_-]{11})']
    for p in patterns:
        match = re.search(p, url)
        if match: return match.group(1)
    if len(url) == 11 and re.match(r'^[0-9A-Za-z_-]{11}$', url):
        return url
    return None

def transcribe_with_whisper(url: str) -> str:
    """Download audio using stealth yt-dlp and transcribe using Groq's Whisper API."""
    print(f"DEBUG: Falling back to Smart Whisper for {url}")
    
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("Groq API Key missing for AI transcription fallback.")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Stealth yt-dlp configuration to bypass 403 Forbidden
        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'outtmpl': os.path.join(tmp_dir, 'audio.%(ext)s'),
            'max_filesize': 25 * 1024 * 1024, # 25MB limit for Groq
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            # Bypasses bot detection by pretending to be an iOS device
            'extractor_args': {'youtube': {'player_client': ['ios']}},
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                audio_path = ydl.prepare_filename(info)
                
                # Check if the extension changed after postprocessing
                if not os.path.exists(audio_path):
                    audio_path = os.path.join(tmp_dir, 'audio.m4a')
                
                # Transcribe via Groq
                with open(audio_path, "rb") as file:
                    transcription = client.audio.transcriptions.create(
                        file=(os.path.basename(audio_path), file.read()),
                        model="whisper-large-v3-turbo",
                        response_format="text",
                        language="en"
                    )
                    return transcription
                    
        except Exception as e:
            print(f"DEBUG: Smart Whisper Failed: {str(e)}")
            raise Exception(f"AI Transcription Failed (YouTube Blocked Download). Status: {str(e)}")

def get_transcript(video_id: str, url: str = None, max_words: int = 4000) -> str:
    """Fetch transcript with multi-stage fallback: manual -> auto -> Smart Whisper."""
    print(f"DEBUG: Processing Video ID: {video_id}")
    
    try:
        # 1. Standard API attempt
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        
    except Exception:
        try:
            # 2. Advanced API attempt (list transcripts)
            transcript_list_obj = YouTubeTranscriptApi.list_transcripts(video_id)
            try:
                transcript_obj = transcript_list_obj.find_manually_created_transcript(['en'])
            except:
                try:
                    transcript_obj = transcript_list_obj.find_generated_transcript(['en'])
                except:
                    # Final API fallback: get any and let's hope it works
                    transcript_obj = next(iter(transcript_list_obj))
            
            transcript_list = transcript_obj.fetch()
            
        except Exception as api_error:
            # 3. Smart Whisper Fallback (if URL is provided)
            if url:
                return transcribe_with_whisper(url)
            else:
                raise Exception(f"Captions unavailable and no URL for fallback: {str(api_error)}")

    # Combine text
    full_text = " ".join([item['text'] for item in transcript_list])
    
    # Word-count limit
    words = full_text.split()
    if len(words) > max_words:
        full_text = " ".join(words[:max_words])
        
    return full_text
