import os
from flask import Flask, request, jsonify, render_template_string
import replicate

app = Flask(__name__)


html_form = """
<!DOCTYPE html>
<html>
<head>
    <title>Story Generator</title>
</head>
<body>
    <h1>Story Generator</h1>
    <form method="POST" action="/generate_story">
        <label for="topic">Enter a topic:</label><br>
        <input type="text" id="topic" name="topic" required><br><br>
        <input type="submit" value="Generate Story">
    </form>
    {% if story %}
    <h2>Generated Story:</h2>
    <p>{{ story }}</p>
    {% elif error %}
    <h2 style="color: red;">Error:</h2>
    <p>{{ error }}</p>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def home():
    return "<h1>Welcome to the Story Generator Agent</h1><p>Go to <a href='/generate_story'>/generate_story</a> to use the form.</p>"

@app.route('/generate_story', methods=['GET', 'POST'])
def generate_story():
    if request.method == 'POST':
        topic = request.form.get('topic')
        if not topic:
            return render_template_string(html_form, error="No topic provided")

        prompt = f"Write a detailed story or script about: {topic}"

        response = {
            "prompt": prompt,
            "max_new_tokens": 512,
            "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        }

        try:
            client = replicate.Client(api_token="r8_VjMqeBx3INSDbrK9Czav9oaKHQxWUaw2wR2nj")  
            output = client.run("meta/meta-llama-3-8b-instruct", input=response)
            output_text = "".join(output)
            return render_template_string(html_form, story=output_text)
        except Exception as e:
            return render_template_string(html_form, error=str(e))
    
    
    return render_template_string(html_form)

if __name__ == "__main__":
    app.run(debug=True)
