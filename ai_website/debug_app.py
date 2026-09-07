from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import traceback

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

print("=" * 60)
print("DEBUG MODE: Simple Mental Health Sentiment Analysis")
print("=" * 60)
print("Server starting...")

# Simple mock response for testing
@app.route("/predict", methods=["POST"])
def predict():
    print("\n" + "=" * 40)
    print("📥 Received prediction request")
    
    try:
        # Get raw request data
        raw_data = request.get_data(as_text=True)
        print(f"Raw request data: {raw_data[:200]}...")
        
        # Try to parse JSON
        try:
            data = request.get_json()
            print(f"Parsed JSON data: {data}")
        except:
            data = {"error": "Invalid JSON"}
            print("❌ Could not parse JSON")
        
        text = data.get("text", "").strip()
        print(f"Text to analyze: '{text}'")
        
        if not text:
            response = {"error": "No text provided"}
            print("❌ No text provided")
        else:
            # Simple mock prediction
            response = {
                "prediction": "Anxiety",  # Mock response
                "confidence": 0.85,
                "probabilities": {
                    "Normal": 0.1,
                    "Depression": 0.05,
                    "Anxiety": 0.85,
                    "Stress": 0.0
                },
                "all_predictions": [
                    {"label": "Normal", "probability": 0.1},
                    {"label": "Depression", "probability": 0.05},
                    {"label": "Anxiety", "probability": 0.85},
                    {"label": "Stress", "probability": 0.0}
                ],
                "recommendations": [
                    "This is a TEST response",
                    "Practice deep breathing exercises",
                    "Try mindfulness meditation for 10 minutes"
                ],
                "debug": {
                    "text_received": text,
                    "text_length": len(text),
                    "server_status": "working"
                }
            }
            print("✅ Mock prediction generated")
        
        print(f"Response being sent: {response}")
        print("=" * 40 + "\n")
        
        return jsonify(response)
        
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        print(f"❌ ERROR: {error_msg}")
        print(f"Traceback: {error_trace}")
        
        return jsonify({
            "error": f"Server error: {error_msg}",
            "traceback": error_trace
        }), 500

@app.route("/health", methods=["GET"])
def health_check():
    print("✅ Health check received")
    return jsonify({
        "status": "healthy",
        "service": "Mental Health Sentiment Debug",
        "mode": "debug",
        "message": "Server is running"
    })

@app.route('/')
def serve_index():
    return send_from_directory('.', 'explore-more.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🌐 SERVER STARTED SUCCESSFULLY!")
    print("=" * 60)
    print("\n📋 Access Information:")
    print("   Web Interface: http://localhost:5000")
    print("   Health Check:  http://localhost:5000/health")
    print("   API Endpoint:  http://localhost:5000/predict")
    print("\n📝 Sample test data to try:")
    print('   {"text": "I feel anxious about my presentation tomorrow"}')
    print('   {"text": "Everything feels hopeless lately"}')
    print('   {"text": "I had a great day with friends today"}')
    print("\n⚠️  Debug Mode: Using mock responses only")
    print("=" * 60 + "\n")
    
    app.run(debug=True, port=5000)