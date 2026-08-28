from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai import get_ai_reply
from app.services.memory import get_memory, update_memory, merge_memory_update
from app.services.memory_extractor import extract_facts_from_chat

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
                # 4–6. Memory extraction + save
        try:
            extracted = extract_facts_from_chat(conversation_history)
            current_memory = get_memory()
            fields_to_update = merge_memory_update(current_memory, extracted)
        
            if fields_to_update:
                update_memory(fields_to_update)
        except Exception as memory_error:
            print("Memory update failed:", memory_error)
            # Do not break the chat if memory fails
        if len(conversation_history) >10 :
            conversation_history[:] = conversation_history[-10:]
    
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