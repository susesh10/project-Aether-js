from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
app = FastAPI(title="Akari")

converstion_history = []
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
    converstion_history.append({"role": "user","content": request.message})
    user_message = request.message
    reply = f"akari heard: {user_message}"
    converstion_history.append({"role": "assistant","content": reply})
    return {
        "reply": f"Akari heard: {user_message}",
        "emotion": "happy"
    }