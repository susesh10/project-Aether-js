from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os
app = FastAPI(title="Akari")
load_dotenv()
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

conversation_history = []
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class ChatRequest(BaseModel):
    message : str
@app.get("/")
async def root():
    return {
        "message":"Akari is awake",
        "status":"online"
            }
@app.get("/health")
async def health():
    return {
        "status": "healthy"
        }
@app.post("/chat")
async def chat(request: ChatRequest):
    try :
        conversation_history.append({
            "role": "user",
            "content": request.message
        })
        response = groq.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages = [{
                "role": "system",
                "content": """You are Akari (灯), a graceful, warm, and slightly playful AI companion.You speak naturally, kindly, and with a soft elegant tone.You are supportive, curious about the user, and enjoy light, meaningful conversations.You never break character. You are not a generic AI assistant — you are Akari."""
            },
            *conversation_history],
            temperature = 0.7,
            max_tokens=500,
        )
        reply = response.choices[0].message.content
        conversation_history.append({
            "role": "assistant",
            "content": reply
        })
        return {
            "reply":reply,
            "emotion": "happy",
            "history": conversation_history
        }
    except Exception as e:
        return {
            "reply":"i'm sorry, i encountered an error while processing your request.",
            "emotion": "sad",
            "error": str(e),
            "history": conversation_history
        }
@app.post("/clear-history")
async def clear_history():
    conversation_history.clear()
    return {
        "message": "Conversation history has been cleared",
        "status": "success"
    }