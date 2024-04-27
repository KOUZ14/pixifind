import chromadb
import os
import json
from chromadb.utils import embedding_functions
import chromadb.utils.embedding_functions as embedding_functions
from sentence_transformers import SentenceTransformer, util
import torch
import uvicorn
from pydantic import BaseModel



sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")

# Establish a connection to ChromaDB
client = chromadb.HttpClient(host='localhost', port=8000)




collection = client.get_collection(name="locations",embedding_function=sentence_transformer_ef)




def update_locations():
    collection = client.reset

    with open('locations.json', 'r') as f:
        locations_data = json.load(f)
    # Create an empty list to store documents, metadatas, and ids
    documents = []
    metadatas = []
    ids = []
    id=1

    # Generate embeddings and prepare data for insertion into ChromaDB
    for location in locations_data:
        name = location["name"]
        description = location["description"]
        category = location["category"]

        # Append location data to respective lists
        documents.append(name)
        metadatas.append({"description": description, "category": category})
        ids.append(str(id))  # You can use name or any other unique identifier as the ID
        id+=1

    # Add documents, metadatas, and ids to ChromaDB collection
    collection.add(documents=documents, metadatas=metadatas, ids=ids)


def get_locations(query):
    client = chromadb.HttpClient(host='localhost', port=8000)
    collection = client.get_collection(name="locations",embedding_function=sentence_transformer_ef)
    results = collection.query(
        query_texts=[query],
        n_results=2,
        include=['documents']
    )
    return results

