from sklearn import flask,josify , request
from sklearn.feature_extraction.text  import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import re

app = (__name__)

texts =[

#spam text

    "Win money now!", "Limited time offer!", "Call this number now",
    "Congratulations, you've won a prize!", "Free gift card waiting for you",
    "Click here to claim your reward", "You're our lucky winner!",
    "Act now - limited supplies!", "Special promotion just for you",
    "Risk-free opportunity", "Guaranteed results", "No credit check needed",
    "Double your income today", "Work from home and earn $5000/week",
    "Exclusive deal for selected customers", "Your account has been compromised",
    "Urgent: action required", "Final notice", "You've been selected",
    "Limited seats available",

#ham text
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
labels= [1] * [20] + [0] * [20] # 1 = spam , 0 = ham

model= Pipeline([
    ('vetorizer', CountVectorizer(analyzer='word', ngram_range=(1,2))),
    ('tfidf', TfidfTransformer()),
    ('classifier',MultinomialNB())
])
model.fit(texts, labels)