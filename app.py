# Improved Error Handling, Data Validation, and Code Refactoring in app.py

import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Improved Route Example
@app.route('/data', methods=['POST'])
def handle_data():
    try:
        # Validate incoming JSON data
        data = request.get_json()
        if not data or 'key' not in data:
            return jsonify({'error': 'Invalid input: Missing key'}), 400

        # Process data
        result = process_data(data['key'])
        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Example data processing function

def process_data(key):
    # Add logic here
    return f'Processed {key}'

if __name__ == '__main__':
    app.run(debug=True)
