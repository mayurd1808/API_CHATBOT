import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from openai import OpenAI


BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "course_data.json"


load_dotenv(BASE_DIR / ".env")

app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")
CORS(app)


def load_data():
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_system_instructions(data):
    catalog = json.dumps(data, indent=2, ensure_ascii=True)
    return (
        "You are CourseBot, a helpful admissions chatbot for a training institute.\n"
        "Answer only using the course catalog and contact details provided below.\n"
        "If the user asks a follow-up question like 'what about timings?' or 'tell me the fee', "
        "use the previous conversation context to infer the course when possible.\n"
        "If the user asks for a course or detail that is not in the catalog, say that clearly and "
        "invite them to contact admissions.\n"
        "Keep answers concise, friendly, and practical.\n"
        "When listing syllabus items, format them as short bullet points.\n\n"
        f"Course catalog:\n{catalog}"
    )


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    previous_response_id = payload.get("previous_response_id")

    if not message:
        return jsonify({"error": "Please enter a question."}), 400

    client = get_openai_client()
    if client is None:
        return (
            jsonify(
                {
                    "error": (
                        "OPENAI_API_KEY is missing. Add it to a .env file before starting the server."
                    )
                }
            ),
            500,
        )

    data = load_data()

    try:
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            instructions=build_system_instructions(data),
            input=message,
            previous_response_id=previous_response_id,
            store=True,
        )
    except Exception as exc:
        return jsonify({"error": f"OpenAI request failed: {exc}"}), 502

    return jsonify(
        {
            "reply": response.output_text,
            "response_id": response.id,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
