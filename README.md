# CourseBot AI Chat

CourseBot is a Flask + Groq API chatbot for course admissions questions. The UI is a polished animated web chat, and the backend uses `data/course_data.json` so answers stay grounded in your course catalog.

## Features

- Animated responsive chat interface
- Groq API integration through Flask
- Per-browser-session conversation memory
- Six-course catalog loaded from `data/course_data.json`
- Clear backend/API error messages
- Works locally, or with GitHub Pages frontend plus a deployed backend

## Local Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in this folder:

   ```env
   GROQ_API_KEY=your_real_groq_api_key_here
   GROQ_MODEL=llama-3.1-8b-instant
   ```

3. Start the backend:

   ```bash
   python app.py
   ```

4. Open:

   ```text
   http://127.0.0.1:10000
   ```

## GitHub Pages Setup

GitHub Pages can host only the frontend. It cannot run `app.py`.

If you deploy the Flask backend on Render, Railway, Replit, or another host, create `config.js` from `config.example.js` and set the backend base URL:

```js
window.CHATBOT_API_URL = "https://your-backend-url.onrender.com";
```

Do not add `/chat` at the end. The frontend adds `/chat` automatically.

## Example Questions

- What is the fee for AI Foundations Bootcamp?
- What about its syllabus?
- And the timings?
- Which course is best for beginners?
- Suggest a course for web development.
- Tell me about Cloud Computing Essentials.
- What is Cybersecurity Fundamentals?
- How can I contact admissions?

## Important

Never paste your real API key into GitHub files like `.env.example`, `script.js`, or `index.html`. Put the real key only in `.env` locally or in your backend hosting provider's environment variables.



URL=https://api-chatbot-czop.onrender.com/