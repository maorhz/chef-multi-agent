/* ==========================================================================
   ☕ Gourmet Chef & Grocery Assistant - Frontend Application Logic
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const chatHistory = document.getElementById("chatHistory");
  const sendBtn = document.getElementById("sendBtn");
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".board-tab-content");
  const boardLoading = document.getElementById("boardLoading");
  const boardEmpty = document.getElementById("boardEmpty");
  
  // Recipe, Checklist, and Nutrition Elements
  const recipeArticle = document.getElementById("recipeArticle");
  const checklistDepartments = document.getElementById("checklistDepartments");
  const nutrCal = document.getElementById("nutrCal");
  const nutrPro = document.getElementById("nutrPro");
  const nutrCarb = document.getElementById("nutrCarb");
  const nutrFat = document.getElementById("nutrFat");
  const barCal = document.getElementById("barCal");
  const barPro = document.getElementById("barPro");
  const barCarb = document.getElementById("barCarb");
  const barFat = document.getElementById("barFat");

  // State Management
  let isGenerating = false;
  let activeSessionId = "session-" + Math.random().toString(36).substring(2, 15);
  const maskedTexts = new Map();

  // Load the MASK_REGEX injected from backend or window
  const MASK_REGEX = window.MASK_REGEX || /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;

  // Log connection to backend
  remoteLog("[Custom UI] Application initialized. Session ID: " + activeSessionId);

  // 1. Tab Navigation Logic
  tabButtons.forEach(button => {
    button.addEventListener("click", () => {
      const targetTabId = button.getAttribute("data-tab");
      
      tabButtons.forEach(btn => btn.classList.remove("active"));
      tabContents.forEach(content => content.classList.remove("active"));
      
      button.classList.add("active");
      document.getElementById(targetTabId).classList.add("active");
    });
  });

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
    sendBtn.innerHTML = `<span class="material-symbols-outlined loader-spinner" style="width:20px;height:20px;border-width:2px;"></span>`;
    
    // Show Loading state on the Gourmet Board
    boardEmpty.style.display = "none";
    boardLoading.style.display = "flex";

    // A. Optimistic Client-Side Masking
    // Scan for regex matches (e.g. emails, cards, addresses)
    const localMatches = rawPrompt.match(MASK_REGEX) || [];
    localMatches.forEach(match => {
      const masked = "#".repeat(match.length);
      maskedTexts.set(match, masked);
    });

    remoteLog("[Custom UI] Client optimistic matches: " + JSON.stringify(localMatches));

    // Render the user's message bubble with nice shielded formatting
    const userMessageBody = renderTextWithShields(rawPrompt);
    appendMessage("user", userMessageBody);

    // B. Synchronous Backend Evaluation
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
          appendMessage("system", `<span style="color:var(--accent-red); font-weight:600;">[Security Alert] Your request was blocked by security filters.</span>`);
          resetGenerationState();
          return;
        }
        
        if (evalData.deidentified_text) {
          finalPrompt = evalData.deidentified_text;
          // Synchronize our maskedText mappings
          const backendMatches = extractPIIDiffs(rawPrompt, finalPrompt);
          backendMatches.forEach(([clearText, maskedText]) => {
            maskedTexts.set(clearText, maskedText);
          });
        }
      }
    } catch (err) {
      console.warn("Failed to contact /evaluate endpoint, falling back to client-side masking", err);
    }

    // C. Dispatch Streaming SSE Request
    appendMessage("system", "", "activeChefBubble");
    const chefBubbleBody = document.getElementById("activeChefBubble");
    chefBubbleBody.innerHTML = `<div class="loader-spinner" style="width:20px;height:20px;border-width:2px;display:inline-block;vertical-align:middle;margin-right:8px;"></div>Thinking...`;

    let accumulatedResponse = "";
    let activeAuthor = "";

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
        throw new Error("Failed to start SSE stream");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop(); // Keep partial line in buffer

        for (const line of lines) {
          const cleanLine = line.trim();
          if (cleanLine.startsWith("data:")) {
            try {
              const eventData = JSON.parse(cleanLine.substring(5).trim());
              
              // Inspect event object
              if (eventData.content && eventData.content.parts) {
                const partText = eventData.content.parts.map(p => p.text || "").join("");
                
                if (partText) {
                  // Check if author changed (e.g. from chef_agent to grocery_agent)
                  if (eventData.author && eventData.author !== activeAuthor) {
                    activeAuthor = eventData.author;
                    remoteLog("[Custom UI] Active agent changed to: " + activeAuthor);
                  }

                  accumulatedResponse += partText;
                  
                  // Live-render response in chat bubble with dynamic masking
                  const renderedText = renderTextWithShields(accumulatedResponse);
                  chefBubbleBody.innerHTML = formatMarkdownToHTML(renderedText);
                  
                  // Live-parse the Gourmet Board items
                  parseAndPopulateGourmetBoard(accumulatedResponse);
                }
              }
            } catch (e) {
              // Ignore partial JSON parse errors
            }
          }
        }
      }
      
      remoteLog("[Custom UI] Stream completed successfully.");
      
    } catch (err) {
      remoteLog("[Custom UI] Stream error: " + err.message);
      chefBubbleBody.innerHTML = `<span style="color:var(--accent-red);">Error: Failed to fetch recipe from server. Please try again.</span>`;
    }

    // Finalize UI states
    resetGenerationState();
  }

  // 4. Reset Generation UI states
  function resetGenerationState() {
    isGenerating = false;
    sendBtn.disabled = false;
    sendBtn.innerHTML = `<span class="material-symbols-outlined">arrow_upward</span>`;
    boardLoading.style.display = "none";
    
    // If no recipe was parsed, show empty state
    if (!recipeArticle.innerHTML.trim()) {
      boardEmpty.style.display = "flex";
    }
  }

  // 5. Utility: Remote Logging to Backend
  function remoteLog(msg) {
    fetch("/api/log", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg })
    }).catch(() => {});
  }

  // 6. Utility: Extract PII diffs between clear text and masked text
  function extractPIIDiffs(clear, masked) {
    // Basic diff helper that maps masked hashes back to original clear texts
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

  // 7. Utility: Render text with interactive secure shields
  function renderTextWithShields(text) {
    let output = text;
    // Sort keys by descending length to prevent partial matches
    const sortedKeys = Array.from(maskedTexts.keys()).sort((a, b) => b.length - a.length);
    
    sortedKeys.forEach(clearText => {
      const maskedText = maskedTexts.get(clearText);
      const shieldHTML = `<span class="shielded-badge" title="PII masked locally to prevent leaks. Clear: ${clearText.replace(/"/g, '&quot;')}"><span class="material-symbols-outlined" style="font-size:14px;vertical-align:middle;margin-right:4px;">shield</span>Sensitive Data Shielded</span>`;
      
      // Replace either clear text or raw hash matches with our gorgeous badge
      output = output.replaceAll(clearText, shieldHTML);
      output = output.replaceAll(maskedText, shieldHTML);
    });
    
    return output;
  }

  // 8. Parser: Dynamic Gourmet Board Populator (Recipe, Checklist, HUD)
  function parseAndPopulateGourmetBoard(text) {
    // Split the text into sections
    const recipeSectionStr = extractSection(text, ["recipe", "ingredients", "instructions"], ["shopping list", "grocery list", "nutrition"]);
    const shoppingSectionStr = extractSection(text, ["shopping list", "grocery list", "ingredients needed to buy"], ["nutrition", "macronutrient", "calories"]);
    const nutritionSectionStr = extractSection(text, ["nutrition", "macronutrient", "calories"], []);

    // A. Populate Recipe Tab
    if (recipeSectionStr) {
      recipeArticle.innerHTML = formatMarkdownToHTML(recipeSectionStr);
    }

    // B. Populate Shopping Checklist Tab
    if (shoppingSectionStr) {
      const items = parseListItems(shoppingSectionStr);
      if (items.length > 0) {
        checklistDepartments.innerHTML = renderChecklistHTML(items);
      }
    }

    // C. Populate Nutrition HUD Tab
    if (nutritionSectionStr) {
      const metrics = parseNutritionMetrics(nutritionSectionStr);
      updateNutritionHUD(metrics);
    }
  }

  // Helper to extract a markdown section based on keyword boundaries
  function extractSection(text, keywords, stopKeywords) {
    const lines = text.split("\n");
    let capturing = false;
    let sectionLines = [];
    
    for (let line of lines) {
      const lowerLine = line.toLowerCase();
      
      // Check for start boundary
      const matchesStart = keywords.some(k => lowerLine.includes(k) && (line.startsWith("#") || line.startsWith("**")));
      if (matchesStart) {
        capturing = true;
        sectionLines.push(line);
        continue;
      }
      
      // Check for stop boundary
      const matchesStop = stopKeywords.some(k => lowerLine.includes(k) && (line.startsWith("#") || line.startsWith("**")));
      if (matchesStop && capturing) {
        break;
      }
      
      if (capturing) {
        sectionLines.push(line);
      }
    }
    
    return sectionLines.length > 0 ? sectionLines.join("\n") : text;
  }

  // Helper to parse bullet list items from shopping list
  function parseListItems(sectionStr) {
    const lines = sectionStr.split("\n");
    const items = [];
    let currentDept = "Other";
    
    for (let line of lines) {
      const trimmed = line.trim();
      
      // Check for department headers e.g. "**Produce**" or "### Meat"
      if (trimmed.startsWith("**") && trimmed.endsWith("**")) {
        currentDept = trimmed.replace(/\*/g, "");
        continue;
      } else if (trimmed.startsWith("###") || trimmed.startsWith("####")) {
        currentDept = trimmed.replace(/#/g, "").trim();
        continue;
      }
      
      // Match bullet items
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

  // Helper to parse nutrition values using regex
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

  // Render checkable grocery checklist grouped by department
  function renderChecklistHTML(items) {
    // Group by department
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
        <div class="department-section">
          <h4>${dept}</h4>
          <div class="checklist-group">
      `;
      
      groups[dept].forEach((item, index) => {
        const itemId = `check-${dept.replace(/\s/g, "")}-${index}`;
        html += `
          <label class="checklist-item" for="${itemId}">
            <input type="checkbox" id="${itemId}">
            <div class="check-box-custom"></div>
            <span class="checklist-item-text">${item.name}</span>
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

  // Update HUD values and animate progress bars
  function updateNutritionHUD(metrics) {
    nutrCal.innerHTML = `${metrics.cal} <span class="unit">kcal</span>`;
    nutrPro.innerHTML = `${metrics.pro} <span class="unit">g</span>`;
    nutrCarb.innerHTML = `${metrics.carb} <span class="unit">g</span>`;
    nutrFat.innerHTML = `${metrics.fat} <span class="unit">g</span>`;
    
    // Scale percentages out of daily/macro benchmarks
    const pctCal = Math.min(100, (metrics.cal / 2000) * 100);
    const pctPro = Math.min(100, (metrics.pro / 120) * 100);
    const pctCarb = Math.min(100, (metrics.carb / 250) * 100);
    const pctFat = Math.min(100, (metrics.fat / 70) * 100);
    
    barCal.style.width = `${pctCal}%`;
    barPro.style.width = `${pctPro}%`;
    barCarb.style.width = `${pctCarb}%`;
    barFat.style.width = `${pctFat}%`;
  }

  // Markdown to basic HTML renderer
  function formatMarkdownToHTML(md) {
    let html = md;
    
    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    // Bold / Italics
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Lists
    html = html.replace(/^\s*-\s*(.*$)/gim, '<li>$1</li>');
    html = html.replace(/^\s*\*\s*(.*$)/gim, '<li>$1</li>');
    
    // Wrap lists in ul
    // A simple hacky regex that wraps consecutive <li> blocks in <ul>
    html = html.replace(/(<li>.*<\/li>)/gms, '<ul>$1</ul>');
    
    // Paragraphs / Newlines
    html = html.split("\n\n").map(p => {
      if (p.trim().startsWith("<h") || p.trim().startsWith("<ul") || p.trim().startsWith("<li")) {
        return p;
      }
      return `<p>${p.replace(/\n/g, '<br>')}</p>`;
    }).join("");
    
    return html;
  }

  // 9. Append chat messages to history pane
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

  // 10. Globals for Suggestion Pills & Reset
  window.sendSuggestion = (suggestionText) => {
    chatInput.value = suggestionText;
    chatInput.style.height = "auto";
    chatInput.style.height = (chatInput.scrollHeight) + "px";
    chatForm.dispatchEvent(new Event("submit"));
  };

  window.resetChecklist = () => {
    const checkboxes = checklistDepartments.querySelectorAll("input[type='checkbox']");
    checkboxes.forEach(cb => cb.checked = false);
  };
});
