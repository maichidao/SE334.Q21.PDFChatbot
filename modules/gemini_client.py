from dotenv import load_dotenv
import os
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def ask_gemini(prompt: str) -> str:
    """Gửi prompt và trả lời text response."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text


def ask_gemini_stream(prompt: str):
    """Gửi prompt và trả về generator cho streaming response."""
    response = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=prompt
    )
    for chunk in response:
        if chunk.text:
            yield chunk.text