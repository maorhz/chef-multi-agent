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
  <!-- Custom Stylesheet -->
  <link rel="stylesheet" href="/static/styles.css">
  
  <!-- Injected Regex Placeholder -->
  <script>
    window.MASK_REGEX = MASK_REGEX_PLACEHOLDER;
  </script>
</head>
<body>
  <div class="app-container">
    <!-- Header -->
    <header class="app-header">
      <div class="header-logo">
        <span class="material-symbols-outlined logo-icon">restaurant</span>
        <h1>Gourmet Chef <span class="accent">&amp;</span> Grocery Assistant</h1>
      </div>
      <div class="security-status">
        <span class="material-symbols-outlined security-icon">shield</span>
        <span class="security-text">Active SDP Prompt Shield</span>
      </div>
    </header>

    <!-- Main Content Grid -->
    <main class="app-main">
      <!-- Left Column: Culinary Chat -->
      <section class="chat-column">
        <div class="panel-header">
          <span class="material-symbols-outlined">chat_bubble</span>
          <h2>Culinary Consultation</h2>
        </div>
        
        <!-- Chat History -->
        <div class="chat-history" id="chatHistory">
          <div class="message system-message">
            <span class="material-symbols-outlined system-avatar">cooking</span>
            <div class="message-body">
              <p>Welcome to your digital kitchen! Tell me what you're craving, what ingredients you want to use, or any dietary restrictions, and I'll whip up a gourmet recipe and a smart shopping list for you.</p>
              <div class="suggestion-pills">
                <button class="pill-btn" onclick="sendSuggestion('I want a high-protein keto dinner using chicken breasts')">🍗 High-Protein Keto Dinner</button>
                <button class="pill-btn" onclick="sendSuggestion('Show me a quick 15-minute vegan pasta recipe')">🌱 15-Min Vegan Pasta</button>
                <button class="pill-btn" onclick="sendSuggestion('Suggest a gluten-free salmon dinner with avocado')">🥑 Gluten-Free Salmon</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Chat Input Form -->
        <form class="chat-input-container" id="chatForm">
          <textarea 
            class="chat-textarea" 
            id="chatInput" 
            placeholder="Type a craving, ingredients, or cooking questions..."
            rows="2"
            required
          ></textarea>
          <button type="submit" class="send-btn" id="sendBtn">
            <span class="material-symbols-outlined">arrow_upward</span>
          </button>
        </form>
      </section>

      <!-- Right Column: The Gourmet Board -->
      <section class="board-column">
        <div class="panel-header board-header">
          <span class="material-symbols-outlined">dashboard</span>
          <h2>The Gourmet Board</h2>
          <div class="board-tabs">
            <button class="tab-btn active" data-tab="recipeTab">Recipe</button>
            <button class="tab-btn" data-tab="shoppingTab">Shopping List</button>
            <button class="tab-btn" data-tab="nutritionTab">Nutrition HUD</button>
          </div>
        </div>

        <!-- Board Body -->
        <div class="board-body">
          <!-- Loading Overlay -->
          <div class="board-loading" id="boardLoading">
            <div class="loader-spinner"></div>
            <p>Curating your personalized culinary board...</p>
          </div>

          <!-- Empty State -->
          <div class="board-empty" id="boardEmpty">
            <span class="material-symbols-outlined empty-icon">menu_book</span>
            <h3>No Active Board</h3>
            <p>Consult with the chef on the left to generate a customized recipe, shopping checklist, and nutritional dashboard.</p>
          </div>

          <!-- Tab 1: Recipe Display -->
          <div class="board-tab-content active" id="recipeTab">
            <article class="recipe-article" id="recipeArticle">
              <!-- Dynamically populated -->
            </article>
          </div>

          <!-- Tab 2: Shopping Checklist -->
          <div class="board-tab-content" id="shoppingTab">
            <div class="shopping-checklist-container">
              <div class="checklist-header">
                <h3>🛒 Smart Department Checklist</h3>
                <button class="clear-selection-btn" onclick="resetChecklist()">Reset List</button>
              </div>
              <div class="checklist-departments" id="checklistDepartments">
                <!-- Dynamically populated -->
              </div>
            </div>
          </div>

          <!-- Tab 3: Nutrition HUD -->
          <div class="board-tab-content" id="nutritionTab">
            <div class="nutrition-hud-container">
              <h3>📊 Macronutrient Breakdown</h3>
              <div class="nutrition-grid">
                <!-- Circular Indicators / Bars -->
                <div class="nutrition-card cal-card">
                  <div class="card-title">Calories</div>
                  <div class="card-value" id="nutrCal">0 <span class="unit">kcal</span></div>
                  <div class="progress-track"><div class="progress-bar" id="barCal" style="width: 0%"></div></div>
                </div>
                <div class="nutrition-card pro-card">
                  <div class="card-title">Protein</div>
                  <div class="card-value" id="nutrPro">0 <span class="unit">g</span></div>
                  <div class="progress-track"><div class="progress-bar" id="barPro" style="width: 0%"></div></div>
                </div>
                <div class="nutrition-card carb-card">
                  <div class="card-title">Carbs</div>
                  <div class="card-value" id="nutrCarb">0 <span class="unit">g</span></div>
                  <div class="progress-track"><div class="progress-bar" id="barCarb" style="width: 0%"></div></div>
                </div>
                <div class="nutrition-card fat-card">
                  <div class="card-title">Fat</div>
                  <div class="card-value" id="nutrFat">0 <span class="unit">g</span></div>
                  <div class="progress-track"><div class="progress-bar" id="barFat" style="width: 0%"></div></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>

  <!-- Custom Javascript -->
  <script src="/static/app.js"></script>
</body>
</html>"""

CSS_CONTENT = """/* ==========================================================================
   🎨 Gourmet Theme CSS & Glassmorphism Design System
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
  overflow: hidden;
  -webkit-font-smoothing: antialiased;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Outfit', sans-serif;
  font-weight: 600;
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 16px 24px;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px 24px;
  background: var(--bg-panel);
  border: 1px solid var(--border-glass);
  backdrop-filter: blur(12px);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-main);
}

.header-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  color: var(--accent-gold);
  font-size: 28px;
}

.app-header h1 {
  font-size: 20px;
  letter-spacing: -0.5px;
}

.app-header h1 .accent {
  color: var(--accent-gold);
}

.security-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: rgba(76, 175, 80, 0.1);
  border: 1px solid rgba(76, 175, 80, 0.25);
  border-radius: 20px;
}

.security-icon {
  color: var(--accent-green);
  font-size: 16px;
}

.security-text {
  font-size: 11px;
  font-weight: 500;
  color: var(--accent-green);
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.app-main {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 20px;
  flex: 1;
  min-height: 0;
  margin-bottom: 8px;
}

.chat-column, .board-column {
  display: flex;
  flex-direction: column;
  background: var(--bg-panel);
  border: 1px solid var(--border-glass);
  backdrop-filter: blur(16px);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-main);
  min-height: 0;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 24px;
  border-bottom: 1px solid var(--border-glass);
}

.panel-header h2 {
  font-size: 18px;
  font-weight: 500;
}

.panel-header span {
  color: var(--accent-gold);
  font-size: 20px;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  gap: 14px;
  max-width: 85%;
  animation: messageFadeIn 0.3s ease-out forwards;
}

@keyframes messageFadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.message.system-message {
  align-self: flex-start;
  max-width: 100%;
}

.message.user-message {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.system-avatar {
  background: rgba(241, 168, 10, 0.1);
  color: var(--accent-gold);
  border: 1px solid rgba(241, 168, 10, 0.2);
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 20px;
}

.message-body {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-glass);
  padding: 14px 18px;
  border-radius: var(--radius-md);
  font-size: 14px;
  line-height: 1.5;
  color: var(--text-primary);
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
  margin-top: 14px;
}

.pill-btn {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-glass);
  color: var(--text-secondary);
  padding: 10px 16px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 13px;
  text-align: left;
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  transition: var(--transition-smooth);
}

.pill-btn:hover {
  background: rgba(241, 168, 10, 0.08);
  border-color: rgba(241, 168, 10, 0.3);
  color: var(--accent-gold);
  transform: translateX(4px);
}

.chat-input-container {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--border-glass);
  background: rgba(0, 0, 0, 0.15);
  align-items: flex-end;
}

.chat-textarea {
  flex: 1;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.4;
  font-family: 'Inter', sans-serif;
  resize: none;
  outline: none;
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

.send-btn:active {
  transform: translateY(0);
}

.shielded-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(244, 67, 54, 0.12);
  border: 1px solid rgba(244, 67, 54, 0.25);
  color: #ff7961;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: help;
  position: relative;
  transition: var(--transition-smooth);
}

.shielded-badge:hover {
  background: rgba(244, 67, 54, 0.2);
  border-color: rgba(244, 67, 54, 0.4);
}

.board-header {
  justify-content: space-between;
  align-items: center;
}

.board-tabs {
  display: flex;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-glass);
  padding: 4px;
  border-radius: var(--radius-md);
  gap: 4px;
}

.tab-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  padding: 8px 18px;
  font-family: 'Outfit', sans-serif;
  font-size: 14px;
  font-weight: 500;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition-smooth);
}

.tab-btn:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.03);
}

.tab-btn.active {
  color: #000;
  background: var(--accent-gold);
}

.board-body {
  flex: 1;
  position: relative;
  min-height: 0;
  overflow-y: auto;
  padding: 30px;
}

.board-loading {
  position: absolute;
  inset: 0;
  background: var(--bg-app);
  display: none;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  z-index: 10;
  backdrop-filter: blur(8px);
}

.loader-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--border-glass);
  border-top-color: var(--accent-gold);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.board-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  height: 100%;
  color: var(--text-secondary);
  padding: 40px;
}

.empty-icon {
  font-size: 64px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.board-empty h3 {
  font-size: 20px;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.board-empty p {
  font-size: 14px;
  max-width: 360px;
  line-height: 1.5;
  color: var(--text-secondary);
}

.board-tab-content {
  display: none;
  height: 100%;
}

.board-tab-content.active {
  display: block;
}

.recipe-article {
  animation: tabFadeIn 0.3s ease-out forwards;
}

@keyframes tabFadeIn {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}

.recipe-header {
  border-bottom: 1px solid var(--border-glass);
  padding-bottom: 20px;
  margin-bottom: 24px;
}

.recipe-title {
  font-size: 28px;
  color: var(--text-primary);
  margin-bottom: 12px;
  line-height: 1.2;
}

.recipe-meta-grid {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-glass);
  padding: 6px 12px;
  border-radius: 20px;
}

.meta-item span {
  font-size: 16px;
  color: var(--accent-gold);
}

.recipe-section {
  margin-bottom: 30px;
}

.recipe-section h3 {
  font-size: 18px;
  color: var(--accent-gold);
  margin-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  padding-bottom: 8px;
}

.ingredients-list {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
}

.ingredients-list li {
  font-size: 14px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 10px;
}

.ingredients-list li::before {
  content: "•";
  color: var(--accent-gold);
  font-size: 18px;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.step-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-glass);
  padding: 18px 22px;
  border-radius: var(--radius-md);
  display: flex;
  gap: 16px;
  transition: var(--transition-smooth);
}

.step-card:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: var(--border-glass-hover);
}

.step-num {
  background: rgba(241, 168, 10, 0.1);
  color: var(--accent-gold);
  border: 1px solid rgba(241, 168, 10, 0.2);
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Outfit', sans-serif;
  font-weight: 600;
  font-size: 13px;
  flex-shrink: 0;
}

.step-text {
  font-size: 14px;
  line-height: 1.5;
  color: var(--text-secondary);
}

.shopping-checklist-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  animation: tabFadeIn 0.3s ease-out forwards;
}

.checklist-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-glass);
  padding-bottom: 14px;
}

.checklist-header h3 {
  font-size: 18px;
}

.clear-selection-btn {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 12px;
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  transition: var(--transition-smooth);
}

.clear-selection-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
  border-color: rgba(255, 255, 255, 0.2);
}

.checklist-departments {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.department-section h4 {
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--accent-gold);
  margin-bottom: 12px;
}

.checklist-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.checklist-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.01);
  border: 1px solid var(--border-glass);
  padding: 12px 18px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition-smooth);
}

.checklist-item:hover {
  background: rgba(255, 255, 255, 0.03);
  border-color: var(--border-glass-hover);
}

.checklist-item input {
  display: none;
}

.check-box-custom {
  width: 20px;
  height: 20px;
  border: 2px solid var(--text-muted);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: var(--transition-smooth);
}

.check-box-custom::after {
  content: "check";
  font-family: 'Material Symbols Outlined';
  font-size: 14px;
  color: #000;
  display: none;
}

.checklist-item input:checked + .check-box-custom {
  background: var(--accent-green);
  border-color: var(--accent-green);
}

.checklist-item input:checked + .check-box-custom::after {
  display: block;
}

.checklist-item-text {
  font-size: 14px;
  color: var(--text-primary);
  transition: var(--transition-smooth);
}

.checklist-item input:checked ~ .checklist-item-text {
  text-decoration: line-through;
  color: var(--text-muted);
}

.nutrition-hud-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  animation: tabFadeIn 0.3s ease-out forwards;
}

.nutrition-hud-container h3 {
  font-size: 18px;
  border-bottom: 1px solid var(--border-glass);
  padding-bottom: 14px;
}

.nutrition-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.nutrition-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-glass);
  padding: 24px;
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
  overflow: hidden;
}

.nutrition-card::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
}

.cal-card::before { background: var(--accent-gold); }
.pro-card::before { background: #2196f3; }
.carb-card::before { background: #e91e63; }
.fat-card::before { background: #9c27b0; }

.nutrition-card .card-title {
  font-size: 13px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.nutrition-card .card-value {
  font-size: 32px;
  font-family: 'Outfit', sans-serif;
  font-weight: 700;
  color: var(--text-primary);
}

.nutrition-card .card-value .unit {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
}

.progress-track {
  background: rgba(255, 255, 255, 0.04);
  height: 6px;
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
}

.cal-card .progress-bar { background: var(--accent-gold); }
.pro-card .progress-bar { background: #2196f3; }
.carb-card .progress-bar { background: #e91e63; }
.fat-card .progress-bar { background: #9c27b0; }

@media (max-width: 960px) {
  .app-main {
    grid-template-columns: 1fr;
    overflow-y: auto;
  }
  .app-container {
    padding: 10px;
    height: auto;
    overflow: auto;
  }
  body {
    overflow: auto;
    height: auto;
  }
  .chat-column {
    height: 500px;
  }
  .board-column {
    height: 600px;
  }
}"""

JS_CONTENT = """/* ==========================================================================
   ☕ Gourmet Chef & Grocery Assistant - Frontend Application Logic
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const chatHistory = document.getElementById("chatHistory");
  const sendBtn = document.getElementById("sendBtn");
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".board-tab-content");
  const boardLoading = document.getElementById("boardLoading");
  const boardEmpty = document.getElementById("boardEmpty");
  
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

  let isGenerating = false;
  let activeSessionId = "session-" + Math.random().toString(36).substring(2, 15);
  const maskedTexts = new Map();

  const MASK_REGEX = window.MASK_REGEX || /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;

  remoteLog("[Custom UI] Application initialized. Session ID: " + activeSessionId);

  tabButtons.forEach(button => {
    button.addEventListener("click", () => {
      const targetTabId = button.getAttribute("data-tab");
      
      tabButtons.forEach(btn => btn.classList.remove("active"));
      tabContents.forEach(content => content.classList.remove("active"));
      
      button.classList.add("active");
      document.getElementById(targetTabId).classList.add("active");
    });
  });

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
    sendBtn.innerHTML = `<span class="material-symbols-outlined loader-spinner" style="width:20px;height:20px;border-width:2px;"></span>`;
    
    boardEmpty.style.display = "none";
    boardLoading.style.display = "flex";

    const localMatches = rawPrompt.match(MASK_REGEX) || [];
    localMatches.forEach(match => {
      const masked = "#".repeat(match.length);
      maskedTexts.set(match, masked);
    });

    remoteLog("[Custom UI] Client optimistic matches: " + JSON.stringify(localMatches));

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
        buffer = lines.pop();

        for (const line of lines) {
          const cleanLine = line.trim();
          if (cleanLine.startsWith("data:")) {
            try {
              const eventData = JSON.parse(cleanLine.substring(5).trim());
              
              if (eventData.content && eventData.content.parts) {
                const partText = eventData.content.parts.map(p => p.text || "").join("");
                
                if (partText) {
                  if (eventData.author && eventData.author !== activeAuthor) {
                    activeAuthor = eventData.author;
                    remoteLog("[Custom UI] Active agent changed to: " + activeAuthor);
                  }

                  accumulatedResponse += partText;
                  
                  const renderedText = renderTextWithShields(accumulatedResponse);
                  chefBubbleBody.innerHTML = formatMarkdownToHTML(renderedText);
                  
                  parseAndPopulateGourmetBoard(accumulatedResponse);
                }
              }
            } catch (e) {
            }
          }
        }
      }
      
      remoteLog("[Custom UI] Stream completed successfully.");
      
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
    boardLoading.style.display = "none";
    
    if (!recipeArticle.innerHTML.trim()) {
      boardEmpty.style.display = "flex";
    }
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

  // Render text with interactive secure shields
  function renderTextWithShields(text) {
    let output = text;
    const sortedKeys = Array.from(maskedTexts.keys()).sort((a, b) => b.length - a.length);
    
    sortedKeys.forEach(clearText => {
      const maskedText = maskedTexts.get(clearText);
      const shieldHTML = `<span class="shielded-badge" title="PII masked locally to prevent leaks. Clear: ${clearText.replace(/"/g, '&quot;')}"><span class="material-symbols-outlined" style="font-size:14px;vertical-align:middle;margin-right:4px;">shield</span>Sensitive Data Shielded</span>`;
      
      output = output.replaceAll(clearText, shieldHTML);
      output = output.replaceAll(maskedText, shieldHTML);
    });
    
    return output;
  }

  function parseAndPopulateGourmetBoard(text) {
    const recipeSectionStr = extractSection(text, ["recipe", "ingredients", "instructions"], ["shopping list", "grocery list", "nutrition"]);
    const shoppingSectionStr = extractSection(text, ["shopping list", "grocery list", "ingredients needed to buy"], ["nutrition", "macronutrient", "calories"]);
    const nutritionSectionStr = extractSection(text, ["nutrition", "macronutrient", "calories"], []);

    if (recipeSectionStr) {
      recipeArticle.innerHTML = formatMarkdownToHTML(recipeSectionStr);
    }

    if (shoppingSectionStr) {
      const items = parseListItems(shoppingSectionStr);
      if (items.length > 0) {
        checklistDepartments.innerHTML = renderChecklistHTML(items);
      }
    }

    if (nutritionSectionStr) {
      const metrics = parseNutritionMetrics(nutritionSectionStr);
      updateNutritionHUD(metrics);
    }
  }

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
    
    return sectionLines.length > 0 ? sectionLines.join("\n") : text;
  }

  function parseListItems(sectionStr) {
    const lines = sectionStr.split("\n");
    const items = [];
    let currentDept = "Other";
    
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

  function updateNutritionHUD(metrics) {
    nutrCal.innerHTML = `${metrics.cal} <span class="unit">kcal</span>`;
    nutrPro.innerHTML = `${metrics.pro} <span class="unit">g</span>`;
    nutrCarb.innerHTML = `${metrics.carb} <span class="unit">g</span>`;
    nutrFat.innerHTML = `${metrics.fat} <span class="unit">g</span>`;
    
    const pctCal = Math.min(100, (metrics.cal / 2000) * 100);
    const pctPro = Math.min(100, (metrics.pro / 120) * 100);
    const pctCarb = Math.min(100, (metrics.carb / 250) * 100);
    const pctFat = Math.min(100, (metrics.fat / 70) * 100);
    
    barCal.style.width = `${pctCal}%`;
    barPro.style.width = `${pctPro}%`;
    barCarb.style.width = `${pctCarb}%`;
    barFat.style.width = `${pctFat}%`;
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

  window.resetChecklist = () => {
    const checkboxes = checklistDepartments.querySelectorAll("input[type='checkbox']");
    checkboxes.forEach(cb => cb.checked = false);
  };
});"""
