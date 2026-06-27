/* ==========================================================================
   ☕ Gourmet Chef - Single-Column Conversational Javascript
   ========================================================================== */

function initializeApp() {
  // DOM Elements
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const chatHistory = document.getElementById("chatHistory");
  const sendBtn = document.getElementById("sendBtn");

  // Reusable Modal Elements
  const gourmetModal = document.getElementById("gourmetModal");
  const modalTitle = document.getElementById("modalTitle");
  const modalBody = document.getElementById("modalBody");
  const modalIcon = document.getElementById("modalIcon");

  // State Management
  let isGenerating = false;
  let activeSessionId = "session-" + Math.random().toString(36).substring(2, 15); // Fallback default
  const maskedTexts = new Map();

  // Dynamic ADK Session Registration
  async function createAdkSession() {
    try {
      const res = await fetch("/apps/chef_grocery_app/users/default-user/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      if (res.ok) {
        const sessionData = await res.json();
        activeSessionId = sessionData.id;
        remoteLog("[Custom UI] Successfully registered ADK session: " + activeSessionId);
      } else {
        remoteLog("[Custom UI] Session registration failed, using fallback ID: " + activeSessionId);
      }
    } catch (err) {
      remoteLog("[Custom UI] Error registering session, using fallback: " + err.message);
    }
  }

  // 1. Safe, Bulletproof Custom Regex Compilation
  let MASK_REGEX = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|\b(?:[01]?[0-9]|2[0-3]):[0-5][0-9](?::[0-5][0-9])?(?:\s*[aApP][mM])?\b|\b(?:[01]?[0-9]|2[0-3])\s*[aApP][mM]\b/g; // Safe default (emails & time)
  
  try {
    const rawPattern = window.MASK_REGEX_STR;
    if (rawPattern && typeof rawPattern === "string") {
      // Safely strip python-specific flags like (?i) which crash JS engines
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

  // 2. Chat Form Submission
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (isGenerating) return;
    
    const prompt = chatInput.value.trim();
    if (!prompt) return;

    chatInput.value = "";
    chatInput.style.height = "auto";
    
    await processAndSendPrompt(prompt);
  });

  // Handle Enter key for submit (and Shift+Enter for newline)
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event("submit"));
    }
  });

  // Textarea Auto-grow
  chatInput.addEventListener("input", function() {
    this.style.height = "auto";
    this.style.height = (this.scrollHeight) + "px";
  });

  // 3. Process and Send Prompt
  async function processAndSendPrompt(rawPrompt) {
    isGenerating = true;
    sendBtn.disabled = true;
    sendBtn.innerHTML = `<span class="loader-spinner"></span>`;
    
    // A. Optimistic Client-Side Masking
    let localMatches = [];
    try {
      localMatches = rawPrompt.match(MASK_REGEX) || [];
      localMatches.forEach(match => {
        maskedTexts.set(match, "[redacted]");
      });
      remoteLog("[Custom UI] Optimistic masking matches: " + JSON.stringify(localMatches));
    } catch (e) {
      console.warn("Error during optimistic masking:", e);
    }

    // Render the user's message bubble with nice shielded formatting and a unique ID
    const userBubbleId = "user-bubble-" + Date.now();
    const userMessageBody = renderTextWithShields(rawPrompt);
    appendMessage("user", userMessageBody, userBubbleId);

    // B. Synchronous Backend Evaluation
    let finalPrompt = rawPrompt;
    let shouldBlock = false;
    try {
      const evalRes = await fetch("/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: rawPrompt })
      });
      
      if (evalRes.ok) {
        const evalData = await evalRes.json();
        remoteLog("[Custom UI] /evaluate result: " + JSON.stringify(evalData));
        
        // 1. ALWAYS extract backend PII diffs and update the user's bubble in the DOM first
        if (evalData.matches && evalData.matches.length > 0) {
          evalData.matches.forEach(m => {
            maskedTexts.set(m.clear, m.masked);
          });
          if (evalData.deidentified_text) finalPrompt = evalData.deidentified_text;
          const userBubbleEl = document.getElementById(userBubbleId);
          if (userBubbleEl) {
            userBubbleEl.innerHTML = renderTextWithShields(rawPrompt);
            remoteLog("[Custom UI] Dynamically updated user bubble with backend PII shields.");
          }
          shouldBlock = true;
        } else if (evalData.deidentified_text) {
          finalPrompt = evalData.deidentified_text;
          const backendMatches = extractPIIDiffs(rawPrompt, finalPrompt);
          backendMatches.forEach(([clearText, maskedText]) => {
            maskedTexts.set(clearText, maskedText);
          });
          
          // Re-render and dynamically update the user's chat bubble with the complete set of shields!
          const userBubbleEl = document.getElementById(userBubbleId);
          if (userBubbleEl) {
            userBubbleEl.innerHTML = renderTextWithShields(rawPrompt);
            remoteLog("[Custom UI] Dynamically updated user bubble with backend PII shields.");
          }
          shouldBlock = true;
        }
        
        // 2. Handle active security blocks
        if (evalData.block) {
          shouldBlock = true;
        }
      }
    } catch (err) {
      console.warn("Failed to contact /evaluate endpoint, falling back to client-side masking", err);
    }

    if (shouldBlock || (localMatches && localMatches.length > 0)) {
      appendMessage("system", `<span style="color:var(--accent-red); font-weight:600;">[Security Alert] Your request was blocked by security filters.</span>`);
      resetGenerationState();
      return;
    }

    // C. Initialize Multi-Agent Stream State
    let currentAgent = null;
    let activeBubbleId = null;
    let activeBubbleBody = null;
    let accumulatedResponse = "";

    try {
      const response = await fetch("/run_sse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          app_name: "chef_grocery_app",
          user_id: "default-user",
          session_id: activeSessionId,
          new_message: {
            role: "user",
            parts: [{ text: finalPrompt }]
          },
          streaming: true
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
              
              // Extract the agent name (defaulting to chef_agent)
              const author = eventData.author || "chef_agent";
              
              if (eventData.content && eventData.content.parts) {
                const partText = eventData.content.parts.map(p => p.text || "").join("");
                if (partText) {
                  // If the agent has switched, or if this is the first chunk:
                  if (author !== currentAgent) {
                    currentAgent = author;
                    accumulatedResponse = ""; // Reset accumulator for the new agent
                    activeBubbleId = "active-agent-" + author + "-" + Date.now();
                    
                    let loadingText = author === "grocery_agent" ? "Planning your grocery checklist..." : "Whipping up your recipe...";
                    appendMessage("chef", `<div class="loader-spinner" style="display:inline-block;vertical-align:middle;margin-right:8px;width:16px;height:16px;border-width:2px;"></div>${loadingText}`, activeBubbleId, author);
                    activeBubbleBody = document.getElementById(activeBubbleId);
                  }
                  
                  accumulatedResponse += partText;
                  const renderedText = renderTextWithShields(accumulatedResponse, false);
                  activeBubbleBody.innerHTML = formatMarkdownToHTML(renderedText);
                }
              }
            } catch (e) {}
          }
        }
      }
      
      remoteLog("[Custom UI] Stream completed successfully.");
      
      // D. Stream Completed: Inject rich, interactive board directly inside the last active agent's bubble!
      if (activeBubbleBody) {
        injectGourmetBoardCard(activeBubbleBody, accumulatedResponse);
      }
      
    } catch (err) {
      remoteLog("[Custom UI] Stream error: " + err.message);
      if (activeBubbleBody) {
        activeBubbleBody.innerHTML = `<span style="color:var(--accent-red);">Error: Failed to fetch recipe from server. Please try again.</span>`;
      } else {
        appendMessage("chef", `<span style="color:var(--accent-red);">Error: Failed to fetch recipe from server. Please try again.</span>`);
      }
    }

    resetGenerationState();
  }

  // 4. Reset UI States
  function resetGenerationState() {
    isGenerating = false;
    sendBtn.disabled = false;
    sendBtn.innerHTML = `<span class="material-symbols-outlined">arrow_upward</span>`;
  }

  // 5. Remote logging
  function remoteLog(msg) {
    fetch("/api/log", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg })
    }).catch(() => {});
  }

  // 6. Extract PII diffs
  function extractPIIDiffs(clear, masked) {
    if (!clear || !masked || clear.length !== masked.length) {
      console.warn("[Custom UI] extractPIIDiffs length mismatch or null:", clear, masked);
      return [];
    }
    const diffs = [];
    let i = 0;
    const len = clear.length;
    while (i < len) {
      if (masked[i] === "#") {
        let start = i;
        while (i < len && masked[i] === "#") {
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

  // 7. Render text with interactive secure shields (Robust Two-Pass Placeholder Compiler Pattern)
  function renderTextWithShields(text, replaceMaskedHashes = true) {
    let output = text;
    const sortedKeys = Array.from(maskedTexts.keys()).sort((a, b) => b.length - a.length);
    
    const placeholders = new Map();
    
    // Step 1: Replace all PII occurrences with safe placeholder tokens (prevents nested HTML corruption)
    sortedKeys.forEach((clearText, index) => {
      const maskedText = maskedTexts.get(clearText);
      const placeholder = `__GOURMET_SHIELD_TOKEN_${index}__`;
      placeholders.set(placeholder, clearText);
      
      output = output.replaceAll(clearText, placeholder);
      if (replaceMaskedHashes && maskedText) {
        output = output.replaceAll(maskedText, placeholder);
      }
    });
    
    // Step 2: Replace all placeholders with the beautiful interactive shield buttons
    placeholders.forEach((clearText, placeholder) => {
      const maskedVal = maskedTexts.get(clearText) || "[redacted]";
      const shieldHTML = `<button type="button" class="shielded-badge" onclick="showPiiDetails(this)" data-clear="${clearText.replace(/"/g, '&quot;')}"><span class="material-symbols-outlined" style="font-size:12px;vertical-align:middle;margin-right:4px;">shield</span>${maskedVal}</button>`;
      output = output.replaceAll(placeholder, shieldHTML);
    });
    
    return output;
  }

  // 8. Reusable Dialog Modal Control
  function showModal(title, bodyHTML, type = "pii") {
    modalTitle.innerText = title;
    modalBody.innerHTML = bodyHTML;
    
    // Set icon and style based on type
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

  // Clickable PII detail modal triggers
  window.showPiiDetails = (element) => {
    const clearText = element.getAttribute("data-clear");
    const maskedVal = maskedTexts.get(clearText) || "###";
    showModal(
      maskedVal,
      `<p>🔒 <strong>Sensitive Information Masked Locally</strong></p>
       <p>This item was intercepted and deidentified locally before leaving your browser to protect your privacy and prevent leaking credentials, personal identity info, or sensitive tokens to cloud logs or histories.</p>
       <p style="margin-top: 14px;"><strong>Protected Original Value:</strong></p>
       <p style="margin-top: 6px;"><code>${clearText}</code></p>
       <p style="margin-top: 14px; font-size: 13px; color: var(--text-muted);">Original values are only visible in this active session via this deidentification shield.</p>`,
      "pii"
    );
  };

  // 9. Inject Gourmet Accordion Card inside active Chat Bubble
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

  // Render checklist grouped by department
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

  function appendMessage(sender, body, bodyId = "", agentType = "chef_agent") {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", `${sender}-message`);
    
    if (sender === "system" || sender === "chef") {
      let icon = "cooking";
      let avatarClass = "system-avatar";
      
      if (sender === "system") {
        icon = "gpp_maybe";
        avatarClass = "system-avatar security-avatar";
      } else if (agentType === "grocery_agent") {
        icon = "shopping_cart";
        avatarClass = "system-avatar grocery-avatar";
      } else if (agentType === "chef_agent") {
        icon = "cooking";
        avatarClass = "system-avatar chef-avatar";
      }
      
      msgDiv.innerHTML = `
        <span class="material-symbols-outlined ${avatarClass}">${icon}</span>
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

  // Trigger Session Registration on Startup
  createAdkSession();
}

// 11. Bulletproof DOM Ready Execution to Prevent Race Conditions!
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeApp);
} else {
  initializeApp();
}
