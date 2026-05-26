// ── Session Management ──────────────────────────────────────
function getOrCreateSessionId() {
  let sessionId = localStorage.getItem("novatech_session_id");
  if (!sessionId) {
    sessionId = "session_" + Math.random().toString(36).substr(2, 9);
    localStorage.setItem("novatech_session_id", sessionId);
  }
  return sessionId;
}

let SESSION_ID = getOrCreateSessionId();

// ── DOM Elements ────────────────────────────────────────────
const messagesArea    = document.getElementById("messagesArea");
const userInput       = document.getElementById("userInput");
const sendBtn         = document.getElementById("sendBtn");
const newChatBtn      = document.getElementById("newChatBtn");
const sessionDisplay  = document.getElementById("sessionDisplay");
const charCount       = document.getElementById("charCount");
const loadingOverlay  = document.getElementById("loadingOverlay");
const messagesWrapper = document.getElementById("messagesWrapper");

// ── Display short session ID ─────────────────────────────────
sessionDisplay.textContent = SESSION_ID.split("_")[1]?.toUpperCase() || SESSION_ID;


// ── Get current timestamp ────────────────────────────────────
function getTimestamp() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}


// ── Append a message bubble ──────────────────────────────────
function appendMessage(role, text, meta = {}) {
  const isUser = role === "user";

  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", isUser ? "user-message" : "assistant-message");

  const avatar = document.createElement("div");
  avatar.classList.add("message-avatar");
  avatar.textContent = isUser ? "🧑" : "🤖";

  const contentDiv = document.createElement("div");
  contentDiv.classList.add("message-content");

  const bubble = document.createElement("div");
  bubble.classList.add("message-bubble");
  bubble.innerHTML = text.replace(/\n/g, "<br/>");

  const timeDiv = document.createElement("div");
  timeDiv.classList.add("message-time");
  timeDiv.textContent = getTimestamp();

  contentDiv.appendChild(bubble);

  // ── Show retrieved chunks count for assistant ────────────
  if (!isUser && meta.retrievedChunks !== undefined) {
    const badge = document.createElement("div");
    badge.classList.add("chunk-badge");
    badge.textContent = `📄 ${meta.retrievedChunks} source(s) retrieved · ${meta.tokensUsed || 0} tokens`;
    contentDiv.appendChild(badge);
  }

  contentDiv.appendChild(timeDiv);

  messageDiv.appendChild(avatar);
  messageDiv.appendChild(contentDiv);
  messagesArea.appendChild(messageDiv);

  scrollToBottom();
}


// ── Show typing indicator ────────────────────────────────────
function showTypingIndicator() {
  const div = document.createElement("div");
  div.classList.add("message", "assistant-message", "typing-indicator");
  div.id = "typingIndicator";
  div.innerHTML = `
    <div class="message-avatar">🤖</div>
    <div class="message-content">
      <div class="message-bubble">
        <span></span><span></span><span></span>
      </div>
    </div>`;
  messagesArea.appendChild(div);
  scrollToBottom();
}


// ── Remove typing indicator ──────────────────────────────────
function removeTypingIndicator() {
  const indicator = document.getElementById("typingIndicator");
  if (indicator) indicator.remove();
}


// ── Auto scroll to bottom ────────────────────────────────────
function scrollToBottom() {
  messagesWrapper.scrollTop = messagesWrapper.scrollHeight;
}


// ── Set loading state ────────────────────────────────────────
function setLoading(isLoading) {
  sendBtn.disabled   = isLoading;
  userInput.disabled = isLoading;
  if (isLoading) {
    showTypingIndicator();
  } else {
    removeTypingIndicator();
  }
}


// ── Send message ─────────────────────────────────────────────
async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  // ── Display user message ──────────────────────────────────
  appendMessage("user", message);
  userInput.value = "";
  charCount.textContent = "0/500";
  autoResizeTextarea();

  setLoading(true);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sessionId: SESSION_ID,
        message: message
      })
    });

    const data = await response.json();

    if (!response.ok) {
      const errMsg = data.detail?.error || data.error || "Something went wrong.";
      appendMessage("assistant", `⚠️ Error: ${errMsg}`);
      return;
    }

    // ── Display assistant reply ───────────────────────────
    appendMessage("assistant", data.reply, {
      retrievedChunks: data.retrievedChunks,
      tokensUsed: data.tokensUsed
    });

  } catch (error) {
    console.error("Request failed:", error);
    appendMessage("assistant", "⚠️ Could not reach the server. Please check your connection.");
  } finally {
    setLoading(false);
  }
}


// ── New Chat ─────────────────────────────────────────────────
async function startNewChat() {
  // Clear session on backend
  try {
    await fetch(`/api/session/${SESSION_ID}`, { method: "DELETE" });
  } catch (e) {
    console.warn("Could not clear session on server:", e);
  }

  // Create new session
  SESSION_ID = "session_" + Math.random().toString(36).substr(2, 9);
  localStorage.setItem("novatech_session_id", SESSION_ID);
  sessionDisplay.textContent = SESSION_ID.split("_")[1]?.toUpperCase();

  // Clear chat UI
  messagesArea.innerHTML = "";
  appendMessage(
    "assistant",
    "🆕 New chat started! How can I help you today?"
  );
}


// ── Auto resize textarea ──────────────────────────────────────
function autoResizeTextarea() {
  userInput.style.height = "auto";
  userInput.style.height = Math.min(userInput.scrollHeight, 120) + "px";
}


// ── Event Listeners ──────────────────────────────────────────
sendBtn.addEventListener("click", sendMessage);

newChatBtn.addEventListener("click", startNewChat);

userInput.addEventListener("input", () => {
  charCount.textContent = `${userInput.value.length}/500`;
  autoResizeTextarea();
});

userInput.addEventListener("keydown", (e) => {
  // Enter = send, Shift+Enter = new line
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});