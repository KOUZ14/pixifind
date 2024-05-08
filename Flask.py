from flask import Flask, render_template, request, jsonify
import requests
from API import store_image_to_s3
import asyncio
import urllib.parse

app = Flask(__name__)

async def upload_image_to_s3(image):
    image_url = await store_image_to_s3(image)
    return image_url

# Route to serve the HTML file
@app.route('/')
def index():
    return render_template('Recommend.html')

# Route to handle AJAX requests to the FastAPI backend
@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    # Make request to FastAPI backend
    response = requests.get(f'http://localhost:9000/locations?query={query}')
    return jsonify(response.json())

# Route to handle form submission for location recommendations
@app.route('/recommend', methods=['POST'])
def recommend():
    name = request.form.get('name')
    link = request.form.get('link')
    description = request.form.get('description')
    images = ""

    # Handle image uploads
    for file in request.files.getlist('images'):
        # Store image in S3 and get the image URL
        image_url_coroutine = store_image_to_s3(file)
        image_url = asyncio.run(image_url_coroutine)
        #encoded_url = urllib.parse.quote(image_url, safe='')
        images = str(image_url)
        # Make request to FastAPI backend
    print(name)
    print(images)
    response = requests.post('http://localhost:9000/recommendations', json={"name": f"{name}","link":f"{link}", "description": description,"images":f"{images}"})
    if response.status_code == 200:
        return 'Recommendation submitted successfully!'
    else:
        return 'Failed to submit recommendation'



if __name__ == '__main__':
    app.run(debug=True)
