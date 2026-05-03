from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Mock Database
LIBRARY_DATA = {
    "books": {
        "the great gatsby": "Available - Shelf A1",
        "1984": "Checked out - Due: May 15, 2026",
        "the hobbit": "Available - Shelf C4",
        "atlas shrugged": "Checked out - Due: May 20, 2026"
    },
    "hours": "Monday - Friday: 9 AM - 8 PM | Saturday: 10 AM - 4 PM | Sunday: Closed"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.json.get("message", "").lower()
    
    if "hour" in user_message or "open" in user_message:
        response = f"Our current hours are: {LIBRARY_DATA['hours']}"
    
    elif "book" in user_message or "find" in user_message:
        # Check if a specific book title from our DB is in the message
        found = False
        for title, status in LIBRARY_DATA['books'].items():
            if title in user_message:
                response = f"Found it! '{title.title()}': {status}"
                found = True
                break
        if not found:
            response = "I can help find books! Try asking about '1984' or 'The Hobbit'."
            
    elif "due date" in user_message:
        response = "To check a specific due date, please provide the book title."
    
    else:
        response = "I'm your Library Assistant. You can ask about our opening hours or the availability of a book."

    return jsonify({"reply": response})

if __name__ == '__main__':
    app.run(debug=True)