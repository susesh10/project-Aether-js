import edge_tts
import tempfile
import re

DEFAULT_VOICE = "en-US-JennyNeural"

def clean_text_for_speech(text: str) -> str:
    # Remove emojis / symbols that sound bad when spoken
    text = re.sub(
        r"[\U00010000-\U0010ffff]",
        "",
        text,
        flags=re.UNICODE
    )
    # Remove leftover decorative symbols
    text = re.sub(r"[*#_~`>]+", " ", text)
    # Collapse extra spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text

async def text_to_speech(text: str, voice: str = DEFAULT_VOICE) -> str:
    text = clean_text_for_speech(text)

    if not text:
        raise ValueError("Text is empty after cleaning")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_path = tmp.name
    tmp.close()

    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(tmp_path)

    return tmp_path