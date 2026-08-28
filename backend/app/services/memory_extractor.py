import json
import re
from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def extract_facts_from_chat(conversation_history: list) -> dict:
    extraction_prompt = """
Extract long-term facts about the user from the conversation.
Only extract what the user clearly stated.
Do not invent anything.

Return ONLY valid JSON in this exact shape:
{
  "name": null,
  "goals": [],
  "plans": [],
  "preferences": []
}

Rules:
- name: string or null
- goals/plans/preferences: arrays of short strings
- If nothing new is found, keep name as null and arrays empty
"""

    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {"role": "system", "content": extraction_prompt},
            *conversation_history[-6:]
        ],
        temperature=0,
        max_tokens=200
    )

    content = response.choices[0].message.content or ""

    match = re.search(r"\{.*\}", content, re.DOTALL)
    if not match:
        return {
            "name": None,
            "goals": [],
            "plans": [],
            "preferences": []
        }

    try:
        data = json.loads(match.group())
    except json.JSONDecodeError:
        return {
            "name": None,
            "goals": [],
            "plans": [],
            "preferences": []
        }

    return {
        "name": data.get("name") or None,
        "goals": data.get("goals") or [],
        "plans": data.get("plans") or [],
        "preferences": data.get("preferences") or []
    }