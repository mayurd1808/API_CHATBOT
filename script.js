const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");
const clearChatButton = document.getElementById("clear-chat");
const chips = document.querySelectorAll(".chip");
const statusText = document.getElementById("status-text");
const courseCount = document.getElementById("course-count");
const courseLibrary = document.getElementById("course-library");

const apiBaseUrl = (window.CHATBOT_API_URL || "").replace(/\/$/, "");
const sessionId = getSessionId();
let isSending = false;
let courses = [
  "AI Foundations Bootcamp",
  "Data Science Career Program",
  "Automation with Python",
  "Full Stack Web Development",
  "Cloud Computing Essentials",
  "Cybersecurity Fundamentals"
];

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

  if (options.loading) {
    bubble.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
    message.dataset.loading = "true";
  } else if (sender === "bot") {
    renderStructuredReply(bubble, content);
  } else {
    bubble.textContent = content;
  }

  message.append(avatar, bubble);
  chatMessages.appendChild(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return bubble;
}

function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatInlineMarkdown(value) {
  return escapeHtml(value).replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
}

function renderStructuredReply(element, content) {
  const lines = content
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  if (lines.length === 0) {
    element.textContent = "";
    return;
  }

  const html = [];
  let listOpen = false;

  lines.forEach((line) => {
    const bulletMatch = line.match(/^[-*]\s+(.*)$/);

    if (bulletMatch) {
      if (!listOpen) {
        html.push("<ul>");
        listOpen = true;
      }
      html.push(`<li>${formatInlineMarkdown(bulletMatch[1])}</li>`);
      return;
    }

    if (listOpen) {
      html.push("</ul>");
      listOpen = false;
    }

    if (/^\*\*.+\*\*$/.test(line)) {
      html.push(`<h3>${formatInlineMarkdown(line.replace(/^\*\*|\*\*$/g, ""))}</h3>`);
    } else {
      html.push(`<p>${formatInlineMarkdown(line)}</p>`);
    }
  });

  if (listOpen) {
    html.push("</ul>");
  }

  element.innerHTML = html.join("");
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
    renderStructuredReply(loadingBubble, await requestBotReply(message));
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

function renderCourseLibrary() {
  courseLibrary.innerHTML = "";

  courses.forEach((course, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "course-library-item";
    button.innerHTML = `<span>${String(index + 1).padStart(2, "0")}</span><strong>${course}</strong>`;
    button.addEventListener("click", () => {
      handleSend(`Tell me about ${course}`);
    });
    courseLibrary.appendChild(button);
  });
}

async function loadCourses() {
  try {
    const response = await fetch(`${apiBaseUrl}/courses`);
    const payload = await parseApiResponse(response);

    if (Array.isArray(payload.courses) && payload.courses.length > 0) {
      courses = payload.courses;
      courseCount.textContent = String(payload.count || courses.length);
    }
  } catch {
    courseCount.textContent = String(courses.length);
  } finally {
    renderCourseLibrary();
  }
}

function setWelcomeMessages() {
  chatMessages.innerHTML = "";
  appendMessage(
    "Hi, I am CourseBot. Ask me about fees, syllabus, duration, eligibility, timings, mode, certification, or admissions contact details.",
    "bot"
  );
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

loadCourses().finally(setWelcomeMessages);
