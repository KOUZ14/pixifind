from fastapi import FastAPI
from sentence_transformers import SentenceTransformer, util
import torch
import uvicorn
from pydantic import BaseModel
from typing import List
import json
from fastapi.middleware.cors import CORSMiddleware
from DB import get_locations, update_locations

app = FastAPI()


# Allow requests from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# pre-trained model for semantic similarity
model = SentenceTransformer("distilbert-base-nli-stsb-mean-tokens")

# Function to load locations from JSON file
def load_locations():
    with open("locations.json", "r") as f:
        locations = json.load(f)
    return locations


# Location search endpoint with semantic search
@app.get("/locations")
async def search_locations(query):
    try:
        results = get_locations(str(query))
        locations = []
        j=0
        for i in results["documents"][j]:
            locations.append(i)
            j+=1
        print(locations)

        return {"query": query, "results": locations}
    except Exception as e:
        return {"error": str(e)}

class LocationRecommendation(BaseModel):
    name: str
    description: str
    category: str

# Endpoint to accept location recommendations
@app.post("/recommendations", response_model=LocationRecommendation)
def add_recommendation(recommendation: LocationRecommendation):
    try:
        # Load locations from JSON file
        with open("locations.json", "r") as f:
            locations = json.load(f)
        
        # Append the recommendation to the locations list
        locations.append(recommendation.model_dump())
        
        # Write updated locations back to JSON file
        with open("locations.json", "w") as f:
            json.dump(locations, f, indent=4)

        locations_data = load_locations()
        
        return recommendation
    except Exception as e:
        return {"error": str(e)}
    


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=9000)
    