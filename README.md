# Course Query Chatbot

This project is now a small Flask-based chatbot app that uses the OpenAI API for more flexible, multi-turn course conversations. The API key stays on the backend, and the frontend passes the previous response ID so follow-up questions like "what about timings?" still work.

## Features

- Supports multi-question and follow-up conversation flow
- Keeps the API key on the server through `.env`
- Uses your course catalog from `data/course_data.json` to ground answers
- Includes a browser chat UI with quick question chips
- Returns clear errors if the API key is missing or the API call fails

## Project Structure

```text
.
|-- .env.example
|-- .gitignore
|-- app.py
|-- index.html
|-- requirements.txt
|-- script.js
|-- style.css
|-- data/
|   `-- course_data.json
`-- README.md
```

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file from `.env.example` and add your real API key:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   ```

3. Start the app:

   ```bash
   python app.py
   ```

4. Open this URL in your browser:

   ```text
   http://127.0.0.1:5000
   ```

## Example Conversation

- What is the fee for AI Foundations Bootcamp?
- What about the syllabus?
- And the timings?
- Is it online?
- How can I contact admissions?

## Notes

- The chatbot answers from the course catalog in `data/course_data.json`.
- GitHub Pages can host only the frontend. It cannot run the Flask backend.
- If you want to keep using GitHub Pages for the UI, deploy the Flask backend separately on Render, Railway, Replit, or another Python host.
- Then create a `config.js` file from `config.example.js` and set:

  ```js
  window.CHATBOT_API_URL = "https://your-backend-url.onrender.com";
  ```

- The frontend will call `https://your-backend-url.onrender.com/api/chat`.
- For multi-turn chat, the backend uses the OpenAI Responses API with the previous response ID.
