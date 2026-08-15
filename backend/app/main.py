from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai import get_ai_reply

app = FastAPI(title="Akari")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conversation_history = []

@app.get("/")
async def root():
    return {
        "message": "Akari is awake",
        "status": "online"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        conversation_history.append({
            "role": "user",
            "content": request.message
        })

        ai_response = get_ai_reply(conversation_history)

        reply = ai_response["reply"]
        emotion = ai_response["emotion"]

        conversation_history.append({
            "role": "assistant",
            "content": reply
        })

        return {
            "reply": reply,
            "emotion": emotion,
            "history": conversation_history
        }

    except Exception as e:
        return {
            "reply": "I'm sorry, I encountered an error while processing your request.",
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