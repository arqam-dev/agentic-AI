import os
import threading
from flask import Flask, request, jsonify
from transformers import pipeline, set_seed
import requests
import time

app = Flask(__name__)


generator = pipeline("text-generation", model="gpt2")
set_seed(42)  

@app.route('/')
def home():
    return "<h1> Welcome to Text Extension Agent </h1>"

@app.route('/extend', methods=['POST'])
def extend_text():
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "Invalid JSON or 'text' key not provided"}), 400

    text_to_extend = data["text"]

    try:
       
        extended = generator(text_to_extend, max_length=500, num_return_sequences=1)
        return jsonify({"extended_text": extended[0]['generated_text']})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def test_api():
    time.sleep(2)

    url = "http://127.0.0.1:5000/extend"
    data = {
        "text": "The future of artificial intelligence holds great promise. In the coming years,"
    }

    try:
        response = requests.post(url, json=data)
        print("Status Code:", response.status_code)
        if response.status_code == 200:
            print("Extended Text:", response.json().get("extended_text"))
        else:
            print("Error:", response.json())
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(debug=False, use_reloader=False)).start()
    test_api()
