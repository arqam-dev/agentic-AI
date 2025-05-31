from flask import Flask, jsonify, request
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import tkinter as tk
from tkinter import messagebox
import threading
import re

from data import sample_texts, labels
from feature_extraction import extract_features

app= Flask(__name__)
