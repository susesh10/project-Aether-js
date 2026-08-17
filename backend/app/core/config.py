from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    
    MODEL_NAME: str = "openai/gpt-oss-20b"

settings = Settings()