import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from groq import Groq


BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "course_data.json"

load_dotenv(BASE_DIR / ".env")

app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")
CORS(app)

chat_memory = {}


def load_course_data():
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def build_system_prompt():
    course_data = load_course_data()
    catalog = json.dumps(course_data, indent=2, ensure_ascii=True)

    return f"""
You are CourseBot, a friendly admissions assistant for a training institute.

Use only this course catalog and contact data:
{catalog}

Rules:
- Answer greetings politely and invite the user to ask about courses.
- Answer fees, duration, syllabus, eligibility, timings, mode, certification, and contact questions from the catalog.
- Use the previous messages to understand follow-up questions like "what about syllabus?" or "and timings?".
- If the answer is not available in the catalog, say so clearly and suggest contacting admissions.
- Keep replies concise, helpful, and easy to read.
- Do not invent courses, discounts, deadlines, or admission promises.
- Use clean Markdown for structured answers.
- For multiple courses, use this format:
  "Here are the details:"
  "- **Course name**: detail"
- For one course, use this format when relevant:
  "**Course name**"
  "- Fee: ..."
  "- Duration: ..."
  "- Timings: ..."
  "- Mode: ..."
  "- Certification: ..."
- Do not use long paragraphs when a list is clearer.
""".strip()


def get_session_messages(session_id):
    if session_id not in chat_memory:
        chat_memory[session_id] = []
    return chat_memory[session_id]


@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/health")
def health():
    return jsonify({"ok": True, "service": "CourseBot API"})


@app.route("/courses")
def courses():
    course_data = load_course_data()
    names = [course["name"] for course in course_data["courses"]]
    return jsonify({"count": len(names), "courses": names})


@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    user_message = (payload.get("message") or "").strip()
    session_id = (payload.get("session_id") or "default").strip()

    if not user_message:
        return jsonify({"reply": "Please type your question so I can help."}), 400

    client = get_groq_client()
    if client is None:
        return (
            jsonify(
                {
                    "reply": (
                        "GROQ_API_KEY is missing. Add it in your backend environment or local .env file."
                    )
                }
            ),
            500,
        )

    session_messages = get_session_messages(session_id)
    session_messages.append({"role": "user", "content": user_message})
    chat_memory[session_id] = session_messages[-10:]

    messages = [{"role": "system", "content": build_system_prompt()}]
    messages.extend(chat_memory[session_id])

    try:
        completion = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            messages=messages,
            temperature=0.45,
            max_tokens=450,
        )
    except Exception as exc:
        return jsonify({"reply": f"API request failed: {exc}"}), 502

    reply = completion.choices[0].message.content.strip()
    chat_memory[session_id].append({"role": "assistant", "content": reply})
    chat_memory[session_id] = chat_memory[session_id][-10:]

    return jsonify({"reply": reply})


@app.route("/clear", methods=["POST"])
def clear_chat():
    payload = request.get_json(silent=True) or {}
    session_id = (payload.get("session_id") or "default").strip()
    chat_memory.pop(session_id, None)
    return jsonify({"message": "Memory cleared"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG") == "1")
