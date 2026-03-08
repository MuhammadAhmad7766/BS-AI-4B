from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)

# Route for home page
@app.route('/')
def home():
    return render_template('index.html')

# API route to fetch a random joke
@app.route('/joke')
def get_joke():
    # Using free joke API
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    
    if response.status_code == 200:
        joke_data = response.json()
        return jsonify({
            "setup": joke_data['setup'],
            "punchline": joke_data['punchline']
        })
    else:
        return jsonify({"error": "Unable to fetch joke"}), 500

if __name__ == '__main__':
    app.run(debug=True)