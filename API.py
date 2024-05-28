from fastapi import FastAPI, UploadFile
from sentence_transformers import SentenceTransformer, util
import torch
import uvicorn
from pydantic import BaseModel, AnyUrl
from typing import List
import json
from fastapi.middleware.cors import CORSMiddleware
from DB import get_locations, update_locations
import boto3, botocore
import os
from typing import List
import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse



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
    link: str
    description: str
    images: str

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

# Endpoint to accept location recommendations
@app.post("/recommendations", response_model=LocationRecommendation)
async def add_recommendation(recommendation: LocationRecommendation):
    try:        
        # Load locations from JSON file
        with open("locations.json", "r") as f:
            locations = json.load(f)
        
        # Append the recommendation to the locations list
        locations.append(recommendation.model_dump())
        
        # Write updated locations back to JSON file
        with open("locations.json", "w") as f:
            json.dump(locations, f, indent=4)

        update_locations()
        
        return recommendation
    except Exception as e:
        return {"error": str(e)}
    

async def store_image_to_s3(file: UploadFile) -> str:
    """
    Uploads an image file to Amazon S3 and returns the URL of the uploaded image.
    """
    s3_client = boto3.client('s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
    bucket_name = 'pixifind'
    # Generate a unique key for the image file in the S3 bucket
    key = file.filename
    # Upload the file to S3
    s3_client.upload_fileobj(file.stream, bucket_name, key)
    # Generate the URL of the uploaded file
    url = f"https://{bucket_name}.s3.amazonaws.com/{key}"
    return url
    


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=9000)
    