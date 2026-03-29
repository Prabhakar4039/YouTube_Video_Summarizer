from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def chat_with_video(question: str, transcript: str) -> str:
    if not os.getenv("GROQ_API_KEY"):
        return "Error: Missing GROQ_API_KEY."

    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    prompt = (
        "You are an AI assistant that has access to a YouTube video's transcript. "
        "Answer the user's question accurately using only the video content. "
        "If you don't know the answer or it's not in the transcript, say so."
        f"\n\nTranscript:\n{transcript}\n\nUser Question:\n{question}"
    )

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Chat Error: {str(e)}"
