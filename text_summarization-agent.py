import os
import threading
from flask import Flask, request, jsonify
from transformers import pipeline
import requests
import time


app = Flask(__name__)


summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@app.route('/')
def home():
    return "<h1> Welcome to Text Summarization Agent </h1>"

@app.route('/summarize', methods=['POST'])
def summarize_text():
    data = request.get_json()
    
    if not data or "text" not in data:
        return jsonify({"error": "Invalid JSON or 'text' key not provided"}), 400

    text_to_summarize = data["text"]

    try:
        summary = summarizer(text_to_summarize, max_length=100, min_length=30, do_sample=False)
        return jsonify({"summary": summary[0]['summary_text']})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def test_api():
    time.sleep(2)  
    
    url = "http://127.0.0.1:5000/summarize"
    data = {
        "text": "Artificial intelligence is rapidly transforming the world. It enables machines to learn from data and perform tasks like speech recognition, decision-making, and language translation. These capabilities are helping industries become more efficient and are creating new opportunities for innovation"
    }

    try:
        response = requests.post(url, json=data)
        print("Status Code:", response.status_code)
        if response.status_code == 200:
            print("Summary:", response.json().get("summary"))
        else:
            print("Error:", response.json())
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(debug=False, use_reloader=False)).start()
    test_api()
