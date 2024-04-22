from fastapi import FastAPI
from sentence_transformers import SentenceTransformer, util
import torch
import uvicorn
from pydantic import BaseModel
from typing import List
import json
from fastapi.middleware.cors import CORSMiddleware

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

# Load locations data
locations = load_locations()

# Location search endpoint with semantic search
@app.get("/locations")
async def search_locations(query: str):
    try:
        # Encode the query into a dense vector representation
        query_embedding = model.encode(query, convert_to_tensor=True)

        # Compute semantic similarity scores between the query and location descriptions
        location_descriptions = [loc["description"] for loc in locations]
        description_embeddings = model.encode(location_descriptions, convert_to_tensor=True)
        similarity_scores = util.pytorch_cos_sim(query_embedding.unsqueeze(0), description_embeddings)

        # Combine location data with similarity scores
        results = [{"name": loc["name"], "description": loc["description"], "category": loc["category"], "score": score.item()} for loc, score in zip(locations, similarity_scores.squeeze())]

        # Sort locations by similarity scores in descending order
        results.sort(key=lambda x: x["score"], reverse=True)

        return {"query": query, "results": results}
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
        
        return recommendation
    except Exception as e:
        return {"error": str(e)}
    


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
    