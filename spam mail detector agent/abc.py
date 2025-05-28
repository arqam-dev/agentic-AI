from flask import Flask, jsonify, request
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import re
import tkinter as tk
from tkinter import messagebox
import threading

app = Flask(__name__)

sample_texts = [
    "Win money now!", "Limited time offer!", "Call this number now",
    "Congratulations, you've won a prize!", "Free gift card waiting for you",
    "Click here to claim your reward", "You're our lucky winner!",
    "Act now - limited supplies!", "Special promotion just for you",
    "Risk-free opportunity", "Guaranteed results", "No credit check needed",
    "Double your income today", "Work from home and earn $5000/week",
    "Exclusive deal for selected customers", "Your account has been compromised",
    "Urgent: action required", "Final notice", "You've been selected",
    "Limited seats available",
    "Hello, how are you?", "Let's meet tomorrow", "Please find the report attached",
    "The meeting is scheduled for 2pm", "I'll send you the documents soon",
    "Thanks for your email", "Looking forward to our discussion",
    "Can we reschedule our appointment?", "Here's the information you requested",
    "Please review the attached proposal", "Let me know your thoughts on this",
    "The project is progressing well", "We need to discuss the budget",
    "Team lunch next Friday", "Reminder: department meeting at 3pm",
    "The client approved the design", "I'm following up on our conversation",
    "Here are the meeting notes", "Can you help with this task?",
    "Thanks for your help with this"
]
labels = [1] * 20 + [0] * 20  

spam_detector = Pipeline([
    ('vectorizer', CountVectorizer(ngram_range=(1, 2))),
    ('tfidf', TfidfTransformer()),
    ('classifier', MultinomialNB())
])
spam_detector.fit(sample_texts, labels)

def extract_features(text):
    return {
        'has_urgent': int(bool(re.search(r'\b(urgent|immediate|act now|limited time)\b', text, re.I))),
        'has_winner': int(bool(re.search(r'\b(win|winner|won|prize|reward|free|gift)\b', text, re.I))),
        'has_link': int(bool(re.search(r'http[s]?://|www\.', text))),
        'has_number': int(bool(re.search(r'\d{10,}', text))),
        'has_special_chars': int(bool(re.search(r'[!$%^&*()_+|~={}\[\]:";\'<>?,./]', text))),
        'has_caps': int(sum(1 for c in text if c.isupper()) / len(text) > 0.3 if text else 0),
        'length': len(text)
    }

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json or {}
    subject = data.get('subject', '')
    body = data.get('body', '')

    def get_result(text):
        prediction = spam_detector.predict([text])[0]
        confidence = spam_detector.predict_proba([text])[0].max()
        features = extract_features(text)
        return prediction, confidence, features

    subj_pred, subj_conf, _ = get_result(subject)
    body_pred, body_conf, _ = get_result(body)
    comb_pred, comb_conf, _ = get_result(subject + ' ' + body)

    return jsonify({
        "subject": {"prediction": "Spam" if subj_pred else "Not Spam", "confidence": round(subj_conf, 2)},
        "body": {"prediction": "Spam" if body_pred else "Not Spam", "confidence": round(body_conf, 2)},
        "combined": {"prediction": "Spam" if comb_pred else "Not Spam", "confidence": round(comb_conf, 2)}
    })

def run_gui():
    def check_spam():
        subject = subject_input.get()
        body = body_input.get("1.0", "end").strip()

        if not subject and not body:
            messagebox.showerror("Error", "Please Enter Subject or Body.")
            return

        response = app.test_client().post('/predict', json={"subject": subject, "body": body})
        result = response.get_json()

        message = (
            f"Subject: {result['subject']['prediction']} ({result['subject']['confidence']*100:.1f}%)\n"
            f"Body: {result['body']['prediction']} ({result['body']['confidence']*100:.1f}%)\n"
            f"Combined: {result['combined']['prediction']} ({result['combined']['confidence']*100:.1f}%)"
        )
        messagebox.showinfo("Spam Detection Result", message)

    window = tk.Tk()

    window.title(" Email Spam Detector")
    tk.Label(window, text="Subject:").pack()
    subject_input = tk.Entry(window, width=60)
    subject_input.pack()

    tk.Label(window,text=" Body:").pack()
    body_input = tk.Text(window, width=60, height=10)
    body_input.pack()

    tk.Button(window, text="Submit", command=check_spam).pack(pady=10)
    window.mainloop()

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(debug=False)).start()
    run_gui()
