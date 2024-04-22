from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Route to serve the HTML file
@app.route('/')
def index():
    return render_template('Recommend.html')

# Route to handle AJAX requests to the FastAPI backend
@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    # Make request to FastAPI backend
    response = requests.get(f'http://localhost:8000/locations?query={query}')
    return jsonify(response.json())

# Route to handle form submission for location recommendations
@app.route('/recommend', methods=['POST'])
def recommend():
    name = request.form.get('name')
    description = request.form.get('description')
    category = request.form.get('category')
        # Make request to FastAPI backend
    response = requests.post('http://localhost:8000/recommendations', json={"name": name, "description": description, "category": category})
    if response.status_code == 200:
        return 'Recommendation submitted successfully!'
    else:
        return 'Failed to submit recommendation'



if __name__ == '__main__':
    app.run(debug=True)
