from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_summary(text: str) -> str:
    if not os.getenv("GROQ_API_KEY"):
        return "Error: Missing GROQ_API_KEY."
        
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    prompt = (
        "Provide a high-quality summary of the following YouTube video transcript. "
        "Format your response as follows:\n\n"
        "### TLDR\n(A concise 1-2 sentence summary)\n\n"
        "### Key Highlights\n(A prioritized list of bullet points covering the main takeaways)\n\n"
        f"Transcript:\n{text}"
    )

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Summarization Error: {str(e)}"
