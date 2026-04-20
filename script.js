const courseData = {
  courses: [
    {
      name: "AI Foundations Bootcamp"
    },
    {
      name: "Data Science Career Program"
    },
    {
      name: "Automation with Python"
    }
  ]
};

const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const clearChatButton = document.getElementById("clear-chat");
const chips = document.querySelectorAll(".chip");

let previousResponseId = null;
let isSending = false;
const apiBaseUrl = window.CHATBOT_API_URL || "";

function formatCourseList() {
  return `We currently offer: ${courseData.courses.map((course) => course.name).join(", ")}.`;
}

function appendMessage(content, sender) {
  const message = document.createElement("div");
  message.className = `message ${sender}`;
  message.textContent = content;
  chatMessages.appendChild(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function setComposerState(disabled) {
  userInput.disabled = disabled;
  chatForm.querySelector('button[type="submit"]').disabled = disabled;
}

async function requestBotReply(message) {
  const response = await fetch(`${apiBaseUrl}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      message,
      previous_response_id: previousResponseId
    })
  });

  const contentType = response.headers.get("content-type") || "";
  let payload;

  if (contentType.includes("application/json")) {
    payload = await response.json();
  } else {
    const text = await response.text();
    throw new Error(
      text.includes("<html")
        ? "Chat API not found. If you opened this on GitHub Pages, deploy the Flask backend separately and set window.CHATBOT_API_URL in config.js."
        : "The chatbot API returned an unexpected response."
    );
  }

  if (!response.ok) {
    throw new Error(payload.error || "Something went wrong while contacting the chatbot API.");
  }

  previousResponseId = payload.response_id || null;
  return payload.reply || "I could not generate a response this time.";
}

async function handleSend(message) {
  if (isSending) {
    return;
  }

  if (!message.trim()) {
    appendMessage("Please type a question so I can help.", "bot");
    return;
  }

  isSending = true;
  appendMessage(message, "user");
  appendMessage("Thinking...", "bot");
  setComposerState(true);

  const placeholder = chatMessages.lastElementChild;

  try {
    const response = await requestBotReply(message);
    placeholder.textContent = response;
  } catch (error) {
    placeholder.textContent = error.message;
  } finally {
    isSending = false;
    setComposerState(false);
    userInput.focus();
  }
}

function setWelcomeMessages() {
  previousResponseId = null;
  chatMessages.innerHTML = "";
  appendMessage(
    "Hello! I'm CourseBot. You can ask multiple follow-up questions about fees, syllabus, timings, eligibility, contact details, and more.",
    "bot"
  );
  appendMessage(formatCourseList(), "bot");
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = userInput.value;
  userInput.value = "";
  await handleSend(message);
});

chips.forEach((chip) => {
  chip.addEventListener("click", async () => {
    const question = chip.textContent || "";
    userInput.value = "";
    await handleSend(question);
  });
});

clearChatButton.addEventListener("click", () => {
  setWelcomeMessages();
  userInput.focus();
});

setWelcomeMessages();
