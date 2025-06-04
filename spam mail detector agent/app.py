from flask import Flask, jsonify, request
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
import tkinter as tk
from tkinter import messagebox
import threading
from data import sample_texts, labels
from feature_extraction import extract_features
from groq import Groq

app = Flask(__name__)
groq_api_key = "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"  
client = Groq(api_key=groq_api_key)
rephrase_count = 0

def rephrase_with_groq(text,mode= "subject"):
    global rephrase_count
    if rephrase_count > 3:
        return "Rephrase limit reached"
    if mode == "subject":
        prompt = (
            f"Rephrase the following email subject to be short, professional, and title-style. "
            f"Keep it under 7 words and avoid turning it into a full sentence: {text}"
        )
    else:
        prompt = (
            f"Rephrase the following email body while keeping the meaning intact. "
            f"Improve clarity and grammar, but don't shorten it too much: {text}"
        )
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that rephrases text."},
                {"role": "user", "content":prompt}
            ]
        )
        rephrase_count += 1
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

embedder = SentenceTransformer('paraphrase-MiniLM-L6-v2')
X_train = embedder.encode(sample_texts)
clf = LogisticRegression()
clf.fit(X_train, labels)

def get_prediction_and_confidence(text):
    vec = embedder.encode([text])
    pred = clf.predict(vec)[0]
    conf = max(clf.predict_proba(vec)[0])
    features = extract_features(text)
    return pred, conf, features, vec[0]

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json or {}
    subject = data.get('subject', '')
    body = data.get('body', '')

    subj_pred, subj_conf, _, subj_vec = get_prediction_and_confidence(subject)
    body_pred, body_conf, _, body_vec = get_prediction_and_confidence(body)
    comb_pred, comb_conf, _, comb_vec = get_prediction_and_confidence(subject + ' ' + body)

    return jsonify({
        "subject": {
            "prediction": "Spam" if subj_pred else "Not Spam",
            "confidence": f"{subj_conf * 100:.1f}%"
        },
        "body": {
            "prediction": "Spam" if body_pred else "Not Spam",
            "confidence": f"{body_conf * 100:.1f}%"
        },
        "combined": {
            "prediction": "Spam" if comb_pred else "Not Spam",
            "confidence": f"{comb_conf * 100:.1f}%"
        },
        "embedding": {
            "subject": subj_vec.tolist(),
            "body": body_vec.tolist(),
            "combined": comb_vec.tolist()
        }
    })

def run_gui():
    def check_spam():
        subject = subject_input.get()
        body = body_input.get("1.0", "end").strip()

        if not subject and not body:
            messagebox.showerror("Error", "Please Enter Subject or Body.")
            return

        rephrased_subject = rephrase_with_groq(subject,mode="subject")
        rephrased_body = rephrase_with_groq(body,mode="body")

        rephrase_output_subject.delete(0, tk.END)
        rephrase_output_subject.insert(0, rephrased_subject)

        rephrase_output_body.delete("1.0", tk.END)
        rephrase_output_body.insert("1.0", rephrased_body)

        original = app.test_client().post('/predict', json={"subject": subject, "body": body}).get_json()
        rephrased = app.test_client().post('/predict', json={"subject": rephrased_subject, "body": rephrased_body}).get_json()

        original_subject_prob = original["subject"]["confidence"]
        original_body_prob = original["body"]["confidence"]
        original_combined_prob = original["combined"]["confidence"]

        rephrased_subject_prob = rephrased["subject"]["confidence"]
        rephrased_body_prob = rephrased["body"]["confidence"]
        rephrased_combined_prob = rephrased["combined"]["confidence"]

        message = (
            f"Original Input Subject: {original['subject']['prediction']} ({original_subject_prob})\n"
            f"Original Input Body: {original['body']['prediction']} ({original_body_prob})\n"
            f"Original Input Combined: {original['combined']['prediction']} ({original_combined_prob})\n\n"
            f"Updated Subject: {rephrased['subject']['prediction']} ({rephrased_subject_prob})\n"
            f"Updated Body: {rephrased['body']['prediction']} ({rephrased_body_prob})\n"
            f"Updated Combined: {rephrased['combined']['prediction']} ({rephrased_combined_prob})\n\n"
            f"Rephrases used: {rephrase_count}/3"
        )
        messagebox.showinfo("Spam Detection Results", message)

    window = tk.Tk()
    window.title("Email Spam Detector")

    frame = tk.Frame(window)
    frame.pack(padx=10, pady=10)

    tk.Label(frame, text="Subject Input:").grid(row=0, column=0, sticky="w")
    subject_input = tk.Entry(frame, width=60)
    subject_input.grid(row=1, column=0, padx=5, pady=5)

    tk.Label(frame, text="Updated Subject:").grid(row=0, column=1, sticky="w")
    rephrase_output_subject = tk.Entry(frame, width=60)
    rephrase_output_subject.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame, text="Body Input:").grid(row=2, column=0, sticky="w")
    body_input = tk.Text(frame, width=60, height=10)
    body_input.grid(row=3, column=0, padx=5, pady=5)

    tk.Label(frame, text="Updated Body:").grid(row=2, column=1, sticky="w")
    rephrase_output_body = tk.Text(frame, width=60, height=10)
    rephrase_output_body.grid(row=3, column=1, padx=5, pady=5)

    tk.Button(window, text="Submit & Update", command=check_spam).pack(pady=10)

    window.mainloop()

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(debug=False, use_reloader=False)).start()
    run_gui()
