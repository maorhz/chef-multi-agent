# -*- coding: utf-8 -*-
"""
🍽️ Gourmet Chef & Grocery Assistant - Static Assets
This file embeds the HTML, CSS, and JS resources as raw Python strings
to ensure they are packaged and deployed successfully to Cloud Run.
"""

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gourmet Chef & Grocery Planner</title>
  <!-- Typography -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
  <!-- Icons -->
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />
  <!-- Custom Stylesheet (with cache-busting query param) -->
  <link rel="stylesheet" href="/static/styles.css?v=3">
  
  <!-- Injected Regex Placeholder -->
  <script>
    window.MASK_REGEX_STR = MASK_REGEX_PLACEHOLDER;
  </script>
</head>
<body>
  <div class="app-container">
    <!-- Header -->
    <header class="app-header">
      <div class="header-logo">
        <span class="material-symbols-outlined logo-icon">restaurant</span>
        <h1>Gourmet Chef</h1>
      </div>
      <div class="security-status">
        <span class="material-symbols-outlined security-icon">shield</span>
        <span class="security-text">SDP Protected</span>
      </div>
    </header>

    <!-- Main Chat Area -->
    <main class="chat-area">
      <!-- Chat History Stream -->
      <div class="chat-history" id="chatHistory">
        <div class="message system-message">
          <span class="material-symbols-outlined system-avatar">cooking</span>
          <div class="message-body">
            <p>Welcome! I am your personal gourmet chef and grocery planner. Tell me what you're craving, what ingredients you want to use, or any dietary restrictions.</p>
            <p style="margin-top: 8px; color: var(--text-secondary); font-size: 13px;">Try one of the suggestions below to get started:</p>
            <div class="suggestion-pills">
              <button class="pill-btn" onclick="sendSuggestion('I want a high-protein keto dinner using chicken breasts')">🍗 High-Protein Keto Dinner</button>
              <button class="pill-btn" onclick="sendSuggestion('Show me a quick 15-minute vegan pasta recipe')">🌱 15-Min Vegan Pasta</button>
              <button class="pill-btn" onclick="sendSuggestion('Suggest a gluten-free salmon dinner with avocado')">🥑 Gluten-Free Salmon</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Chat Input Area -->
      <div class="input-area-container">
        <form class="chat-input-container" id="chatForm">
          <textarea 
            class="chat-textarea" 
            id="chatInput" 
            placeholder="Ask for a recipe, ingredients on hand, or dietary plan..."
            rows="1"
            required
          ></textarea>
          <button type="submit" class="send-btn" id="sendBtn">
            <span class="material-symbols-outlined">arrow_upward</span>
          </button>
        </form>
      </div>
    </main>
  </div>

  <!-- Reusable Custom Dialog Modal -->
  <div class="gourmet-modal" id="gourmetModal">
    <div class="modal-overlay" onclick="closeModal()"></div>
    <div class="modal-card">
      <div class="modal-header" id="modalHeader">
        <span class="material-symbols-outlined modal-header-icon" id="modalIcon">shield</span>
        <h3 id="modalTitle">Security Notice</h3>
      </div>
      <div class="modal-body" id="modalBody">
        <!-- Content dynamically injected -->
      </div>
      <div class="modal-footer">
        <button class="modal-btn" onclick="closeModal()">Dismiss</button>
      </div>
    </div>
  </div>

  <!-- Custom Javascript (with cache-busting query param) -->
  <script src="/static/app.js?v=3"></script>
</body>
</html>"""

CSS_CONTENT = """/* ==========================================================================
   🎨 Gourmet Theme CSS - Focused Single-Column Conversational Stream
   ========================================================================== */

:root {
  --bg-app: hsl(220, 12%, 6%);
  --bg-panel: rgba(22, 24, 30, 0.7);
  --bg-panel-solid: hsl(222, 15%, 12%);
  --border-glass: rgba(255, 255, 255, 0.06);
  --border-glass-hover: rgba(255, 255, 255, 0.12);
  
  --text-primary: hsl(0, 0%, 95%);
  --text-secondary: hsl(220, 8%, 65%);
  --text-muted: hsl(220, 6%, 45%);
  
  --accent-gold: hsl(38, 92%, 52%);
  --accent-gold-rgb: 241, 168, 10;
  --accent-green: hsl(142, 38%, 45%);
  --accent-red: hsl(0, 75%, 45%);
  
  --shadow-main: 0 12px 40px rgba(0, 0, 0, 0.4);
  --transition-smooth: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  --radius-lg: 16px;
  --radius-md: 12px;
  --radius-sm: 8px;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background-color: var(--bg-app);
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
  height: 100vh;
  display: flex;
  justify-content: center;
  -webkit-font-smoothing: antialiased;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Outfit', sans-serif;
  font-weight: 600;
}

.app-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 800px;
  height: 100vh;
  padding: 16px;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 12px 20px;
  background: var(--bg-panel);
  border: 1px solid var(--border-glass);
  backdrop-filter: blur(12px);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-main);
  flex-shrink: 0;
}

.header-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  color: var(--accent-gold);
  font-size: 24px;
}

.app-header h1 {
  font-size: 18px;
}

.security-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  background: rgba(76, 175, 80, 0.1);
  border: 1px solid rgba(76, 175, 80, 0.25);
  border-radius: 20px;
}

.security-icon {
  color: var(--accent-green);
  font-size: 14px;
}

.security-text {
  font-size: 10px;
  font-weight: 500;
  color: var(--accent-green);
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.chat-area {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  background: var(--bg-panel);
  border: 1px solid var(--border-glass);
  backdrop-filter: blur(16px);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-main);
  padding: 8px 0;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  scroll-behavior: smooth;
}

.message {
  display: flex;
  gap: 14px;
  max-width: 90%;
  animation: messageFadeIn 0.3s ease-out forwards;
}

@keyframes messageFadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.message.system-message, .message.chef-message {
  align-self: flex-start;
  max-width: 95%;
}

.message.user-message {
  align-self: flex-end;
  flex-direction: row-reverse;
  max-width: 85%;
}

.system-avatar {
  background: rgba(241, 168, 10, 0.1);
  color: var(--accent-gold);
  border: 1px solid rgba(241, 168, 10, 0.2);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 18px;
}

.message-body {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-glass);
  padding: 16px 20px;
  border-radius: var(--radius-md);
  font-size: 14.5px;
  line-height: 1.6;
  color: var(--text-primary);
  word-break: break-word;
}

.message.user-message .message-body {
  background: rgba(241, 168, 10, 0.08);
  border-color: rgba(241, 168, 10, 0.2);
  border-radius: var(--radius-md) 0 var(--radius-md) var(--radius-md);
}

.suggestion-pills {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
}

.pill-btn {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-glass);
  color: var(--text-secondary);
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 13px;
  text-align: left;
  font-weight: 500;
  transition: var(--transition-smooth);
}

.pill-btn:hover {
  background: rgba(241, 168, 10, 0.08);
  border-color: rgba(241, 168, 10, 0.3);
  color: var(--accent-gold);
  transform: translateX(4px);
}

.shielded-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(244, 67, 54, 0.12);
  border: 1px solid rgba(244, 67, 54, 0.25);
  color: #ff7961;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11.5px;
  font-weight: 500;
  cursor: pointer;
  vertical-align: middle;
  margin: 0 2px;
  transition: var(--transition-smooth);
}

.shielded-badge:hover {
  background: rgba(244, 67, 54, 0.2);
  border-color: rgba(244, 67, 54, 0.4);
  transform: scale(1.03);
}

.input-area-container {
  padding: 12px 20px;
  border-top: 1px solid var(--border-glass);
  background: rgba(0, 0, 0, 0.15);
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  flex-shrink: 0;
}

.chat-input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.chat-textarea {
  flex: 1;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  padding: 12px 16px;
  font-size: 14.5px;
  line-height: 1.4;
  font-family: 'Inter', sans-serif;
  resize: none;
  outline: none;
  max-height: 120px;
  transition: var(--transition-smooth);
}

.chat-textarea:focus {
  border-color: rgba(241, 168, 10, 0.4);
  background: rgba(255, 255, 255, 0.05);
  box-shadow: 0 0 0 3px rgba(241, 168, 10, 0.1);
}

.send-btn {
  background: var(--accent-gold);
  border: none;
  color: #000;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: var(--transition-smooth);
}

.send-btn:hover {
  background: hsl(38, 92%, 60%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(241, 168, 10, 0.3);
}

.send-btn:disabled {
  background: var(--text-muted);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loader-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-top-color: var(--text-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.message-body h1, .message-body h2, .message-body h3 {
  color: var(--accent-gold);
  margin-top: 16px;
  margin-bottom: 8px;
  font-weight: 500;
}

.message-body h2 { font-size: 17px; }
.message-body h3 { font-size: 15.5px; border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 4px; }

.message-body p {
  margin-bottom: 10px;
}

.message-body ul {
  list-style-type: none;
  padding-left: 0;
  margin-bottom: 14px;
}

.message-body li {
  position: relative;
  padding-left: 16px;
  margin-bottom: 6px;
}

.message-body li::before {
  content: "•";
  color: var(--accent-gold);
  position: absolute;
  left: 4px;
  font-weight: bold;
}

.embedded-gourmet-card {
  margin-top: 18px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  animation: cardSlideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes cardSlideIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

.gourmet-accordion {
  border-bottom: 1px solid var(--border-glass);
}

.gourmet-accordion:last-child {
  border-bottom: none;
}

.accordion-trigger {
  width: 100%;
  background: transparent;
  border: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  color: var(--text-primary);
  font-family: 'Outfit', sans-serif;
  font-size: 14.5px;
  font-weight: 500;
  cursor: pointer;
  text-align: left;
  transition: var(--transition-smooth);
}

.accordion-trigger:hover {
  background: rgba(255, 255, 255, 0.02);
  color: var(--accent-gold);
}

.trigger-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trigger-title-group span.material-symbols-outlined {
  color: var(--accent-gold);
  font-size: 20px;
}

.accordion-icon {
  font-size: 18px;
  transition: transform 0.3s ease;
  color: var(--text-secondary);
}

.gourmet-accordion.open .accordion-icon {
  transform: rotate(180deg);
  color: var(--accent-gold);
}

.accordion-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease-out, padding 0.3s ease;
  background: rgba(0, 0, 0, 0.1);
  padding: 0 18px;
}

.gourmet-accordion.open .accordion-content {
  max-height: 600px;
  padding: 16px 18px;
  overflow-y: auto;
}

.embedded-checklist-departments {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.checklist-dept-section h4 {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--accent-gold);
  margin-bottom: 8px;
}

.checklist-dept-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checklist-item-row {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.01);
  border: 1px solid rgba(255, 255, 255, 0.04);
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition-smooth);
}

.checklist-item-row:hover {
  background: rgba(255, 255, 255, 0.03);
  border-color: var(--border-glass-hover);
}

.checklist-item-row input {
  display: none;
}

.check-circle-custom {
  width: 18px;
  height: 18px;
  border: 2px solid var(--text-muted);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-smooth);
  flex-shrink: 0;
}

.check-circle-custom::after {
  content: "check";
  font-family: 'Material Symbols Outlined';
  font-size: 12px;
  color: #000;
  display: none;
}

.checklist-item-row input:checked + .check-circle-custom {
  background: var(--accent-green);
  border-color: var(--accent-green);
}

.checklist-item-row input:checked + .check-circle-custom::after {
  display: block;
}

.checklist-item-row-text {
  font-size: 13.5px;
  color: var(--text-primary);
  transition: var(--transition-smooth);
}

.checklist-item-row input:checked ~ .checklist-item-row-text {
  text-decoration: line-through;
  color: var(--text-muted);
}

.embedded-nutrition-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.nutrition-pill {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-glass);
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
  gap: 6px;
  position: relative;
  overflow: hidden;
}

.nutrition-pill::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
}

.cal-pill::before { background: var(--accent-gold); }
.pro-pill::before { background: #2196f3; }
.carb-pill::before { background: #e91e63; }
.fat-pill::before { background: #9c27b0; }

.nutrition-pill .pill-name {
  font-size: 11px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.nutrition-pill .pill-val {
  font-size: 18px;
  font-family: 'Outfit', sans-serif;
  font-weight: 600;
}

.nutrition-pill .pill-val .unit {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 400;
}

.pill-track {
  background: rgba(255, 255, 255, 0.04);
  height: 4px;
  border-radius: 2px;
  overflow: hidden;
}

.pill-bar {
  height: 100%;
  border-radius: 2px;
  transition: width 1s ease-out;
}

.cal-pill .pill-bar { background: var(--accent-gold); }
.pro-pill .pill-bar { background: #2196f3; }
.carb-pill .pill-bar { background: #e91e63; }
.fat-pill .pill-bar { background: #9c27b0; }

.gourmet-modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.gourmet-modal.open {
  display: flex;
}

.modal-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  animation: overlayFadeIn 0.3s ease-out forwards;
}

@keyframes overlayFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-card {
  position: relative;
  background: hsl(222, 15%, 12%);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 480px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 1001;
  animation: cardSlideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
  border-left: 5px solid var(--accent-gold);
}

@keyframes cardSlideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.gourmet-modal.type-security .modal-card {
  border-left-color: var(--accent-red);
}

.gourmet-modal.type-pii .modal-card {
  border-left-color: var(--accent-gold);
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px 14px 24px;
  border-bottom: 1px solid var(--border-glass);
}

.modal-header-icon {
  font-size: 28px;
  color: var(--accent-gold);
}

.gourmet-modal.type-security .modal-header-icon {
  color: var(--accent-red);
}

.gourmet-modal.type-pii .modal-header-icon {
  color: var(--accent-gold);
}

.modal-header h3 {
  font-size: 18px;
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
  font-size: 14.5px;
  line-height: 1.6;
  color: var(--text-secondary);
  overflow-y: auto;
  max-height: 300px;
}

.modal-body strong {
  color: var(--text-primary);
}

.modal-body code {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 3px 6px;
  border-radius: 4px;
  font-family: monospace;
  color: var(--accent-gold);
  font-size: 13px;
  word-break: break-all;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 14px 24px 20px 24px;
  border-top: 1px solid var(--border-glass);
  background: rgba(0, 0, 0, 0.15);
}

.modal-btn {
  background: var(--border-glass);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
  padding: 8px 20px;
  border-radius: var(--radius-sm);
  font-family: 'Inter', sans-serif;
  font-size: 13.5px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition-smooth);
}

.modal-btn:hover {
  background: var(--accent-gold);
  border-color: var(--accent-gold);
  color: #000;
}

.gourmet-modal.type-security .modal-btn:hover {
  background: var(--accent-red);
  border-color: var(--accent-red);
  color: #fff;
}
"""

JS_CONTENT = """/* ==========================================================================
   ☕ Gourmet Chef - Single-Column Conversational Javascript
   ========================================================================== */

function initializeApp() {
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const chatHistory = document.getElementById("chatHistory");
  const sendBtn = document.getElementById("sendBtn");

  const gourmetModal = document.getElementById("gourmetModal");
  const modalTitle = document.getElementById("modalTitle");
  const modalBody = document.getElementById("modalBody");
  const modalIcon = document.getElementById("modalIcon");

  let isGenerating = false;
  let activeSessionId = "session-" + Math.random().toString(36).substring(2, 15);
  const maskedTexts = new Map();

  let MASK_REGEX = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
  
  try {
    const rawPattern = window.MASK_REGEX_STR;
    if (rawPattern && typeof rawPattern === "string") {
      let cleanPattern = rawPattern;
      let flags = "gi";
      
      if (cleanPattern.includes("(?i)")) {
        cleanPattern = cleanPattern.replace(/\(\?i\)/g, "");
      }
      
      MASK_REGEX = new RegExp(cleanPattern, flags);
      remoteLog("[Custom UI] Successfully compiled custom regex: " + cleanPattern);
    }
  } catch (err) {
    console.warn("Failed to compile custom regex pattern, falling back to default.", err);
    remoteLog("[Custom UI] Regex compile warning: " + err.message);
  }

  remoteLog("[Custom UI] Conversational app initialized. Session: " + activeSessionId);

  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (isGenerating) return;
    
    const prompt = chatInput.value.trim();
    if (!prompt) return;

    chatInput.value = "";
    chatInput.style.height = "auto";
    
    await processAndSendPrompt(prompt);
  });

  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event("submit"));
    }
  });

  chatInput.addEventListener("input", function() {
    this.style.height = "auto";
    this.style.height = (this.scrollHeight) + "px";
  });

  async function processAndSendPrompt(rawPrompt) {
    isGenerating = true;
    sendBtn.disabled = true;
    sendBtn.innerHTML = `<span class="loader-spinner"></span>`;
    
    try {
      const localMatches = rawPrompt.match(MASK_REGEX) || [];
      localMatches.forEach(match => {
        const masked = "#".repeat(match.length);
        maskedTexts.set(match, masked);
      });
      remoteLog("[Custom UI] Optimistic masking matches: " + JSON.stringify(localMatches));
    } catch (e) {
      console.warn("Error during optimistic masking:", e);
    }

    const userMessageBody = renderTextWithShields(rawPrompt);
    appendMessage("user", userMessageBody);

    let finalPrompt = rawPrompt;
    try {
      const evalRes = await fetch("/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: rawPrompt })
      });
      
      if (evalRes.ok) {
        const evalData = await evalRes.json();
        remoteLog("[Custom UI] /evaluate result: " + JSON.stringify(evalData));
        
        if (evalData.block) {
          showModal(
            "Security Blocked",
            `<p>⚠️ <strong>Active Prompt Shield Intervention</strong></p>
             <p>Your request was blocked because it contains instructions that violated the active safety templates (e.g. jailbreaks, injection attempts, or malicious inputs).</p>
             <p style="margin-top: 12px;">The downstream culinary agent workflow has been safely halted to protect system integrity.</p>`,
            "security"
          );
          
          appendMessage("system", `<span style="color:var(--accent-red); font-weight:600;">[Security Alert] Your request was blocked by security filters.</span>`);
          resetGenerationState();
          return;
        }
        
        if (evalData.deidentified_text) {
          finalPrompt = evalData.deidentified_text;
          const backendMatches = extractPIIDiffs(rawPrompt, finalPrompt);
          backendMatches.forEach(([clearText, maskedText]) => {
            maskedTexts.set(clearText, maskedText);
          });
        }
      }
    } catch (err) {
      console.warn("Failed to contact /evaluate endpoint, falling back to client-side masking", err);
    }

    const activeBubbleId = "active-chef-" + Date.now();
    appendMessage("chef", `<div class="loader-spinner" style="display:inline-block;vertical-align:middle;margin-right:8px;width:16px;height:16px;border-width:2px;"></div>Whipping up your recipe...`, activeBubbleId);
    const chefBubbleBody = document.getElementById(activeBubbleId);

    let accumulatedResponse = "";

    try {
      const response = await fetch("/run_sse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          newMessage: {
            parts: [{ text: finalPrompt }]
          }
        })
      });

      if (!response.ok) {
        throw new Error("Failed to start stream");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop();

        for (const line of lines) {
          const cleanLine = line.trim();
          if (cleanLine.startsWith("data:")) {
            try {
              const eventData = JSON.parse(cleanLine.substring(5).trim());
              if (eventData.content && eventData.content.parts) {
                const partText = eventData.content.parts.map(p => p.text || "").join("");
                if (partText) {
                  accumulatedResponse += partText;
                  const renderedText = renderTextWithShields(accumulatedResponse);
                  chefBubbleBody.innerHTML = formatMarkdownToHTML(renderedText);
                }
              }
            } catch (e) {}
          }
        }
      }
      
      remoteLog("[Custom UI] Stream completed successfully.");
      injectGourmetBoardCard(chefBubbleBody, accumulatedResponse);
      
    } catch (err) {
      remoteLog("[Custom UI] Stream error: " + err.message);
      chefBubbleBody.innerHTML = `<span style="color:var(--accent-red);">Error: Failed to fetch recipe from server. Please try again.</span>`;
    }

    resetGenerationState();
  }

  function resetGenerationState() {
    isGenerating = false;
    sendBtn.disabled = false;
    sendBtn.innerHTML = `<span class="material-symbols-outlined">arrow_upward</span>`;
  }

  function remoteLog(msg) {
    fetch("/api/log", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg })
    }).catch(() => {});
  }

  function extractPIIDiffs(clear, masked) {
    const diffs = [];
    let i = 0;
    while (i < clear.length) {
      if (masked[i] === "#") {
        let start = i;
        while (i < masked.length && masked[i] === "#") {
          i++;
        }
        const clearSubstring = clear.substring(start, i);
        const maskedSubstring = masked.substring(start, i);
        diffs.push([clearSubstring, maskedSubstring]);
      } else {
        i++;
      }
    }
    return diffs;
  }

  function renderTextWithShields(text) {
    let output = text;
    const sortedKeys = Array.from(maskedTexts.keys()).sort((a, b) => b.length - a.length);
    
    sortedKeys.forEach(clearText => {
      const maskedText = maskedTexts.get(clearText);
      const shieldHTML = `<button type="button" class="shielded-badge" onclick="showPiiDetails(this)" data-clear="${clearText.replace(/"/g, '&quot;')}"><span class="material-symbols-outlined" style="font-size:12px;vertical-align:middle;margin-right:4px;">shield</span>Sensitive Data Shielded</button>`;
      
      output = output.replaceAll(clearText, shieldHTML);
      output = output.replaceAll(maskedText, shieldHTML);
    });
    
    return output;
  }

  function showModal(title, bodyHTML, type = "pii") {
    modalTitle.innerText = title;
    modalBody.innerHTML = bodyHTML;
    
    if (type === "security") {
      modalIcon.innerText = "gpp_maybe";
      gourmetModal.className = "gourmet-modal open type-security";
    } else {
      modalIcon.innerText = "shield";
      gourmetModal.className = "gourmet-modal open type-pii";
    }
  }

  window.closeModal = () => {
    gourmetModal.className = "gourmet-modal";
  };

  window.showPiiDetails = (element) => {
    const clearText = element.getAttribute("data-clear");
    showModal(
      "Sensitive Data Shielded",
      `<p>🔒 <strong>Sensitive Information Masked Locally</strong></p>
       <p>This item was intercepted and deidentified locally before leaving your browser to protect your privacy and prevent leaking credentials, personal identity info, or sensitive tokens to cloud logs or histories.</p>
       <p style="margin-top: 14px;"><strong>Protected Original Value:</strong></p>
       <p style="margin-top: 6px;"><code>${clearText}</code></p>
       <p style="margin-top: 14px; font-size: 13px; color: var(--text-muted);">Original values are only visible in this active session via this deidentification shield.</p>`,
      "pii"
    );
  };

  function injectGourmetBoardCard(bubbleElement, fullText) {
    const shoppingSectionStr = extractSection(fullText, ["shopping list", "grocery list", "ingredients needed to buy"], ["nutrition", "macronutrient", "calories"]);
    const nutritionSectionStr = extractSection(fullText, ["nutrition", "macronutrient", "calories"], []);

    const hasShopping = (shoppingSectionStr && parseListItems(shoppingSectionStr).length > 0);
    const hasNutrition = (nutritionSectionStr && parseNutritionMetrics(nutritionSectionStr).cal > 0);

    if (!hasShopping && !hasNutrition) return;

    const cardId = "gourmet-card-" + Date.now();
    let cardHTML = `<div class="embedded-gourmet-card" id="${cardId}">`;

    if (hasShopping) {
      const items = parseListItems(shoppingSectionStr);
      const checklistHTML = renderChecklistHTML(items);
      cardHTML += `
        <div class="gourmet-accordion" id="${cardId}-shop-acc">
          <button class="accordion-trigger" onclick="toggleAccordion('${cardId}-shop-acc')">
            <div class="trigger-title-group">
              <span class="material-symbols-outlined">shopping_cart</span>
              <span>🛒 Smart Grocery Checklist</span>
            </div>
            <span class="material-symbols-outlined accordion-icon">expand_more</span>
          </button>
          <div class="accordion-content">
            <div class="embedded-checklist-departments">
              ${checklistHTML}
            </div>
          </div>
        </div>
      `;
    }

    if (hasNutrition) {
      const metrics = parseNutritionMetrics(nutritionSectionStr);
      const pctCal = Math.min(100, (metrics.cal / 2000) * 100);
      const pctPro = Math.min(100, (metrics.pro / 120) * 100);
      const pctCarb = Math.min(100, (metrics.carb / 250) * 100);
      const pctFat = Math.min(100, (metrics.fat / 70) * 100);

      cardHTML += `
        <div class="gourmet-accordion" id="${cardId}-nutr-acc">
          <button class="accordion-trigger" onclick="toggleAccordion('${cardId}-nutr-acc')">
            <div class="trigger-title-group">
              <span class="material-symbols-outlined">bar_chart</span>
              <span>📊 Estimated Nutrition HUD</span>
            </div>
            <span class="material-symbols-outlined accordion-icon">expand_more</span>
          </button>
          <div class="accordion-content">
            <div class="embedded-nutrition-grid">
              <div class="nutrition-pill cal-pill">
                <span class="pill-name">Calories</span>
                <span class="pill-val">${metrics.cal} <span class="unit">kcal</span></span>
                <div class="pill-track"><div class="pill-bar" style="width: ${pctCal}%"></div></div>
              </div>
              <div class="nutrition-pill pro-pill">
                <span class="pill-name">Protein</span>
                <span class="pill-val">${metrics.pro} <span class="unit">g</span></span>
                <div class="pill-track"><div class="pill-bar" style="width: ${pctPro}%"></div></div>
              </div>
              <div class="nutrition-pill carb-pill">
                <span class="pill-name">Carbs</span>
                <span class="pill-val">${metrics.carb} <span class="unit">g</span></span>
                <div class="pill-track"><div class="pill-bar" style="width: ${pctCarb}%"></div></div>
              </div>
              <div class="nutrition-pill fat-pill">
                <span class="pill-name">Fat</span>
                <span class="pill-val">${metrics.fat} <span class="unit">g</span></span>
                <div class="pill-track"><div class="pill-bar" style="width: ${pctFat}%"></div></div>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    cardHTML += `</div>`;
    bubbleElement.insertAdjacentHTML("beforeend", cardHTML);
  }

  window.toggleAccordion = (accordionId) => {
    const el = document.getElementById(accordionId);
    if (!el) return;
    
    const isOpen = el.classList.contains("open");
    
    const parentCard = el.closest(".embedded-gourmet-card");
    if (parentCard) {
      const otherAccordions = parentCard.querySelectorAll(".gourmet-accordion");
      otherAccordions.forEach(acc => {
        acc.classList.remove("open");
        acc.querySelector(".accordion-content").style.maxHeight = "0px";
      });
    }

    if (!isOpen) {
      el.classList.add("open");
      const content = el.querySelector(".accordion-content");
      content.style.maxHeight = content.scrollHeight + 40 + "px";
    }
  };

  function extractSection(text, keywords, stopKeywords) {
    const lines = text.split("\n");
    let capturing = false;
    let sectionLines = [];
    
    for (let line of lines) {
      const lowerLine = line.toLowerCase();
      
      const matchesStart = keywords.some(k => lowerLine.includes(k) && (line.startsWith("#") || line.startsWith("**") || line.startsWith("###")));
      if (matchesStart) {
        capturing = true;
        sectionLines.push(line);
        continue;
      }
      
      const matchesStop = stopKeywords.some(k => lowerLine.includes(k) && (line.startsWith("#") || line.startsWith("**") || line.startsWith("###")));
      if (matchesStop && capturing) {
        break;
      }
      
      if (capturing) {
        sectionLines.push(line);
      }
    }
    
    return sectionLines.length > 0 ? sectionLines.join("\n") : "";
  }

  function parseListItems(sectionStr) {
    const lines = sectionStr.split("\n");
    const items = [];
    let currentDept = "Ingredients";
    
    for (let line of lines) {
      const trimmed = line.trim();
      
      if (trimmed.startsWith("**") && trimmed.endsWith("**")) {
        currentDept = trimmed.replace(/\*/g, "");
        continue;
      } else if (trimmed.startsWith("###") || trimmed.startsWith("####")) {
        currentDept = trimmed.replace(/#/g, "").trim();
        continue;
      }
      
      if (trimmed.startsWith("-") || trimmed.startsWith("*")) {
        const value = trimmed.substring(1).trim();
        if (value) {
          items.push({
            name: value,
            department: currentDept
          });
        }
      }
    }
    
    return items;
  }

  function parseNutritionMetrics(sectionStr) {
    const metrics = { cal: 0, pro: 0, carb: 0, fat: 0 };
    
    const calMatch = sectionStr.match(/(?:calories|cal|energy):\s*(\d+)/i);
    const proMatch = sectionStr.match(/(?:protein|pro):\s*(\d+)/i);
    const carbMatch = sectionStr.match(/(?:carbs|carbohydrates|carb):\s*(\d+)/i);
    const fatMatch = sectionStr.match(/(?:fat|fats):\s*(\d+)/i);
    
    if (calMatch) metrics.cal = parseInt(calMatch[1]);
    if (proMatch) metrics.pro = parseInt(proMatch[1]);
    if (carbMatch) metrics.carb = parseInt(carbMatch[1]);
    if (fatMatch) metrics.fat = parseInt(fatMatch[1]);
    
    return metrics;
  }

  function renderChecklistHTML(items) {
    const groups = {};
    items.forEach(item => {
      if (!groups[item.department]) {
        groups[item.department] = [];
      }
      groups[item.department].push(item);
    });
    
    let html = "";
    for (const dept in groups) {
      html += `
        <div class="checklist-dept-section">
          <h4>${dept}</h4>
          <div class="checklist-dept-group">
      `;
      
      groups[dept].forEach((item, index) => {
        const itemId = `check-${dept.replace(/\s/g, "")}-${index}-${Date.now()}`;
        html += `
          <label class="checklist-item-row" for="${itemId}">
            <input type="checkbox" id="${itemId}">
            <div class="check-circle-custom"></div>
            <span class="checklist-item-row-text">${item.name}</span>
          </label>
        `;
      });
      
      html += `
          </div>
        </div>
      `;
    }
    
    return html;
  }

  function formatMarkdownToHTML(md) {
    let html = md;
    
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    html = html.replace(/^\s*-\s*(.*$)/gim, '<li>$1</li>');
    html = html.replace(/^\s*\*\s*(.*$)/gim, '<li>$1</li>');
    
    html = html.replace(/(<li>.*<\/li>)/gms, '<ul>$1</ul>');
    
    html = html.split("\n\n").map(p => {
      if (p.trim().startsWith("<h") || p.trim().startsWith("<ul") || p.trim().startsWith("<li")) {
        return p;
      }
      return `<p>${p.replace(/\n/g, '<br>')}</p>`;
    }).join("");
    
    return html;
  }

  function appendMessage(sender, body, bodyId = "") {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", `${sender}-message`);
    
    if (sender === "system" || sender === "chef") {
      msgDiv.innerHTML = `
        <span class="material-symbols-outlined system-avatar">cooking</span>
        <div class="message-body" ${bodyId ? `id="${bodyId}"` : ""}>${body}</div>
      `;
    } else {
      msgDiv.innerHTML = `
        <div class="message-body" ${bodyId ? `id="${bodyId}"` : ""}>${body}</div>
      `;
    }
    
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }

  window.sendSuggestion = (suggestionText) => {
    chatInput.value = suggestionText;
    chatInput.style.height = "auto";
    chatInput.style.height = (chatInput.scrollHeight) + "px";
    chatForm.dispatchEvent(new Event("submit"));
  };
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeApp);
} else {
  initializeApp();
}
"""
