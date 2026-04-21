import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google import genai

# -----------------------------
# Flask App
# -----------------------------
app = Flask(__name__, static_folder=".")
CORS(app)

# -----------------------------
# Gemini API Key
# -----------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise Exception("GEMINI_API_KEY not found in Render Environment Variables")

client = genai.Client(api_key=GEMINI_API_KEY)

# -----------------------------
# Load Course Data
# -----------------------------
def load_course_data():
    try:
        with open("data/course_data.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}

course_data = load_course_data()

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Please type a question."}), 400

        prompt = f"""
You are CourseBot.

Use this course data:
{json.dumps(course_data)}

Answer only based on available course data.
Keep answers short, clear, and helpful.

Question: {user_message}
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        reply = response.text if response.text else "No response generated."

        return jsonify({"reply": reply})

    except Exception as e:
       return jsonify({"reply":"API quota exceeded. Please try later."}), 500

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)