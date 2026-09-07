from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import traceback
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Global variables
model = None
vectorizer = None
label_map = {"Normal": 0, "Depression": 1, "Anxiety": 2, "Stress": 3}
reverse_label_map = {0: "Normal", 1: "Depression", 2: "Anxiety", 3: "Stress"}

# ============================================================
# NEW: Prompt Suggestion System
# ============================================================
prompt_model = None
prompt_embeddings = None
prompt_list = None


# Stress-specific keywords for better detection
STRESS_KEYWORDS = [
    'overwhelmed', 'pressure', 'deadline', 'busy', 'workload', 'exhausted',
    'burnout', 'too much', 'cant cope', 'handle', 'responsibilities',
    'demanding', 'hectic', 'rush', 'overworked', 'stretched', 'burden',
    'stressed', 'stressful', 'tense', 'tension', 'pressured', 'swamped',
    'overloaded', 'juggling', 'multitask', 'time pressure', 'behind schedule',
    'cant keep up', 'falling behind', 'drowning', 'suffocating'
]

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
gemini_model = None
if api_key:
    print(f"✓ Gemini API key loaded")
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel('gemini-2.5-flash')
else:
    print("⚠️ Gemini API key not found - using ML model only")


def load_and_train_model():
    """Load CSV data and train the model"""
    global model, vectorizer
    
    try:
        # Load dataset
        df = pd.read_csv("Data.csv")
        print(f"✓ Loaded {len(df)} records from Data.csv")
        
        # Clean the data
        # Remove rows where 'status' column contains 'status' (header in data)
        df = df[df['status'] != 'status']
        
        # Remove rows with missing values
        df = df.dropna(subset=['statement', 'status'])
        
        # Remove empty strings
        df = df[(df['statement'].str.strip() != '') & (df['status'].str.strip() != '')]
        
        # Standardize status labels (handle case variations)
        df['status'] = df['status'].str.strip().str.title()
        
        print(f"✓ After cleaning: {len(df)} valid records")
        print(f"✓ Classes: {df['status'].value_counts().to_dict()}")
        
        # Check class distribution
        class_counts = df['status'].value_counts()
        if 'Stress' in class_counts:
            print(f"  → Stress samples: {class_counts['Stress']}")
        else:
            print("  ⚠️ WARNING: No 'Stress' samples found in dataset!")
        
        # Verify all status values are valid
        valid_statuses = set(label_map.keys())
        invalid_statuses = set(df['status'].unique()) - valid_statuses
        if invalid_statuses:
            print(f"  ⚠️ WARNING: Found invalid status values: {invalid_statuses}")
            print(f"     Valid values are: {valid_statuses}")
            # Filter out invalid statuses
            df = df[df['status'].isin(valid_statuses)]
            print(f"  ✓ Filtered to {len(df)} records with valid statuses")
        
        if len(df) < 20:
            raise ValueError(f"Not enough training data after cleaning. Only {len(df)} records found.")
        
        # Prepare data
        X = df['statement'].values
        y = df['status'].map(label_map).values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Enhanced vectorization focusing on stress-related terms
        vectorizer = TfidfVectorizer(
            max_features=2500, 
            stop_words='english',
            ngram_range=(1, 3),  # Include trigrams for better context
            min_df=1,  # Lower min_df to capture rare stress terms
            max_df=0.85,
            sublinear_tf=True  # Use sublinear term frequency scaling
        )
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)
        
        # Train model with adjusted parameters
        model = MultinomialNB(alpha=0.05)  # Lower alpha for better stress detection
        model.fit(X_train_vec, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"✓ Model trained with accuracy: {accuracy:.2%}")
        
        # Print per-class performance
        print("\n📊 Per-class Performance:")
        print(classification_report(y_test, y_pred, target_names=list(reverse_label_map.values())))
        
        return True
    except FileNotFoundError:
        print("❌ Error: Data.csv not found!")
        return False
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        traceback.print_exc()
        return False


def calculate_stress_score(text):
    """Calculate stress indicators from text"""
    text_lower = text.lower()
    
    # Count stress keywords
    stress_count = sum(1 for keyword in STRESS_KEYWORDS if keyword in text_lower)
    
    # Check for stress-specific patterns
    patterns = [
        r'too much',
        r'cant (cope|handle|manage)',
        r'overwhelmed (by|with)',
        r'under pressure',
        r'stressed out',
        r'burning out',
        r'no time',
        r'running out of time',
        r'behind on',
        r'juggling'
    ]
    
    pattern_matches = sum(1 for pattern in patterns if re.search(pattern, text_lower))
    
    # Combine scores
    total_score = stress_count + (pattern_matches * 2)  # Weight pattern matches higher
    
    return total_score


def get_gemini_prediction(text):
    """Get enhanced prediction from Gemini with stress-focused prompting"""
    if not gemini_model:
        return None
    
    try:
        prompt = f"""You are a mental health analysis assistant. Analyze the following statement and classify it into ONE of these categories: Normal, Depression, Anxiety, or Stress.

IMPORTANT: Pay special attention to STRESS indicators:
- Feeling overwhelmed by responsibilities or tasks
- Time pressure, deadlines, busy schedules
- Work overload, too many demands
- Difficulty coping with multiple challenges
- Feeling stretched thin or burned out
- Physical exhaustion combined with mental pressure

Category Definitions:
- **Depression**: Persistent sadness, hopelessness, loss of interest, feeling worthless, low energy with emotional numbness
- **Anxiety**: Excessive worry about future events, fear, panic, nervousness, constant anticipation of problems
- **Stress**: Feeling overwhelmed by current demands, pressure from responsibilities, too much to handle RIGHT NOW, exhaustion from overwork
- **Normal**: Balanced emotions, manageable challenges, positive or neutral outlook

Key Distinction:
- Anxiety = worry about FUTURE possibilities ("what if?")
- Stress = overwhelmed by CURRENT demands ("too much right now")
- Depression = persistent emotional pain and hopelessness

Statement: "{text}"

Respond ONLY with a valid JSON object (no markdown, no extra text):
{{
  "category": "Normal|Depression|Anxiety|Stress",
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation focusing on specific indicators present",
  "recommendation": "Specific helpful recommendation"
}}"""

        response = gemini_model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean response - remove markdown code blocks
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        response_text = response_text.strip()
        
        # Parse JSON
        result = json.loads(response_text)
        
        # Validate category
        if result.get("category") not in ["Normal", "Depression", "Anxiety", "Stress"]:
            print(f"Invalid category from Gemini: {result.get('category')}")
            return None
            
        return result
    except json.JSONDecodeError as e:
        print(f"Gemini JSON parse error: {e}")
        print(f"Response was: {response_text[:200]}")
        return None
    except Exception as e:
        print(f"Gemini error: {e}")
        traceback.print_exc()
        return None


def provide_recommendation(category, confidence):
    """Provide detailed recommendations based on mental health category"""
    recommendations = {
        "Normal": {
            "message": "You appear to be in a balanced mental state. Keep up the good work!",
            "tips": [
                "Continue practicing healthy routines and self-care",
                "Maintain social connections with friends and family",
                "Keep engaging in activities you enjoy",
                "Practice mindfulness or meditation regularly",
                "Ensure adequate sleep (7-9 hours per night)"
            ]
        },
        "Depression": {
            "message": "You may be experiencing symptoms of depression. It's important to reach out for support.",
            "tips": [
                "Talk to someone you trust about how you're feeling",
                "Consider reaching out to a mental health professional or therapist",
                "Try to maintain a routine even when it feels difficult",
                "Engage in gentle physical activity like walking or stretching",
                "Avoid isolating yourself - stay connected with supportive people",
                "Practice self-compassion and avoid self-criticism"
            ]
        },
        "Anxiety": {
            "message": "You may be experiencing anxiety. There are effective strategies to help manage these feelings.",
            "tips": [
                "Practice deep breathing exercises (try the 4-7-8 technique: inhale 4s, hold 7s, exhale 8s)",
                "Try progressive muscle relaxation to release physical tension",
                "Challenge anxious thoughts by examining evidence for and against them",
                "Limit caffeine and alcohol intake as they can worsen anxiety",
                "Ground yourself using the 5-4-3-2-1 technique (5 things you see, 4 you can touch, etc.)",
                "Consider speaking with a therapist about cognitive-behavioral techniques"
            ]
        },
        "Stress": {
            "message": "You're showing signs of stress and feeling overwhelmed. Managing your load is important.",
            "tips": [
                "Prioritize tasks - identify what truly needs immediate attention",
                "Break large tasks into smaller, manageable steps",
                "Learn to say 'no' to non-essential commitments",
                "Take regular short breaks throughout your day (even 5 minutes helps)",
                "Practice time management techniques like the Pomodoro method",
                "Delegate tasks when possible and ask for help",
                "Engage in stress-relief activities: exercise, deep breathing, or a hobby you enjoy",
                "Ensure you're getting adequate sleep - being overtired worsens stress",
                "Talk to someone about your workload or consider professional stress management counseling"
            ]
        }
    }
    
    rec = recommendations.get(category, recommendations["Normal"])
    
    return {
        "message": rec["message"],
        "tips": rec["tips"],
        "urgency": "high" if category in ["Depression", "Anxiety"] and confidence > 0.7 else "medium"
    }


# ============================================================
# NEW: Load Prompt Suggestion Model
# ============================================================
def load_prompt_model():
    """Load the prompt suggestion model"""
    global prompt_model, prompt_embeddings, prompt_list

    try:
        from sentence_transformers import SentenceTransformer
        from prompts import prompts

        print("🔄 Loading prompt suggestion model...")

        prompt_list = prompts

        prompt_model = SentenceTransformer("all-mpnet-base-v2")

        embeddings_file = "prompts_embeddings.npy"

        if os.path.exists(embeddings_file):
            try:
                prompt_embeddings = np.load(embeddings_file)

                # Make sure saved embeddings match current prompts
                if len(prompt_embeddings) != len(prompt_list):
                    print("⚠️ Prompt embeddings do not match prompts. Rebuilding...")
                    prompt_embeddings = prompt_model.encode(
                        prompt_list,
                        convert_to_numpy=True,
                        show_progress_bar=False
                    )
                    np.save(embeddings_file, prompt_embeddings)
            except Exception:
                print("⚠️ Could not load saved prompt embeddings. Rebuilding...")
                prompt_embeddings = prompt_model.encode(
                    prompt_list,
                    convert_to_numpy=True,
                    show_progress_bar=False
                )
                np.save(embeddings_file, prompt_embeddings)
        else:
            prompt_embeddings = prompt_model.encode(
                prompt_list,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            np.save(embeddings_file, prompt_embeddings)

        print("✓ Prompt suggestion model ready")
        return True

    except Exception as e:
        print(f"❌ Error loading prompt suggestion model: {e}")
        traceback.print_exc()
        return False


# ============================================================
# NEW: AI Chat API
# ============================================================
@app.route("/api/chat", methods=["POST"])
def api_chat():
    """AI Chat endpoint"""
    try:
        data = request.get_json(silent=True) or {}
        message = data.get("message", "").strip()

        if not message:
            return jsonify({"error": "No message provided"}), 400

        if not gemini_model:
            return jsonify({
                "error": "Gemini AI is not available. Please check your GEMINI_API_KEY."
            }), 503

        print(f"\n💬 AI Chat: {message[:100]}...")

        response = gemini_model.generate_content(message)

        response_text = response.text.strip()

        if not response_text:
            return jsonify({
                "error": "AI returned an empty response."
            }), 500

        return jsonify({
            "response": response_text
        })

    except Exception as e:
        print(f"❌ AI Chat Error: {e}")
        traceback.print_exc()

        return jsonify({
            "error": "AI Chat failed",
            "details": str(e)
        }), 500


# ============================================================
# NEW: Prompt Generation API
# ============================================================
@app.route("/api/suggest-prompt", methods=["POST"])
def suggest_prompt():
    """Generate useful prompts based on the user's message"""
    try:
        data = request.get_json(silent=True) or {}
        user_message = data.get("userMessage", "").strip()

        if not user_message:
            return jsonify({"error": "No user message provided"}), 400

        global prompt_model, prompt_embeddings, prompt_list

        # Load the prompt model only when this feature is used
        if prompt_model is None or prompt_embeddings is None or prompt_list is None:
            if not load_prompt_model():
                return jsonify({
                    "error": "Prompt suggestion model could not be loaded."
                }), 500

        from sklearn.metrics.pairwise import cosine_similarity

        # Convert user message into an embedding
        query_embedding = prompt_model.encode(
            [user_message],
            convert_to_numpy=True,
            show_progress_bar=False
        )

        # Calculate similarity
        similarities = cosine_similarity(
            query_embedding,
            prompt_embeddings
        )[0]

        # Get top 5 suggestions
        top_k = min(5, len(prompt_list))
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        suggestions = []

        for index in top_indices:
            suggestions.append({
                "prompt": prompt_list[index],
                "score": round(float(similarities[index]), 4)
            })

        print(f"💡 Generated {len(suggestions)} prompt suggestions")

        return jsonify({
            "prompts": [item["prompt"] for item in suggestions],
            "suggestions": suggestions
        })

    except Exception as e:
        print(f"❌ Prompt suggestion error: {e}")
        traceback.print_exc()

        return jsonify({
            "error": "Prompt generation failed",
            "details": str(e)
        }), 500


@app.route("/predict", methods=["POST"])
def predict():
    if model is None or vectorizer is None:
        return jsonify({"error": "Model not loaded. Please check Data.csv exists."}), 500
    
    try:
        data = request.get_json()
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"error": "No text provided"}), 400

        print(f"\n📝 Analyzing: {text[:100]}...")

        # Calculate stress score
        stress_score = calculate_stress_score(text)
        print(f"🔍 Stress indicator score: {stress_score}")

        # ML Model Prediction
        text_vector = vectorizer.transform([text])
        prediction_num = model.predict(text_vector)[0]
        probabilities = model.predict_proba(text_vector)[0]
        ml_confidence = float(max(probabilities))
        ml_prediction = reverse_label_map[prediction_num]

        print(f"🤖 ML Prediction: {ml_prediction} (confidence: {ml_confidence:.2f})")
        print(f"   Probabilities: {dict(zip(reverse_label_map.values(), probabilities))}")

        # Get Gemini prediction (if available)
        gemini_result = None
        final_prediction = ml_prediction
        final_confidence = ml_confidence
        
        if gemini_model:
            gemini_result = get_gemini_prediction(text)
            
            if gemini_result:
                print(f"🧠 Gemini Prediction: {gemini_result['category']} (confidence: {gemini_result.get('confidence', 0):.2f})")
                
                # Enhanced logic for stress detection
                gemini_pred = gemini_result['category']
                gemini_conf = gemini_result.get('confidence', 0)
                
                # If high stress score detected, favor stress prediction
                if stress_score >= 3:
                    print(f"⚠️ High stress score detected ({stress_score}) - favoring stress prediction")
                    if gemini_pred == "Stress" or ml_prediction == "Stress":
                        final_prediction = "Stress"
                        final_confidence = max(ml_confidence, gemini_conf, 0.75)
                
                # If both models agree
                elif gemini_pred == ml_prediction:
                    final_confidence = min(0.95, (ml_confidence + gemini_conf) / 2 + 0.1)
                
                # If Gemini predicts stress with high confidence
                elif gemini_pred == "Stress" and gemini_conf > 0.7:
                    final_prediction = "Stress"
                    final_confidence = gemini_conf
                
                # If ML predicts stress with decent confidence
                elif ml_prediction == "Stress" and ml_confidence > 0.5:
                    final_prediction = "Stress"
                    final_confidence = ml_confidence
                
                # Gemini has very high confidence for other categories
                elif gemini_conf > 0.85:
                    final_prediction = gemini_pred
                    final_confidence = gemini_conf
                
                # ML has higher confidence
                elif ml_confidence > gemini_conf:
                    final_prediction = ml_prediction
                    final_confidence = ml_confidence
                
                # Default to Gemini for tie-breaker
                else:
                    final_prediction = gemini_pred
                    final_confidence = gemini_conf
        
        # If no Gemini but high stress score, boost stress confidence
        elif stress_score >= 3 and ml_prediction == "Stress":
            final_confidence = min(0.85, ml_confidence + 0.15)
        
        # Generate recommendation
        recommendation = provide_recommendation(final_prediction, final_confidence)
        
        # Build response
        response = {
            "prediction": final_prediction,
            "confidence": round(final_confidence, 2),
            "recommendation": recommendation["message"],
            "tips": recommendation["tips"],
            "urgency": recommendation["urgency"],
            "analysis": {
                "ml_prediction": ml_prediction,
                "ml_confidence": round(ml_confidence, 2),
                "stress_score": stress_score,
                "all_probabilities": {
                    label: round(prob, 3) 
                    for label, prob in zip(reverse_label_map.values(), probabilities)
                }
            }
        }
        
        if gemini_result:
            response["analysis"]["gemini_prediction"] = gemini_result["category"]
            response["analysis"]["gemini_confidence"] = round(gemini_result.get("confidence", 0), 2)
            response["analysis"]["reasoning"] = gemini_result.get("reasoning", "")
            response["model_used"] = "ML + Gemini Enhanced + Stress Detection"
        else:
            response["model_used"] = "ML Model + Stress Detection"
        
        print(f"✅ Final Prediction: {final_prediction} (confidence: {final_confidence:.2f})")
        
        return jsonify(response)

    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "Prediction failed",
            "details": str(e)
        }), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "vectorizer_loaded": vectorizer is not None,
        "gemini_available": gemini_model is not None,
        "classes": list(reverse_label_map.values()),
        "stress_keywords_count": len(STRESS_KEYWORDS)
    })


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "Mental Health Sentiment Analysis API",
        "version": "2.1 - Enhanced Stress Detection",
        "endpoints": {
            "/predict": "POST - Analyze mental health statement",
            "/health": "GET - Check server health",
            "/api/chat": "POST - AI Chat",
            "/api/suggest-prompt": "POST - Generate prompt suggestions"
        },
        "classes": ["Normal", "Depression", "Anxiety", "Stress"],
        "features": [
            "ML-based text classification",
            "Gemini AI enhancement",
            "Enhanced stress detection with keyword analysis",
            "Detailed recommendations",
            "Confidence scoring",
            "AI Chat",
            "Prompt Generation"
        ]
    })


if __name__ == "__main__":
    print("🚀 Starting Mental Health Analysis API v2.1...")
    print("=" * 50)
    
    # Load and train model
    if load_and_train_model():
        print("=" * 50)
        print("✓ Server ready to accept predictions")
        print(f"✓ Stress detection keywords loaded: {len(STRESS_KEYWORDS)}")
        print("📍 Running on http://localhost:5000")
        print("=" * 50)
        app.run(debug=True, port=5000)
    else:
        print("❌ Failed to start - check Data.csv file")