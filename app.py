from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os
import json

app = Flask(__name__)
CORS(app)

# -----------------------------------
# Groq Client
# -----------------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# -----------------------------------
# Memory Storage
# -----------------------------------
chat_memory = []

# -----------------------------------
# Load Course Data
# -----------------------------------
course_data = {
    "courses": [
        {
            "name": "AI Foundations Bootcamp",
            "fee": "₹4,999",
            "duration": "6 Weeks",
            "timings": "Mon-Fri 7 PM to 8 PM",
            "syllabus": "Python, AI Basics, Prompt Engineering, Real Projects"
        },
        {
            "name": "Data Science Career Program",
            "fee": "₹9,999",
            "duration": "3 Months",
            "timings": "Weekend Batches",
            "syllabus": "Python, SQL, Power BI, Machine Learning"
        },
        {
            "name": "Automation with Python",
            "fee": "₹5,999",
            "duration": "2 Months",
            "timings": "Sat-Sun Evening",
            "syllabus": "Python Automation, Selenium, Excel Automation"
        }
    ]
}

# -----------------------------------
# Home Route
# -----------------------------------
@app.route("/")
def home():
    return "CourseBot Groq Backend Running"

# -----------------------------------
# Chat Route
# -----------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Please type your question."})

        # Save User Message
        chat_memory.append({"role": "user", "content": user_message})

        # Keep only last 6 chats
        if len(chat_memory) > 6:
            chat_memory.pop(0)

        system_prompt = f"""
You are CourseBot, a smart admission assistant.

Use this course data:

{json.dumps(course_data, indent=2)}

Rules:
- Answer short and professional.
- If user asks fee, timings, syllabus, eligibility etc answer from course data.
- If user says hi/hello greet politely.
- Remember previous messages.
- If not found, say kindly contact admissions team.
"""

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(chat_memory)

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )

        reply = completion.choices[0].message.content

        # Save Bot Reply
        chat_memory.append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})

    except Exception as e:
        print(str(e))
        return jsonify({"reply": "Server error. Please try again later."}), 500

# -----------------------------------
# Clear Memory Route
# -----------------------------------
@app.route("/clear", methods=["POST"])
def clear_chat():
    global chat_memory
    chat_memory = []
    return jsonify({"message": "Memory cleared"})

# -----------------------------------
# Run App
# -----------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)