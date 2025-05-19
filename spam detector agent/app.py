from flask import Flask, jsonify, request
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import re

app = Flask(__name__)


texts = [
    # spam
    "Win money now!", "Limited time offer!", "Call this number now",
    "Congratulations, you've won a prize!", "Free gift card waiting for you",
    "Click here to claim your reward", "You're our lucky winner!",
    "Act now - limited supplies!", "Special promotion just for you",
    "Risk-free opportunity", "Guaranteed results", "No credit check needed",
    "Double your income today", "Work from home and earn $5000/week",
    "Exclusive deal for selected customers", "Your account has been compromised",
    "Urgent: action required", "Final notice", "You've been selected",
    "Limited seats available",
    # ham
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

labels = [1] * 20 + [0] * 20  # 1 = spam, 0 = ham

# Model pipeline
model = Pipeline([
    ('vectorizer', CountVectorizer(analyzer='word', ngram_range=(1, 2))),
    ('tfidf', TfidfTransformer()),
    ('classifier', MultinomialNB())
])

model.fit(texts, labels)

def extract_spam_features(text):
    """Extra spam indicators"""
    features = {
        'has_urgent': int(bool(re.search(r'\b(urgent|immediate|act now|limited time)\b', text, re.I))),
        'has_winner': int(bool(re.search(r'\b(win|winner|won|prize|reward|free|gift)\b', text, re.I))),
        'has_link': int(bool(re.search(r'http[s]?://|www\.', text))),
        'has_number': int(bool(re.search(r'\d{10,}', text))),
        'has_special_chars': int(bool(re.search(r'[!$%^&*()_+|~=`{}\[\]:";\'<>?,./]', text))),
        'has_caps': int(sum(1 for c in text if c.isupper()) / len(text) > 0.3 if text else 0),
        'length': len(text)
    }
    return features

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        insert_text = request.json.get('text', '')
    else:
        insert_text = request.args.get('text', "Congratulations, you've been selected for a job!")

    if not insert_text:
        return jsonify({"error": "No text provided"}), 400

    prediction = model.predict([insert_text])[0]
    probability = model.predict_proba([insert_text])[0].max()
    spam_features = extract_spam_features(insert_text)

    result = {
        "input": insert_text,
        "prediction": "Spam" if prediction == 1 else "Not Spam",
        "confidence": round(float(probability), 2),
        "spam_indicators": spam_features,
        "spam_score": sum(spam_features.values())
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
