/**
 * DevTutor AI - Frontend Client Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const messagesContainer = document.getElementById("messages-container");
  const userInput = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");
  const errorMessageInput = document.getElementById("error-message-input");
  const errorInputWrapper = document.getElementById("error-input-wrapper");
  const languageSelect = document.getElementById("language-select");
  const difficultySelect = document.getElementById("difficulty-select");
  const explainCheckbox = document.getElementById("explain-line-by-line");
  const modeButtons = document.querySelectorAll(".mode-btn");
  const currentModeTitle = document.getElementById("current-mode-title");
  const currentModeSubtitle = document.getElementById("current-mode-subtitle");
  const statusDot = document.querySelector(".status-dot");
  const statusText = document.getElementById("status-text");
  const themeToggle = document.getElementById("theme-toggle");
  const clearChatBtn = document.getElementById("clear-chat-btn");
  const sampleChips = document.getElementById("sample-chips");

  // State
  let currentMode = "debug";
  let conversationHistory = []; // list of { role: "user" | "assistant", content: string }
  let isGenerating = false;

  const modeDescriptions = {
    debug: {
      title: "Debug Mode",
      subtitle: "Paste your buggy code below to get line-by-line error identification, root-cause explanation, and fixed code.",
      placeholder: "Paste the code you want to debug here...",
      showErrorBox: true,
    },
    tutorial: {
      title: "Tutorial Mode",
      subtitle: "Ask for any programming concept or data structure to get definitions, syntax, annotated examples, and practice challenges.",
      placeholder: "Enter topic name, e.g. 'Binary Search Trees', 'Recursion', 'Async/Await'...",
      showErrorBox: false,
    },
    qa: {
      title: "Q&A Mode",
      subtitle: "Ask any programming, algorithmic, or software engineering question for direct, concise explanations and code examples.",
      placeholder: "Ask your programming question here...",
      showErrorBox: false,
    },
  };

  // Configure marked.js
  if (window.marked) {
    marked.setOptions({
      breaks: true,
      gfm: true,
      highlight: function (code, lang) {
        if (window.hljs) {
          const language = hljs.getLanguage(lang) ? lang : "plaintext";
          return hljs.highlight(code, { language }).value;
        }
        return code;
      },
    });
  }

  // Health check on load
  async function checkBackendHealth() {
    try {
      const res = await fetch("/health");
      if (res.ok) {
        const data = await res.json();
        statusDot.className = "status-dot online";
        statusText.textContent = `Online (${data.model})`;
        if (!data.gemini_configured) {
          statusText.textContent += " [API Key Needed in .env]";
          statusDot.className = "status-dot offline";
        }
      } else {
        statusDot.className = "status-dot offline";
        statusText.textContent = "Server Error";
      }
    } catch (err) {
      statusDot.className = "status-dot offline";
      statusText.textContent = "Backend Offline";
    }
  }

  checkBackendHealth();

  // Mode Selection
  modeButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const mode = btn.dataset.mode;
      switchMode(mode);
    });
  });

  function switchMode(mode) {
    currentMode = mode;
    modeButtons.forEach((b) => b.classList.toggle("active", b.dataset.mode === mode));

    const meta = modeDescriptions[mode];
    currentModeTitle.textContent = meta.title;
    currentModeSubtitle.textContent = meta.subtitle;
    userInput.placeholder = meta.placeholder;

    if (meta.showErrorBox) {
      errorInputWrapper.classList.add("active");
    } else {
      errorInputWrapper.classList.remove("active");
    }
  }

  // Initialize debug mode UI
  switchMode("debug");

  // Quick Chips Click Handlers
  if (sampleChips) {
    sampleChips.addEventListener("click", (e) => {
      const chip = e.target.closest(".chip-btn");
      if (!chip) return;
      const targetMode = chip.dataset.mode;
      const targetLang = chip.dataset.lang;
      const targetText = chip.dataset.text;

      if (targetMode) switchMode(targetMode);
      if (targetLang) languageSelect.value = targetLang;
      userInput.value = targetText;
      userInput.focus();
    });
  }

  // Handle Enter to send, Shift+Enter for new line
  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  });

  sendBtn.addEventListener("click", handleSend);

  // Send Message Handler
  async function handleSend() {
    const text = userInput.value.trim();
    if (!text || isGenerating) return;

    const errorMsg = errorMessageInput.value.trim();
    const language = languageSelect.value;
    const difficulty = difficultySelect.value;
    const explainLineByLine = explainCheckbox.checked;

    // Display user message in UI
    appendUserMessage(text, currentMode, language, errorMsg);
    userInput.value = "";
    errorMessageInput.value = "";
    userInput.style.height = "auto";

    // Append to conversation history
    let userTurnContent = text;
    if (errorMsg) {
      userTurnContent = `Code:\n${text}\nError:\n${errorMsg}`;
    }
    conversationHistory.push({ role: "user", content: userTurnContent });

    // Show typing indicator
    const loadingElem = appendTypingIndicator();
    scrollToBottom();
    setGeneratingState(true);

    try {
      const payload = {
        mode: currentMode,
        message: text,
        language: language,
        error_message: errorMsg || null,
        difficulty: difficulty,
        explain_line_by_line: explainLineByLine,
        history: conversationHistory.slice(-6), // pass recent history context
      };

      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      loadingElem.remove();

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errMsg = errorData.detail || `Server responded with error status ${response.status}`;
        appendAssistantMessage(`❌ **Error**: ${errMsg}`);
        return;
      }

      const data = await response.json();
      appendAssistantMessage(data.response_text);
      conversationHistory.push({ role: "assistant", content: data.response_text });
    } catch (err) {
      loadingElem.remove();
      appendAssistantMessage(
        `❌ **Network Connection Error**: Unable to reach backend server at \`${window.location.origin}\`. ` +
        `Please verify that the FastAPI backend is running.`
      );
    } finally {
      setGeneratingState(false);
      scrollToBottom();
    }
  }

  function setGeneratingState(generating) {
    isGenerating = generating;
    sendBtn.disabled = generating;
    userInput.disabled = generating;
    if (!generating) {
      userInput.focus();
    }
  }

  function appendUserMessage(text, mode, lang, errorMsg) {
    const msgDiv = document.createElement("div");
    msgDiv.className = "message user";

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = "👤";

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    let html = `<p><strong>[${mode.toUpperCase()} - ${lang.toUpperCase()}]</strong></p>`;
    if (mode === "debug") {
      html += `<pre><code>${escapeHtml(text)}</code></pre>`;
      if (errorMsg) {
        html += `<p style="margin-top: 6px; font-size: 0.82rem; color: #ffb3ba;"><em>Error:</em> <code>${escapeHtml(errorMsg)}</code></p>`;
      }
    } else {
      html += `<p>${escapeHtml(text)}</p>`;
    }

    contentDiv.innerHTML = html;
    msgDiv.appendChild(avatar);
    msgDiv.appendChild(contentDiv);
    messagesContainer.appendChild(msgDiv);
    scrollToBottom();
  }

  function appendAssistantMessage(markdownText) {
    const msgDiv = document.createElement("div");
    msgDiv.className = "message assistant";

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = "⚡";

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    // Render markdown
    if (window.marked) {
      contentDiv.innerHTML = marked.parse(markdownText);
    } else {
      contentDiv.textContent = markdownText;
    }

    // Enhance all <pre><code> blocks with header and copy button
    enhanceCodeBlocks(contentDiv);

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(contentDiv);
    messagesContainer.appendChild(msgDiv);
    scrollToBottom();
  }

  function appendTypingIndicator() {
    const msgDiv = document.createElement("div");
    msgDiv.className = "message assistant loading-msg";

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = "⚡";

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content typing-indicator";
    contentDiv.innerHTML = `
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    `;

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(contentDiv);
    messagesContainer.appendChild(msgDiv);
    return msgDiv;
  }

  function enhanceCodeBlocks(container) {
    const preElements = container.querySelectorAll("pre");
    preElements.forEach((pre) => {
      const codeElem = pre.querySelector("code");
      if (!codeElem) return;

      // Extract language class e.g. class="language-python"
      let languageName = "code";
      codeElem.classList.forEach((cls) => {
        if (cls.startsWith("language-")) {
          languageName = cls.replace("language-", "");
        }
      });

      const wrapper = document.createElement("div");
      wrapper.className = "code-block-wrapper";

      const header = document.createElement("div");
      header.className = "code-header";

      const langSpan = document.createElement("span");
      langSpan.textContent = languageName.toUpperCase();

      const copyBtn = document.createElement("button");
      copyBtn.className = "copy-btn";
      copyBtn.innerHTML = `
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
        </svg>
        <span>Copy</span>
      `;

      copyBtn.addEventListener("click", async () => {
        const textToCopy = codeElem.innerText;
        try {
          await navigator.clipboard.writeText(textToCopy);
          copyBtn.querySelector("span").textContent = "Copied!";
          copyBtn.style.color = "var(--success-color)";
          setTimeout(() => {
            copyBtn.querySelector("span").textContent = "Copy";
            copyBtn.style.color = "";
          }, 2000);
        } catch (e) {
          copyBtn.querySelector("span").textContent = "Failed";
        }
      });

      header.appendChild(langSpan);
      header.appendChild(copyBtn);

      pre.parentNode.insertBefore(wrapper, pre);
      wrapper.appendChild(header);
      wrapper.appendChild(pre);

      if (window.hljs) {
        hljs.highlightElement(codeElem);
      }
    });
  }

  function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Clear Chat
  clearChatBtn.addEventListener("click", () => {
    if (confirm("Are you sure you want to clear the conversation history?")) {
      conversationHistory = [];
      const messages = messagesContainer.querySelectorAll(".message:not(.system-welcome)");
      messages.forEach((m) => m.remove());
    }
  });

  // Dark / Light Theme Toggle
  themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("light-theme");
    const isLight = document.body.classList.contains("light-theme");
    themeToggle.textContent = isLight ? "☀️" : "🌙";
    localStorage.setItem("theme", isLight ? "light" : "dark");
  });

  // Load saved theme
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "light") {
    document.body.classList.add("light-theme");
    themeToggle.textContent = "☀️";
  }
});

