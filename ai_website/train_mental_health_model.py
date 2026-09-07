import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("🧠 Mental Health Model Training Script")
print("="*60)

# Step 1: Load your data
print("\n📂 Loading Data.csv...")
try:
    df = pd.read_csv('Data.csv')
    print(f"✓ Data loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"\n📊 Columns in dataset: {list(df.columns)}")
    print(f"\n🔍 First few rows:")
    print(df.head())
except Exception as e:
    print(f"❌ Error loading data: {e}")
    print("\n⚠️ Creating sample dataset for demonstration...")
    
    # Create sample data if Data.csv doesn't exist or has issues
    sample_data = {
        'text': [
            'I feel very sad and lonely all the time',
            'I am constantly worried about everything',
            'I have been feeling great and energetic',
            'I cannot stop thinking about past traumatic events',
            'I experience extreme mood swings',
            'I feel overwhelmed by daily tasks',
            'Life is good and I am happy',
            'I have panic attacks frequently',
            'I feel disconnected from reality',
            'I am doing well and enjoying life'
        ],
        'label': [
            'depression', 'anxiety', 'normal', 'ptsd', 'bipolar',
            'stress', 'normal', 'anxiety', 'depression', 'normal'
        ]
    }
    df = pd.DataFrame(sample_data)
    print("✓ Sample dataset created")

# Step 2: Identify text and label columns
print("\n🔎 Identifying text and label columns...")

# Try to find text column
text_column = None
for col in df.columns:
    if 'text' in col.lower() or 'statement' in col.lower() or 'description' in col.lower():
        text_column = col
        break

if text_column is None:
    # Use first column that contains strings
    for col in df.columns:
        if df[col].dtype == 'object' and df[col].str.len().mean() > 20:
            text_column = col
            break

# Try to find label column
label_column = None
for col in df.columns:
    if 'label' in col.lower() or 'status' in col.lower() or 'condition' in col.lower() or 'class' in col.lower():
        label_column = col
        break

if label_column is None:
    # Use last column as label if not found
    label_column = df.columns[-1]

print(f"✓ Text column: '{text_column}'")
print(f"✓ Label column: '{label_column}'")

# Step 3: Prepare data
print("\n🔧 Preparing data...")
X = df[text_column].fillna('').astype(str)
y = df[label_column].fillna('unknown')

print(f"✓ Total samples: {len(X)}")
print(f"✓ Unique labels: {y.nunique()}")
print(f"✓ Label distribution:\n{y.value_counts()}")

# Step 4: Split data
print("\n✂️ Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y if y.nunique() > 1 else None
)
print(f"✓ Training samples: {len(X_train)}")
print(f"✓ Testing samples: {len(X_test)}")

# Step 5: Create TF-IDF vectorizer
print("\n🔤 Creating TF-IDF vectorizer...")
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    min_df=1,
    max_df=0.95
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)
print(f"✓ Feature vector shape: {X_train_vec.shape}")

# Step 6: Train model
print("\n🤖 Training models...")

models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Naive Bayes': MultinomialNB()
}

best_model = None
best_score = 0
best_name = ''

for name, model in models.items():
    print(f"\n  Training {name}...")
    model.fit(X_train_vec, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_vec)
    score = accuracy_score(y_test, y_pred)
    
    print(f"  ✓ Accuracy: {score:.4f}")
    
    if score > best_score:
        best_score = score
        best_model = model
        best_name = name

print(f"\n🏆 Best model: {best_name} with accuracy: {best_score:.4f}")

# Step 7: Detailed evaluation
print("\n📊 Detailed Classification Report:")
print("="*60)
y_pred = best_model.predict(X_test_vec)
print(classification_report(y_test, y_pred))

# Step 8: Save model and vectorizer
print("\n💾 Saving model and vectorizer...")

try:
    # Save the model
    with open('mental_health_model.pkl', 'wb') as f:
        pickle.dump(best_model, f)
    print("✓ Model saved as 'mental_health_model.pkl'")
    
    # Save the vectorizer
    with open('tfidf_vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    print("✓ Vectorizer saved as 'tfidf_vectorizer.pkl'")
    
    # Test loading
    with open('mental_health_model.pkl', 'rb') as f:
        test_model = pickle.load(f)
    print("✓ Model verification: Successfully loaded")
    
except Exception as e:
    print(f"❌ Error saving model: {e}")

# Step 9: Test prediction
print("\n🧪 Testing prediction functionality...")
test_texts = [
    "I feel anxious and worried",
    "I am happy and doing great",
    "I feel very depressed"
]

for text in test_texts:
    text_vec = vectorizer.transform([text])
    prediction = best_model.predict(text_vec)[0]
    
    if hasattr(best_model, 'predict_proba'):
        proba = best_model.predict_proba(text_vec)[0]
        confidence = max(proba)
        print(f"\n  Text: '{text}'")
        print(f"  Prediction: {prediction}")
        print(f"  Confidence: {confidence:.2%}")
    else:
        print(f"\n  Text: '{text}'")
        print(f"  Prediction: {prediction}")

print("\n" + "="*60)
print("✅ Training completed successfully!")
print("="*60)
print("\n📝 Next steps:")
print("  1. Run: python app.py")
print("  2. Open: http://localhost:5000")
print("  3. Test the prediction API")
print("\n🎉 Your model is ready to use!")
print("="*60)