const courses = [
  "AI Foundations Bootcamp",
  "Data Science Career Program",
  "Automation with Python"
];

const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");
const clearChatButton = document.getElementById("clear-chat");
const chips = document.querySelectorAll(".chip");
const statusText = document.getElementById("status-text");

const apiBaseUrl = (window.CHATBOT_API_URL || "").replace(/\/$/, "");
const sessionId = getSessionId();
let isSending = false;

function getSessionId() {
  const existing = localStorage.getItem("coursebot_session_id");
  if (existing) {
    return existing;
  }

  const next = crypto.randomUUID ? crypto.randomUUID() : String(Date.now());
  localStorage.setItem("coursebot_session_id", next);
  return next;
}

function appendMessage(content, sender, options = {}) {
  const message = document.createElement("div");
  message.className = `message ${sender}`;

  const avatar = document.createElement("span");
  avatar.className = "message-avatar";
  avatar.textContent = sender === "bot" ? "CB" : "YOU";

  const bubble = document.createElement("p");
  bubble.className = "message-bubble";
  bubble.textContent = content;

  if (options.loading) {
    bubble.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
    message.dataset.loading = "true";
  }

  message.append(avatar, bubble);
  chatMessages.appendChild(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return bubble;
}

function setComposerState(disabled) {
  isSending = disabled;
  userInput.disabled = disabled;
  sendButton.disabled = disabled;
  if (disabled) {
    statusText.textContent = "Thinking...";
  }
}

async function parseApiResponse(response) {
  const contentType = response.headers.get("content-type") || "";

  if (!contentType.includes("application/json")) {
    const text = await response.text();
    if (text.toLowerCase().includes("<html")) {
      throw new Error(
        "Backend not connected. Run Flask locally or set CHATBOT_API_URL in config.js to your deployed backend."
      );
    }
    throw new Error("Backend returned an unexpected response.");
  }

  return response.json();
}

async function requestBotReply(message) {
  const response = await fetch(`${apiBaseUrl}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      message,
      session_id: sessionId
    })
  });

  const payload = await parseApiResponse(response);
  if (!response.ok) {
    throw new Error(payload.reply || payload.error || "The chatbot API could not answer right now.");
  }

  return payload.reply || "I could not generate a response this time.";
}

async function handleSend(rawMessage) {
  const message = rawMessage.trim();
  if (isSending) {
    return;
  }

  if (!message) {
    appendMessage("Please type a question so I can help.", "bot");
    return;
  }

  appendMessage(message, "user");
  const loadingBubble = appendMessage("", "bot", { loading: true });
  setComposerState(true);
  let requestFailed = false;

  try {
    loadingBubble.textContent = await requestBotReply(message);
    statusText.textContent = "Online";
  } catch (error) {
    requestFailed = true;
    loadingBubble.textContent = error.message;
    loadingBubble.classList.add("error");
    statusText.textContent = "Needs backend";
  } finally {
    setComposerState(false);
    if (!requestFailed) {
      statusText.textContent = "Online";
    }
    userInput.focus();
  }
}

async function clearServerMemory() {
  try {
    await fetch(`${apiBaseUrl}/clear`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ session_id: sessionId })
    });
  } catch {
    // The local UI can still be cleared even if the backend is offline.
  }
}

function setWelcomeMessages() {
  chatMessages.innerHTML = "";
  appendMessage(
    "Hi, I am CourseBot. Ask me about fees, syllabus, duration, eligibility, timings, mode, certification, or admissions contact details.",
    "bot"
  );
  appendMessage(`Available courses: ${courses.join(", ")}.`, "bot");
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = userInput.value;
  userInput.value = "";
  await handleSend(message);
});

chips.forEach((chip) => {
  chip.addEventListener("click", async () => {
    await handleSend(chip.textContent || "");
  });
});

clearChatButton.addEventListener("click", async () => {
  await clearServerMemory();
  setWelcomeMessages();
  userInput.focus();
});

setWelcomeMessages();
