import edge_tts
import tempfile

DEFAULT_VOICE = "en-US-JennyNeural"

async def text_to_speech(text: str, voice: str = DEFAULT_VOICE) -> str:
    if not text or not text.strip():
        raise ValueError("Text is empty")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_path = tmp.name
    tmp.close()

    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(tmp_path)

    return tmp_path