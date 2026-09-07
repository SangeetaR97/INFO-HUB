from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import fitz  # PyMuPDF
from PIL import Image
from transformers import pipeline

# ------------------ APP SETUP ------------------
app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ------------------ AI MODEL ------------------
# Question Answering model (offline, free)
qa_model = pipeline(
    "question-answering",
    model="deepset/roberta-base-squad2"
)

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    return "INFO HUB Backend is running"

# ---------- PDF QUESTION ANSWER ----------
@app.route("/solve-pdf", methods=["POST"])
def solve_pdf():
    if "pdf" not in request.files:
        return jsonify({"error": "No PDF uploaded"}), 400

    file = request.files["pdf"]
    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)

    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    questions = [
        q.strip() for q in full_text.split("?")
        if len(q.strip()) > 15
    ]

    answers = []
    for q in questions[:10]:  # limit to avoid overload
        try:
            result = qa_model(
                question=q,
                context=full_text[:4000]
            )
            answers.append({
                "question": q + "?",
                "answer": result.get("answer", "Answer not found")
            })
        except:
            continue

    return jsonify(answers)

# ---------- PDF COMPRESS ----------
@app.route("/compress-pdf", methods=["POST"])
def compress_pdf():
    if "pdf" not in request.files:
        return "No PDF uploaded", 400

    file = request.files["pdf"]
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_path = os.path.join(
        UPLOAD_FOLDER, "compressed_" + file.filename
    )

    file.save(input_path)
    doc = fitz.open(input_path)
    doc.save(output_path, garbage=4, deflate=True)

    return send_file(output_path, as_attachment=True)

# ---------- IMAGE COMPRESS ----------
@app.route("/compress-image", methods=["POST"])
def compress_image():
    if "image" not in request.files:
        return "No image uploaded", 400

    file = request.files["image"]
    image = Image.open(file.stream)

    output_path = os.path.join(UPLOAD_FOLDER, "compressed.jpg")
    image.save(output_path, optimize=True, quality=40)

    return send_file(output_path, as_attachment=True)

# ------------------ RUN ------------------
if __name__ == "__main__":
    app.run(debug=True)
