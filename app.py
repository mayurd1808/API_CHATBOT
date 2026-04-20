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
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def build_system_instructions(data):
    return (
        "You are CourseBot, a helpful admissions chatbot. "
        "Answer only using the course data provided."
    )


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None

    return OpenAI(api_key=api_key)


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/health")
def health():
    return jsonify({"ok": True})


@app.route("/chat", methods=["POST"])
@app.route("/api/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}

    message = (payload.get("message") or "").strip()
    previous_response_id = payload.get("previous_response_id")

    if not message:
        return jsonify({"error": "Please enter a question."}), 400

    client = get_openai_client()

    if client is None:
        return jsonify({
            "error": "OPENAI_API_KEY missing in Render variables."
        }), 500

    data = load_data()

    try:
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            instructions=build_system_instructions(data),
            input=message,
            previous_response_id=previous_response_id,
            store=True
        )

        return jsonify({
            "reply": response.output_text,
            "response_id": response.id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)