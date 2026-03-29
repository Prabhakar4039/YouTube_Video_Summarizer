from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# Recommended models: llama-3.3-70b-versatile, mixtral-8x7b-32768
model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

def summarize_text(transcript: str, custom_prompt: str = "") -> str:
    """Generate a summary of the transcript using Groq API."""
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("Groq API Key is missing. Please check your `.env` file.")
    
    system_instruction = (
        "You are an expert content summarizer. Your goal is to provide a comprehensive "
        "yet concise summary of a YouTube video transcript. Highlight the key points, "
        "the main takeaway, and any important data or mentions."
    )
    
    user_content = f"Transcript:\n{transcript}\n\n"
    if custom_prompt:
        user_content += f"Additional Request: {custom_prompt}\n"
    
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content}
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        return completion.choices[0].message.content
        
    except Exception as e:
        raise Exception(f"Groq Summarization failed: {str(e)}")

# Example usage
if __name__ == "__main__":
    t = "This is a dummy transcript for testing purposes."
    try:
        # print(summarize_text(t))
        pass
    except Exception as e:
        print(e)
