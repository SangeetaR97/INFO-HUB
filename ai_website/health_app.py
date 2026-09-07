# pip install wordcloud matplotlib seaborn scikit-learn nltk

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from collections import Counter
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')

import re
import string
import pickle
import os

# Check current working directory
print("Current Directory:", os.getcwd())
print("File exists:", os.path.isfile("Data.csv"))

# Read the CSV file
df = pd.read_csv("Data.csv")
print(df.head())

# Basic data exploration
print("\nMissing values:")
print(df.isnull().sum())
print("\nShape:", df.shape)
print("Duplicates:", df.duplicated().sum())
print("\nInfo:")
df.info()
print("\nDescription:")
print(df.describe())

# Drop rows with missing values in 'statement' and 'status'
df = df.dropna(subset=['statement', 'status'])
print("\nMissing values after dropping:", df['statement'].isnull().sum())
print("Shape after dropping missing values:", df.shape)

# Reset index
df.reset_index(drop=True, inplace=True)

# Convert data types
df['statement'] = df['statement'].astype(str)
df['status'] = df['status'].astype('category')

# 1. Distribution of Mental Health Statuses
plt.figure(figsize=(8, 5))
sns.countplot(data=df, x='status', order=df['status'].value_counts().index, palette='viridis')
plt.title("Distribution of Mental Health Statuses")
plt.xlabel("Mental Health Status")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 2. Sentiment Distribution (alternative visualization)
plt.figure(figsize=(8, 5))
sns.countplot(y=df["status"], order=df["status"].value_counts().index, palette='viridis')
plt.title("Sentiment Distribution")
plt.tight_layout()
plt.show()

# 3. Word Cloud for the Most Frequent Words in Statements
all_text = " ".join(statement for statement in df['statement'].astype(str))

plt.figure(figsize=(10, 6))
wordcloud = WordCloud(width=800, height=400, background_color="black", colormap="viridis").generate(all_text)
plt.imshow(wordcloud, interpolation='bilinear')
plt.title("Word Cloud of All Statements")
plt.axis("off")
plt.show()

# 4. Text Length Distribution by Mental Health Status
df['text_length'] = df['statement'].astype(str).apply(len)
plt.figure(figsize=(8, 5))
sns.boxplot(data=df, x='status', y='text_length', palette='viridis')
plt.title("Text Length Distribution by Mental Health Status")
plt.xlabel("Mental Health Status")
plt.ylabel("Text Length")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 5. Most Common Words in Each Status
def most_common_words(text):
    words = text.lower().split()
    words = [word for word in words if word not in stopwords.words('english')]
    word_counts = Counter(words)
    return word_counts.most_common(10)

for status in df['status'].unique():
    status_text = " ".join(df[df['status'] == status]['statement'].astype(str))
    common_words = most_common_words(status_text)
    if common_words:
        words, counts = zip(*common_words)
        
        plt.figure(figsize=(8, 5))
        sns.barplot(x=list(words), y=list(counts), palette='viridis')
        plt.title(f"Top 10 Common Words in {status} Statements")
        plt.xlabel("Words")
        plt.ylabel("Count")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

# Text Cleaning Function
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>+', '', text)
    text = re.sub(f'[{re.escape(string.punctuation)}]', '', text)
    text = re.sub(r'\n', '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    return text

# Test cleaning function
sample = "i am n't busy"
print("\nCleaned sample text:", clean_text(sample))

# Apply text cleaning to statements
df['statement'] = df['statement'].astype(str).apply(clean_text)

# Encode labels
label_encoder = LabelEncoder()
df['status'] = label_encoder.fit_transform(df['status'])

# Check class distribution
print("\nClass distribution:")
print(df['status'].value_counts())

# Prepare features and target
X = df['statement']
y = df['status']

# Train-test split with stratification
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=42
)

# TF-IDF Vectorization with bigrams
tfidf = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

# Train Multinomial Naive Bayes Model
print("\n=== Training Multinomial Naive Bayes ===")
model_nb = MultinomialNB()
model_nb.fit(X_train_tfidf, y_train)

y_pred_train = model_nb.predict(X_train_tfidf)
print("Training Accuracy:", accuracy_score(y_train, y_pred_train))
print(classification_report(y_train, y_pred_train))

y_pred = model_nb.predict(X_test_tfidf)
print("Test Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

conf_mat = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(conf_mat, annot=True, fmt='d', cmap='Blues', 
            xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
plt.title("Confusion Matrix - Naive Bayes")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.show()

# Train Logistic Regression Model with class weights
print("\n=== Training Logistic Regression ===")
model = LogisticRegression(class_weight='balanced', max_iter=1000)
model.fit(X_train_tfidf, y_train)

y_pred = model.predict(X_test_tfidf)
print("Test Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

conf_mat = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(conf_mat, annot=True, fmt='d', cmap='Blues', 
            xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
plt.title("Confusion Matrix - Logistic Regression")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.show()

# Save the model and vectorizer
pickle.dump(model, open("mental_health_model.pkl", "wb"))
pickle.dump(tfidf, open("tfidf_vectorizer.pkl", "wb"))
print("\nModel and vectorizer saved successfully!")

# Load the model and vectorizer
loaded_model = pickle.load(open("mental_health_model.pkl", "rb"))
loaded_tfidf = pickle.load(open("tfidf_vectorizer.pkl", "rb"))

# Recommendation function
def provide_recommendation(label):
    recommendations = {
        "Normal": "You seem to be in a balanced state. Keep practicing healthy routines and mindfulness.",
        "Depression": "You might be feeling low. Please talk to someone you trust or consider professional support.",
        "Anxiety": "If you're feeling anxious, try breathing exercises or meditation. Seek help if it persists.",
        "Suicidal": "Your message is deeply concerning. Please seek immediate help from a mental health professional or a helpline.",
        "Personality disorder": "It may help to explore therapy options tailored to your personality experiences.",
        "Bipolar": "Managing mood swings can be challenging. It's helpful to maintain a routine, track your moods, and stay connected with a mental health professional.",
        "Other": "Consider monitoring your mental state and journaling your thoughts. If discomfort grows, seek help."
    }
    return recommendations.get(label, "We're here for you. Consider reaching out for support when needed.")

# Test predictions with sample inputs
print("\n=== Testing Predictions ===")
sample = input("Enter your caption: ")
sample_text = [sample]
sample_tfidf = loaded_tfidf.transform(sample_text)
prediction = loaded_model.predict(sample_tfidf)
predicted_status = label_encoder.inverse_transform(prediction)[0]

print("Predicted Status:", predicted_status)
print("Recommendation:", provide_recommendation(predicted_status))

# Example test cases (commented out for interactive use):
# Test cases:
# "getting sleepy" -> Normal
# "Im tired of everything. Cant wait to die." -> Suicidal
# "i feel so sad" -> Depression
# "i feel so nervous" -> Anxiety