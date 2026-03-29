from youtube_transcript_api import YouTubeTranscriptApi
import re
import os
import yt_dlp
from groq import Groq
from dotenv import load_dotenv
import tempfile

# Load env
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_video_id(url: str) -> str:
    patterns = [r'(?:v=|\/|embed\/|shorts\/)([0-9A-Za-z_-]{11})']
    for p in patterns:
        match = re.search(p, url)
        if match: return match.group(1)
    return url if len(url) == 11 else None

def transcribe_with_whisper(url: str) -> str:
    """Download audio and transcribe using Groq's Whisper API."""
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("Groq API Key missing for Whisper fallback.")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # 1. Download audio only
        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'outtmpl': os.path.join(tmp_dir, 'audio.%(ext)s'),
            'max_filesize': 25 * 1024 * 1024, # 25MB limit for Groq
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }],
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                audio_path = ydl.prepare_filename(info)
                
                # In some cases, prepare_filename doesn't match the final output after postprocessing
                if not os.path.exists(audio_path):
                    audio_path = os.path.join(tmp_dir, 'audio.m4a')
                
                # 2. Transcribe via Groq
                with open(audio_path, "rb") as file:
                    transcription = client.audio.transcriptions.create(
                        file=(os.path.basename(audio_path), file.read()),
                        model="whisper-large-v3-turbo",
                        response_format="text",
                        language="en"
                    )
                    return transcription
                    
        except Exception as e:
            raise Exception(f"Whisper Fallback Failed: {str(e)}")

def get_transcript(video_id: str, url: str = None, max_words: int = 4000) -> str:
    """Fetch transcript normally or fallback to Whisper if subtitles are disabled."""
    try:
        # Standard API attempt
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([item['text'] for item in transcript_list])
        
        words = full_text.split()
        if len(words) > max_words:
            full_text = " ".join(words[:max_words])
            
        return full_text
        
    except Exception as api_error:
        # Fallback to Whisper if URL is provided and transcript API failed
        if url:
            # We don't want to re-download the whole video if it's super long, 
            # but Groq Whisper can handle substantial content.
            return transcribe_with_whisper(url)
        else:
            raise Exception(f"Transcript Error (and no fallback URL): {str(api_error)}")
