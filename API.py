from fastapi import FastAPI
from sentence_transformers import SentenceTransformer, util
from locations import locations
import torch
import uvicorn

app = FastAPI()

# pre-trained model for semantic similarity
model = SentenceTransformer("distilbert-base-nli-stsb-mean-tokens")

# Location search endpoint with semantic search
@app.get("/locations")
async def search_locations(query: str):
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
