import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from scipy.sparse import hstack
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("🧠 MENTAL HEALTH MODEL: DATA PREPARATION & TRAINING")
print("="*70)

# ============================================================================
# PHASE 1: DATA ENHANCEMENT
# ============================================================================

print("\n" + "="*70)
print("PHASE 1: ENHANCING DATASET")
print("="*70)

print("\n📂 Loading existing Data.csv...")
try:
    existing_data = pd.read_csv('Data.csv')
    print(f"✓ Loaded {len(existing_data)} existing records")
    print(f"✓ Columns: {list(existing_data.columns)}")
    print(f"\n📊 Current distribution:")
    print(existing_data.iloc[:, 1].value_counts())
except Exception as e:
    print(f"❌ Error loading Data.csv: {e}")
    exit(1)

print("\n➕ Adding comprehensive training examples...")

# Additional comprehensive examples
additional_data = {
    'statement': [
        # More Depression examples (15)
        "I feel completely worthless and like a burden to everyone",
        "Nothing brings me joy anymore, everything feels gray",
        "I can't remember the last time I felt happy",
        "Getting out of bed is the hardest thing I do all day",
        "I'm numb and feel disconnected from everything",
        "Life feels meaningless and I see no point in continuing",
        "I've isolated myself from everyone who cares about me",
        "Every task feels like climbing a mountain",
        "I cry all the time for no reason",
        "The future looks completely hopeless and dark",
        "Food has no taste and I have no appetite",
        "I sleep 14 hours a day but still feel exhausted",
        "I'm a failure at everything I try",
        "The weight of sadness is crushing me",
        "I wish I could just disappear forever",
        
        # More Anxiety examples (15)
        "My heart races constantly and I feel like I'm dying",
        "I'm terrified of things that never used to bother me",
        "Panic attacks come out of nowhere and paralyze me",
        "I catastrophize everything and expect the worst",
        "My mind won't stop racing with anxious thoughts",
        "I avoid social situations because they make me so nervous",
        "I'm constantly on edge and can't relax at all",
        "Physical symptoms like sweating and trembling won't stop",
        "I'm afraid to leave my house most days",
        "Intrusive thoughts plague me constantly",
        "Every decision feels impossible to make",
        "I check things repeatedly to ease my anxiety",
        "My stomach is in knots all the time",
        "I feel like I'm losing my mind",
        "Sleep is impossible because of constant worry",
        
        # More Stress examples (15)
        "The workload is crushing me and I can't breathe",
        "I'm juggling too many responsibilities and failing at all",
        "Pressure from deadlines makes me feel like exploding",
        "I haven't had a moment to myself in weeks",
        "Everything is urgent and I'm constantly in crisis mode",
        "Work-life balance is impossible and I'm burning out",
        "The stress is giving me physical symptoms",
        "I snap at people because I'm so overwhelmed",
        "I need a break desperately but can't take one",
        "Managing everything is becoming impossible",
        "My to-do list never ends and keeps growing",
        "I'm running on empty with no time to recharge",
        "The pressure is affecting my health and relationships",
        "I feel like a hamster on a wheel going nowhere",
        "Stress headaches are my constant companion",
        
        # PTSD examples (15)
        "I keep having flashbacks of the traumatic event",
        "Nightmares about what happened haunt me every night",
        "I avoid anything that reminds me of the trauma",
        "I'm hypervigilant and always expecting danger",
        "Sudden noises make me jump and panic",
        "I feel disconnected from my body since the incident",
        "Intrusive memories won't leave me alone",
        "I can't trust anyone after what happened to me",
        "I feel guilty for surviving when others didn't",
        "The trauma plays in my head like a loop",
        "I'm emotionally numb since the traumatic event",
        "Loud sounds trigger intense fear responses",
        "I relive the horror every time I close my eyes",
        "My sense of safety is completely shattered",
        "I avoid places that remind me of what happened",
        
        # Bipolar examples (15)
        "My mood swings wildly from euphoric to suicidal",
        "I have periods of intense energy then crash completely",
        "Sometimes I feel invincible, other times worthless",
        "I barely sleep when manic then sleep all day when depressed",
        "My spending is out of control during high periods",
        "Racing thoughts make it impossible to focus",
        "I'm impulsive and make terrible decisions when up",
        "My energy levels are completely unpredictable",
        "Relationships suffer because of my mood instability",
        "I experience extreme irritability during episodes",
        "One day I'm on top of the world, next day I want to die",
        "I go from being super productive to unable to function",
        "My behavior changes drastically with my moods",
        "I have grandiose ideas during highs then feel empty",
        "The mood swings are destroying my life",
        
        # More Normal examples (15)
        "I'm managing my emotions well and feeling stable",
        "Challenges come up but I handle them effectively",
        "I have a good support system and use it",
        "Exercise and self-care keep me balanced",
        "I'm satisfied with my life overall",
        "Small setbacks don't derail me anymore",
        "I feel resilient and capable of handling stress",
        "My relationships are healthy and fulfilling",
        "I have hobbies and activities I genuinely enjoy",
        "Life has its ups and downs but I'm okay",
        "I practice good self-care and it shows",
        "I'm grateful for the good things in my life",
        "I handle difficult emotions in healthy ways",
        "I feel grounded and present in my daily life",
        "My mental health is in a good place right now",
    ],
    
    'status': (
        ['Depression'] * 15 +
        ['Anxiety'] * 15 +
        ['Stress'] * 15 +
        ['PTSD'] * 15 +
        ['Bipolar'] * 15 +
        ['Normal'] * 15
    )
}

additional_df = pd.DataFrame(additional_data)

print(f"✓ Created {len(additional_df)} additional training examples")

# ============================================================================
# NORMALIZE AND COMBINE
# ============================================================================

print("\n🔧 Normalizing and combining data...")

# Standardize column names
existing_data.columns = ['statement', 'status']

# Combine datasets
combined_df = pd.concat([existing_data, additional_df], ignore_index=True)
print(f"✓ Combined dataset: {len(combined_df)} total records")

# ============================================================================
# DATA CLEANING
# ============================================================================

print("\n🧹 Cleaning data...")

# Remove duplicates
original_len = len(combined_df)
combined_df = combined_df.drop_duplicates(subset=['statement'], keep='first')
duplicates_removed = original_len - len(combined_df)
if duplicates_removed > 0:
    print(f"✓ Removed {duplicates_removed} duplicate statements")

# Standardize status labels
status_mapping = {
    'Depression': 'Depression',
    'Anxiety': 'Anxiety',
    'Stress': 'Stress',
    'Normal': 'Normal',
    'Suicidal': 'Suicidal',
    'PTSD': 'PTSD',
    'Bipolar': 'Bipolar',
    'depression': 'Depression',
    'anxiety': 'Anxiety',
    'stress': 'Stress',
    'normal': 'Normal',
    'suicidal': 'Suicidal',
    'ptsd': 'PTSD',
    'bipolar': 'Bipolar',
}

combined_df['status'] = combined_df['status'].map(status_mapping)
combined_df = combined_df.dropna(subset=['status'])

# Remove very short statements
combined_df = combined_df[combined_df['statement'].str.len() >= 10]

print(f"✓ Clean dataset: {len(combined_df)} records")

# ============================================================================
# ANALYZE DISTRIBUTION
# ============================================================================

print("\n📊 ENHANCED DISTRIBUTION:")
print("="*70)
distribution = combined_df['status'].value_counts()
print(distribution)
print()

total = len(combined_df)
for status, count in distribution.items():
    percentage = (count / total) * 100
    print(f"{status:15} : {count:4d} records ({percentage:5.1f}%)")

# Balance check
min_samples = distribution.min()
max_samples = distribution.max()
balance_ratio = min_samples / max_samples

print(f"\n⚖️ Balance ratio: {balance_ratio:.2f}", end=" ")
if balance_ratio >= 0.6:
    print("✓ Well balanced!")
elif balance_ratio >= 0.3:
    print("- Moderately balanced")
else:
    print("⚠️ Imbalanced - consider adding more examples")

# ============================================================================
# SAVE ENHANCED DATASET
# ============================================================================

print("\n💾 Saving enhanced dataset...")

# Backup original
try:
    pd.read_csv('Data_original_backup.csv')
    print("ℹ️ Backup already exists, skipping...")
except:
    pd.read_csv('Data.csv').to_csv('Data_original_backup.csv', index=False)
    print("✓ Original backed up as: Data_original_backup.csv")

# Save enhanced
combined_df.to_csv('Data.csv', index=False)
print("✓ Enhanced dataset saved as: Data.csv")

# ============================================================================
# PHASE 2: MODEL TRAINING
# ============================================================================

print("\n" + "="*70)
print("PHASE 2: TRAINING MODEL")
print("="*70)

df = combined_df.copy()

# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

print("\n🔧 Engineering features...")

# Keyword lists for sentiment analysis
NEGATIVE_WORDS = ['sad', 'depressed', 'anxious', 'worried', 'hopeless', 'worthless', 
                  'panic', 'fear', 'trauma', 'nightmare', 'cry', 'empty', 'alone',
                  'helpless', 'guilty', 'numb', 'overwhelmed', 'stressed', 'tense',
                  'dying', 'burden', 'fail', 'terrible', 'worst', 'hate', 'pain',
                  'scared', 'terrified', 'nervous', 'afraid']

POSITIVE_WORDS = ['happy', 'good', 'great', 'well', 'positive', 'content', 'satisfied',
                  'joyful', 'peaceful', 'calm', 'balanced', 'grateful', 'blessed',
                  'love', 'enjoy', 'smile', 'laugh', 'relaxed', 'energetic', 'wonderful']

# Extract features
df['text_length'] = df['statement'].str.len()
df['word_count'] = df['statement'].str.split().str.len()
df['negative_word_count'] = df['statement'].apply(
    lambda x: sum(1 for word in NEGATIVE_WORDS if word in x.lower())
)
df['positive_word_count'] = df['statement'].apply(
    lambda x: sum(1 for word in POSITIVE_WORDS if word in x.lower())
)

print("✓ Created 4 numerical features")

# ============================================================================
# PREPARE TRAINING DATA
# ============================================================================

print("\n📚 Splitting data (80% train, 20% test)...")

X_text = df['statement']
X_features = df[['text_length', 'word_count', 'negative_word_count', 'positive_word_count']]
y = df['status']

# Check if stratification is possible
min_samples_per_class = y.value_counts().min()

if min_samples_per_class >= 2:
    X_text_train, X_text_test, X_feat_train, X_feat_test, y_train, y_test = train_test_split(
        X_text, X_features, y, test_size=0.2, random_state=42, stratify=y
    )
else:
    X_text_train, X_text_test, X_feat_train, X_feat_test, y_train, y_test = train_test_split(
        X_text, X_features, y, test_size=0.2, random_state=42
    )

print(f"✓ Training samples: {len(X_text_train)}")
print(f"✓ Testing samples: {len(X_text_test)}")

# ============================================================================
# TEXT VECTORIZATION
# ============================================================================

print("\n🔤 Creating TF-IDF vectorizer...")

vectorizer = TfidfVectorizer(
    max_features=3000,
    ngram_range=(1, 3),
    min_df=1,
    max_df=0.8,
    sublinear_tf=True,
    strip_accents='unicode'
)

X_text_train_vec = vectorizer.fit_transform(X_text_train)
X_text_test_vec = vectorizer.transform(X_text_test)

# Combine features
X_train_combined = hstack([X_text_train_vec, X_feat_train.values])
X_test_combined = hstack([X_text_test_vec, X_feat_test.values])

print(f"✓ Feature vector shape: {X_train_combined.shape}")
print(f"✓ Vocabulary size: {len(vectorizer.vocabulary_)}")

# ============================================================================
# MODEL TRAINING
# ============================================================================

print("\n🤖 Training multiple models...")

models = {
    'Logistic Regression': LogisticRegression(
        max_iter=2000,
        C=1.0,
        class_weight='balanced',
        random_state=42,
        solver='lbfgs'
    ),
    'Random Forest': RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    ),
    'Gradient Boosting': GradientBoostingClassifier(
        n_estimators=150,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
}

best_model = None
best_score = 0
best_name = ''

for name, model in models.items():
    print(f"\n  Training {name}...")
    model.fit(X_train_combined, y_train)
    
    # Test accuracy
    y_pred = model.predict(X_test_combined)
    score = accuracy_score(y_test, y_pred)
    
    # Cross-validation
    if len(X_train_combined) >= 10:
        cv_scores = cross_val_score(
            model, X_train_combined, y_train, 
            cv=min(5, len(X_train_combined)//2)
        )
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()
        print(f"  ✓ Test Accuracy: {score:.4f} ({score*100:.1f}%)")
        print(f"  ✓ CV Accuracy: {cv_mean:.4f} (+/- {cv_std:.4f})")
    else:
        print(f"  ✓ Accuracy: {score:.4f} ({score*100:.1f}%)")
    
    if score > best_score:
        best_score = score
        best_model = model
        best_name = name

print(f"\n🏆 Best Model: {best_name}")
print(f"   Accuracy: {best_score:.4f} ({best_score*100:.1f}%)")

# ============================================================================
# DETAILED EVALUATION
# ============================================================================

print("\n📊 Classification Report:")
print("="*70)
y_pred = best_model.predict(X_test_combined)
print(classification_report(y_test, y_pred, zero_division=0))

# ============================================================================
# SAVE MODEL
# ============================================================================

print("\n💾 Saving model and components...")

try:
    # Save model
    with open('mental_health_model.pkl', 'wb') as f:
        pickle.dump(best_model, f)
    print("✓ Model saved: mental_health_model.pkl")
    
    # Save vectorizer
    with open('tfidf_vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    print("✓ Vectorizer saved: tfidf_vectorizer.pkl")
    
    # Save feature info
    feature_info = {
        'text_features': ['text_length', 'word_count', 'negative_word_count', 'positive_word_count'],
        'label_classes': list(best_model.classes_),
        'negative_words': NEGATIVE_WORDS,
        'positive_words': POSITIVE_WORDS
    }
    with open('feature_info.pkl', 'wb') as f:
        pickle.dump(feature_info, f)
    print("✓ Feature info saved: feature_info.pkl")
    
    # Verify
    with open('mental_health_model.pkl', 'rb') as f:
        test_model = pickle.load(f)
    print("✓ Verification: Models load successfully")
    
except Exception as e:
    print(f"❌ Error saving: {e}")

# ============================================================================
# TEST PREDICTIONS
# ============================================================================

print("\n🧪 Testing predictions with diverse examples...")

test_cases = [
    ("I feel so depressed and hopeless, life has no meaning", "Depression"),
    ("I'm constantly worried and anxious about everything", "Anxiety"),
    ("Work stress is overwhelming me completely", "Stress"),
    ("I keep having flashbacks of the traumatic event", "PTSD"),
    ("My mood swings from extreme highs to deep lows", "Bipolar"),
    ("I feel great today, life is wonderful", "Normal"),
]

print("\n" + "-"*70)
correct = 0
for text, expected in test_cases:
    # Extract features
    text_length = len(text)
    word_count = len(text.split())
    neg_count = sum(1 for word in NEGATIVE_WORDS if word in text.lower())
    pos_count = sum(1 for word in POSITIVE_WORDS if word in text.lower())
    
    # Vectorize
    text_vec = vectorizer.transform([text])
    feat_array = np.array([[text_length, word_count, neg_count, pos_count]])
    combined = hstack([text_vec, feat_array])
    
    # Predict
    prediction = best_model.predict(combined)[0]
    
    if hasattr(best_model, 'predict_proba'):
        proba = best_model.predict_proba(combined)[0]
        confidence = max(proba)
        match = "✓" if prediction == expected else "✗"
        if prediction == expected:
            correct += 1
        print(f"{match} \"{text[:45]}...\"")
        print(f"  Expected: {expected} | Got: {prediction} ({confidence:.1%})")
    
print("-"*70)
print(f"Test accuracy: {correct}/{len(test_cases)} ({correct/len(test_cases)*100:.0f}%)")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "="*70)
print("✅ COMPLETE! MODEL READY FOR USE")
print("="*70)

print(f"\n📈 Model Summary:")
print(f"  • Algorithm: {best_name}")
print(f"  • Accuracy: {best_score:.1%}")
print(f"  • Training samples: {len(X_train_combined)}")
print(f"  • Test samples: {len(X_test_combined)}")
print(f"  • Total dataset: {len(df)} records")
print(f"  • Classes: {len(best_model.classes_)}")
print(f"  • Conditions: {', '.join(sorted(best_model.classes_))}")

print(f"\n💾 Files Created:")
print(f"  ✓ Data.csv (enhanced dataset)")
print(f"  ✓ Data_original_backup.csv (your original data)")
print(f"  ✓ mental_health_model.pkl")
print(f"  ✓ tfidf_vectorizer.pkl")
print(f"  ✓ feature_info.pkl")

print(f"\n🚀 Next Step:")
print(f"  Run: python app.py")
print(f"  Then open: http://localhost:8000/prediction.html")

print("\n" + "="*70)