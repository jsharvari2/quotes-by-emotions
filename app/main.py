from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
import json
import random
import os

app = FastAPI()

# Step 1: Initialize ChromaDB client and create collection
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="motivational_quotes")

# Step 2: Load quotes from JSON file
with open("quotes.json", "r") as f:
    quotes_data = json.load(f)

# Step 3: Insert into ChromaDB
doc_id = 0
for emotion, quote_list in quotes_data.items():
    for quote in quote_list:
        collection.add(
            documents=[quote],
            metadatas=[{"emotion": emotion}],
            ids=[str(doc_id)]
        )
        doc_id += 1

# Define input schema
class EmotionRequest(BaseModel):
    emotion: str

# Step 4: API to retrieve a quote by emotion
@app.post("/quote")
def get_quote(req: EmotionRequest):
    emotion = req.emotion.lower()
    results = collection.get(where={"emotion": emotion})
    documents = results.get("documents", [])
    
    if documents:
        return {
            "quote": random.choice(documents),
            "matched_emotion": emotion
        }
    return {
        "quote": "No quote found for that emotion.",
        "matched_emotion": emotion
    }

# Step 5: CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Or "*" for all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
