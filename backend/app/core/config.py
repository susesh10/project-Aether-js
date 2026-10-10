from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # MongoDB
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "akari")

    # Models
    MODEL_NAME: str = os.getenv("MODEL_NAME", "openai/gpt-oss-120b")
    MODEL_FAST: str = os.getenv("MODEL_FAST", "openai/gpt-oss-20b")


settings = Settings()

ALLOWED_MODELS = {
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
}


def resolve_model(requested: str | None = None) -> str:
    name = (requested or settings.MODEL_NAME or "").strip()
    if name in ALLOWED_MODELS:
        return name
    return settings.MODEL_NAME