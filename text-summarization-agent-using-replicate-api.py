import os
import threading
import time
from flask import Flask, request, jsonify
import replicate
import requests

# ------------------ Flask App Setup ------------------ #
app = Flask(__name__)

@app.route('/')
def home():
    return "<h1> Welcome to Text Summarization Agent </h1>"

@app.route('/summarize', methods=['POST'])
def summarize_text():
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "Invalid JSON or 'text' key not provided"}), 400

    text_to_summarize = data.get("text")

    try:
        client = replicate.Client(api_token="r8_1oZGFvx7JFfo400P29PyFVy6FXT1N6c1mdJgy")  # Use your actual token

        output = client.run(
            "meta/meta-llama-3-8b-instruct",
            input={
                "prompt": f"Summarize the following text:\n\n{text_to_summarize}",
                "max_new_tokens": 300,
                "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a helpful assistant that summarizes text.<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
            }
        )

        summarized_text = "".join(output)
        return jsonify({"summary": summarized_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------ API Test Function ------------------ #
def test_api():
    time.sleep(3)  
    url = "http://127.0.0.1:5000/summarize"
    data = {
        "text": "Climate change refers to long-term shifts in temperatures and weather patterns. These changes may be natural, such as through variations in the solar cycle. However, since the 1800s, human activities have been the main driver of climate change, primarily due to burning fossil fuels like coal, oil, and gas. Burning these materials releases greenhouse gases such as carbon dioxide, which trap heat in the atmosphere, leading to global warming. The effects include rising sea levels, more extreme weather events, and impacts on ecosystems and biodiversity."
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

# ------------------ Main Entry Point ------------------ #
if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(debug=False, use_reloader=False)).start()
    test_api()
