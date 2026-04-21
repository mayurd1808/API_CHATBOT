import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder=".")
CORS(app)

# --------------------
# Gemini API Key
# --------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise Exception("GEMINI_API_KEY not found in Render Environment Variables")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")
# --------------------
# Load Course Data
# --------------------
def load_course_data():
    try:
        with open("data/course_data.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}

course_data = load_course_data()

# --------------------
# Routes
# --------------------
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

Question: {user_message}

Give short answer.
"""

        response = model.generate_content(prompt)

        # 🔥 SAFE extraction
        reply = ""

        if hasattr(response, "text") and response.text:
            reply = response.text
        elif hasattr(response, "candidates"):
            reply = response.candidates[0].content.parts[0].text
        else:
            reply = "No response from Gemini."

        return jsonify({"reply": reply})

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("FULL ERROR:", str(e))
        return jsonify({"reply": str(e)}), 500

# --------------------
# Run App
# --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)