from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# Recommended models: llama-3.3-70b-versatile, mixtral-8x7b-32768
model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

def chat_with_video(transcript: str, user_query: str, chat_history: list = None) -> str:
    """Answer a user question based on the video's transcript context using Groq."""
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("Groq API Key is missing. Please check your `.env` file.")
    
    system_instruction = (
        "You are an expert AI assistant that has been given a transcript from a YouTube video."
        "Answer the user's question accurately using only the provided video transcript."
        "If the answer is not in the transcript, state that clearly."
    )
    
    user_message = f"Transcript Content: {transcript}\n\nUser Question: {user_query}"
    
    messages = [
        {"role": "system", "content": system_instruction},
    ]
    
    if chat_history:
        messages.extend(chat_history)
        
    messages.append({"role": "user", "content": user_message})
    
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        return completion.choices[0].message.content
        
    except Exception as e:
        raise Exception(f"Groq Chat failed: {str(e)}")

if __name__ == "__main__":
    t = "This is a dummy transcript for testing purposes."
    try:
        # print(chat_with_video(t, "What is this for?"))
        pass
    except Exception as e:
        print(e)
