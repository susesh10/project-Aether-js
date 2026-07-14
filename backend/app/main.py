from fastapi import FastAPI

app = FastAPI(title="Akari")
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
async def chat(user_message: str):
    return {
        "reply": f"Akari heard: {user_message}",
        "emotion": "happy"
    }