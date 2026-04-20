import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# --------------------
# Flask Setup
# --------------------
app = Flask(__name__, static_folder=".")
CORS(app)

# --------------------
# Gemini API Key
# --------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

# --------------------
# Load Course Data
# --------------------
def load_course_data():
    try:
        with open("data/course_data.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return {}

course_data = load_course_data()

# --------------------
# Home Route
# --------------------
@app.route("/")
def home():
    return send_from_directory(".", "index.html")

# --------------------
# Health Check
# --------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# --------------------
# Chat Route
# --------------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        prompt = f"""
You are CourseBot.

Use this data:
{json.dumps(course_data)}

Question: {user_message}

Give short answer.
"""

        response = model.generate_content(prompt)

        return jsonify({
            "reply": response.text
        })

    except Exception as e:
        print("CHAT ERROR:", str(e))
        return jsonify({
            "reply": str(e)
        }), 500

# --------------------
# Run App
# --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)