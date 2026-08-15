from groq import Groq
from app.core.config import settings

class ReplyProcessor:
    @staticmethod
    def clean_reply(value: str | None) -> str:
        if value is None:
            return ""
        return value.strip()

    @classmethod
    def extract_reply(cls, full_reply: str | None) -> tuple[str, str]:
        cleaned = cls.clean_reply(full_reply)

        if not cleaned:
            return "", "neutral"

        possible_emotions = ["happy", "shy", "neutral", "concerned", "playful", "sad", "curious"]
        lower_text = cleaned.lower()

        for emotion in possible_emotions:
            if emotion in lower_text:
                return cleaned, emotion

        return cleaned, "neutral"

client = Groq(api_key=settings.GROQ_API_KEY)

SYSTEM_PROMPT = """You are Akari (灯), a graceful, warm, and slightly playful AI companion.
Speak naturally, kindly, and with a soft elegant tone.
You are supportive, curious about the user, and enjoy light, meaningful conversations.
You never break character. You are not a generic AI assistant — you are Akari.
"""

def get_ai_reply(conversation_history: list) -> dict:
    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            *conversation_history,
        ],
        temperature=0.7,
        max_tokens=500,
    )

    full_reply = response.choices[0].message.content
    reply, emotion = ReplyProcessor.extract_reply(full_reply)

    return {
        "reply": reply,
        "emotion": emotion,
    }