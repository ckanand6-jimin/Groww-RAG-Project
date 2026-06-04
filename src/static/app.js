const suggestions = [
  "What is the expense ratio of HDFC Mid Cap Fund?",
  "What is the minimum SIP amount for HDFC Large Cap Fund?",
  "How do I download my Capital Gains Certificate?",
  "What is the exit load for HDFC Small Cap Fund?",
  "Where can I find the HDFC KIM and SID?",
];

const schemes = [
  "HDFC Mid Cap Fund",
  "HDFC Large Cap Fund",
  "HDFC Small Cap Fund",
  "HDFC Equity Fund",
  "HDFC Tax Saver Fund",
  "HDFC Balanced Advantage Fund",
  "HDFC Nifty 50 Index Fund",
  "HDFC Defence Fund",
  "HDFC Gold ETF Fund of Fund",
  "HDFC Liquid Fund",
];

const sources = [
  "HDFC KIM",
  "HDFC SID",
  "HDFC Online Services",
  "HDFC Consolidated Account Statement",
  "AMFI Investor Education",
  "SEBI Investor Portal",
  "Groww HDFC scheme pages",
];

const state = {
  messages: [],
  loading: false,
  recentChats: [],
};

const messagesEl = document.getElementById("messages");
const suggestionBar = document.getElementById("suggestionBar");
const schemeList = document.getElementById("schemeList");
const sourceList = document.getElementById("sourceList");
const recentChatsEl = document.getElementById("recentChats");
const queryInput = document.getElementById("queryInput");
const sendBtn = document.getElementById("sendBtn");
const newChatBtn = document.getElementById("newChatBtn");
const sidebarToggle = document.getElementById("sidebarToggle");
const sidebar = document.getElementById("sidebar");

function createElement(tag, className, text = "") {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (text) el.textContent = text;
  return el;
}

function normalizeAnswer(text, citation) {
  if (!text) return "";
  const escaped = citation ? citation.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&") : "";
  const pattern = new RegExp(`\\s*\\[${escaped}\\]\\s*$`);
  return text.replace(pattern, "").trim();
}

function stripUrls(text) {
  if (!text) return text;
  return text.replace(/https?:\/\/\S+/g, "")
             .replace(/www\.\S+/g, "")
             .trim();
}

function renderSuggestions() {
  suggestionBar.innerHTML = "";
  suggestions.forEach((text) => {
    const button = createElement("button", "suggestion-chip", text);
    button.type = "button";
    button.addEventListener("click", () => {
      queryInput.value = text;
      submitQuery(text);
    });
    suggestionBar.appendChild(button);
  });
}

function renderSidebarItems() {
  schemeList.innerHTML = "";
  sourceList.innerHTML = "";
  recentChatsEl.innerHTML = "";

  state.recentChats.slice(-5).reverse().forEach((text) => {
    const item = createElement("li", "");
    const button = createElement("button", "", text);
    button.addEventListener("click", () => {
      queryInput.value = text;
      submitQuery(text);
    });
    item.appendChild(button);
    recentChatsEl.appendChild(item);
  });

  schemes.forEach((label) => {
    const item = createElement("li", "", label);
    schemeList.appendChild(item);
  });

  sources.forEach((label) => {
    const item = createElement("li", "", label);
    sourceList.appendChild(item);
  });
}

function createCitationCard(message) {
  if (!message.citation) return null;
  const card = createElement("div", "citation-card");
  const heading = createElement("div", "citation-title", "Source");
  const subtitle = createElement("div", "citation-subtitle", message.sourceName || message.citation);
  const date = createElement("div", "citation-date", `Last updated: ${message.last_updated}`);
  const link = createElement("a", "citation-link", "View Source");
  link.href = message.citation;
  link.target = "_blank";
  link.rel = "noreferrer noopener";
  link.setAttribute("aria-label", `View source ${message.sourceName || message.citation}`);

  const meta = createElement("div", "citation-meta");
  meta.appendChild(heading);
  meta.appendChild(date);
  card.appendChild(meta);
  card.appendChild(subtitle);
  card.appendChild(link);
  return card;
}

function createClarificationCard(schemes, originalQuery) {
  if (!schemes || !schemes.length) return null;
  const card = createElement("div", "clarification-card");
  const title = createElement("div", "clarification-title", "Multiple HDFC schemes match your query");
  card.appendChild(title);
  const list = createElement("div", "clarification-list");
  schemes.forEach((s) => {
    const btn = createElement("button", "clarification-btn", s);
    btn.type = "button";
    btn.addEventListener("click", () => {
      // re-submit the query scoped to the selected scheme
      const scoped = `${originalQuery} scheme:${s}`;
      queryInput.value = scoped;
      submitQuery(scoped);
    });
    list.appendChild(btn);
  });
  card.appendChild(list);
  return card;
}

function renderMessages() {
  messagesEl.innerHTML = "";

  if (state.messages.length === 0) {
    const emptyCard = createElement("div", "message-bubble message-assistant-bubble");
    emptyCard.innerHTML = `<div class="message-heading">Ask a question about HDFC mutual funds.</div>
      <div class="message-body">Try one of the suggested questions or enter your own query about schemes, documents, or expenses.</div>`;
    const emptyRow = createElement("div", "message-row message-assistant-row");
    emptyRow.appendChild(emptyCard);
    messagesEl.appendChild(emptyRow);
    return;
  }

  state.messages.forEach((message) => {
    const row = createElement("div", `message-row ${message.role === "user" ? "message-user-row" : "message-assistant-row"}`);

    const avatar = createElement("div", `avatar ${message.role === "user" ? "avatar-user" : "avatar-assistant"}`);
    avatar.textContent = message.role === "user" ? "U" : "H";

    const content = createElement("div", "message-content");
    const bubble = createElement("div", `message-bubble ${message.role === "user" ? "message-user-bubble" : "message-assistant-bubble"}`);

    if (message.role === "user") {
      bubble.textContent = message.text;
      content.appendChild(bubble);
      row.appendChild(avatar);
      row.appendChild(content);
    } else {
      const heading = createElement("div", "message-heading", message.heading || "Answer");
      const body = createElement("div", "message-body");
      // ensure we don't show raw links in the answer text
      const raw = message.html || message.text || "";
      const cleaned = stripUrls(raw).replace(/\n/g, "<br />");
      body.innerHTML = cleaned;

      bubble.appendChild(heading);
      bubble.appendChild(body);

      if (message.responseType === "REFUSAL") {
        bubble.classList.add("alert-card");
        const alertCopy = createElement("div", "alert-copy", "I can only provide factual information about HDFC mutual fund schemes. I cannot provide investment advice or recommend specific funds.");
        const alertLink = createElement("a", "alert-link", "AMFI Investor Education");
        alertLink.href = "https://www.amfiindia.com/investor";
        alertLink.target = "_blank";
        alertLink.rel = "noreferrer noopener";
        bubble.appendChild(alertCopy);
        bubble.appendChild(alertLink);
      }

      content.appendChild(bubble);

      // clarification card when multiple schemes match
      const clarificationCard = (message.clarifications && message.clarifications.length) ? createClarificationCard(message.clarifications, message._original_query || '') : null;
      if (clarificationCard) content.appendChild(clarificationCard);

      const citationCard = createCitationCard(message);
      if (citationCard) content.appendChild(citationCard);

      row.appendChild(avatar);
      row.appendChild(content);
    }

    messagesEl.appendChild(row);
  });

  // autoscroll to latest
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addUserMessage(text) {
  state.messages.push({ role: "user", text });
  if (!state.recentChats.includes(text)) {
    state.recentChats.push(text);
  }
  renderSidebarItems();
  renderMessages();
}

function addAssistantMessage(payload) {
  const citationUrl = payload.citation || payload.source_url || null;
  let displayText = payload.answer || "";
  if (citationUrl) {
    displayText = normalizeAnswer(displayText, citationUrl);
  }

  // remove raw urls from answer text
  displayText = stripUrls(displayText);

  const msg = {
    role: "assistant",
    heading: payload.response_type === "REFUSAL" ? "I can't provide investment advice" : "Answer",
    text: displayText,
    html: displayText.replace(/\n/g, "<br />"),
    citation: citationUrl,
    sourceName: payload.source_url ? (() => { try { return new URL(payload.source_url).hostname; } catch(e){ return payload.source_url; } })() : null,
    last_updated: payload.last_updated || "unknown",
    responseType: payload.response_type,
    error: payload.error,
  };

  // handle possible scheme disambiguation hints from backend (many possible field names)
  const candidates = payload.scheme_matches || payload.scheme_candidates || payload.candidates || payload.matches || null;
  if (candidates && Array.isArray(candidates) && candidates.length > 1) {
    msg.clarifications = candidates;
    msg._original_query = payload.original_query || payload.query || '';
  }

  state.messages.push(msg);
  renderMessages();
}

function showLoading() {
  const loadingCard = createElement("div", "message-bubble message-assistant-bubble");
  loadingCard.innerHTML = `<div class="message-heading">Looking up facts...</div><div class="message-body">Searching the HDFC corpus for the best source-backed answer.</div>`;
  const row = createElement("div", "message-row message-assistant-row");
  row.appendChild(loadingCard);
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setLoading(value) {
  state.loading = value;
  sendBtn.disabled = value;
  queryInput.disabled = value;
  if (value) {
    sendBtn.classList.add('loading');
  } else {
    sendBtn.classList.remove('loading');
  }
}

async function submitQuery(queryText) {
  const trimmed = queryText.trim();
  if (!trimmed || state.loading) return;

  addUserMessage(trimmed);
  queryInput.value = "";
  setLoading(true);
  renderMessages();
  showLoading();

  try {
    const response = await fetch("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: trimmed }),
    });
    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }
    const payload = await response.json();
    addAssistantMessage(payload);
  } catch (err) {
    addAssistantMessage({
      response_type: "ERROR",
      answer: "Something went wrong while fetching the answer. Please try again.",
      citation: null,
      last_updated: new Date().toISOString().slice(0, 10),
      error: err.message,
    });
  } finally {
    setLoading(false);
  }
}

function clearChat() {
  state.messages = [];
  renderMessages();
}

function toggleSidebar() {
  sidebar.classList.toggle("open");
}

sendBtn.addEventListener("click", () => submitQuery(queryInput.value));
queryInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    submitQuery(queryInput.value);
  }
});
newChatBtn.addEventListener("click", clearChat);
sidebarToggle.addEventListener("click", toggleSidebar);
window.addEventListener("click", (event) => {
  if (!sidebar.contains(event.target) && !sidebarToggle.contains(event.target) && sidebar.classList.contains("open")) {
    sidebar.classList.remove("open");
  }
});

renderSuggestions();
renderSidebarItems();
renderMessages();
