from pymongo import MongoClient
from app.core.config import settings

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]

# Collection for long-term memory
memory_collection = db["memory"]