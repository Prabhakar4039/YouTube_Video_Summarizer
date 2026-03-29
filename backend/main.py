from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv

# Import our logic
from transcript import extract_video_id, get_transcript
from summarize import summarize_text
from chat import chat_with_video

# Load environment variables
load_dotenv()

app = FastAPI(title="YouTube Video Summarizer API", version="1.0.0")

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request bodies
class TranscribeRequest(BaseModel):
    url: str

class SummarizeRequest(BaseModel):
    transcript: str
    custom_prompt: Optional[str] = None

class ChatRequest(BaseModel):
    transcript: str
    user_query: str
    chat_history: Optional[List[dict]] = None

@app.get("/")
def read_root():
    return {"message": "Welcome to the YouTube Summarizer API. Use /transcribe, /summarize, or /chat."}

@app.post("/transcribe")
async def transcribe(req: TranscribeRequest):
    """Takes a YouTube URL and returns the transcript text."""
    try:
        video_id = extract_video_id(req.url)
        transcript = get_transcript(video_id)
        return {
            "video_id": video_id,
            "transcript": transcript
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize")
async def summarize(req: SummarizeRequest):
    """Summarizes a given transcript using OpenAI."""
    try:
        summary = summarize_text(req.transcript, req.custom_prompt)
        return {"summary": summary}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(req: ChatRequest):
    """Answers a question about the video transcript."""
    try:
        response = chat_with_video(req.transcript, req.user_query, req.chat_history)
        return {"response": response}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
