# backend/database.py

from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "model_store"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

models_collection = db["models"]
