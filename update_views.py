# -*- coding: utf-8 -*-
import re

html_path = r'D:\workspace\english\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 注入 CSS 样式
css_to_add = """
    /* 顶部模式切换按钮 */
    .mode-tabs {
      display: flex;
      background: rgba(15, 23, 42, 0.7);
      padding: 3px;
      border-radius: 12px;
      border: 1px solid var(--card-border);
      gap: 4px;
    }

    .tab-btn {
      background: transparent;
      color: var(--text-muted);
      border: none;
      padding: 6px 13px;
      border-radius: 9px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 5px;
      transition: all 0.2s ease;
    }

    .tab-btn:hover {
      color: var(--text-main);
    }

    .tab-btn.active {
      background: var(--card-bg);
      color: var(--accent);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
    }

    /* 视图切换容器 */
    #view-player {
      display: grid;
      grid-template-columns: 1fr 320px;
      gap: 20px;
      width: 100%;
    }

    #view-player.hidden {
      display: none !important;
    }

    #view-reader {
      display: none;
      flex-direction: column;
      gap: 16px;
      width: 100%;
    }

    #view-reader.active {
      display: flex !important;
    }

    @media (max-width: 768px) {
      #view-player {
        grid-template-columns: 1fr;
      }
      .mode-tabs {
        order: 3;
        width: 100%;
        justify-content: center;
        margin-top: 6px;
      }
      header {
        flex-wrap: wrap;
        gap: 8px;
      }
    }

    /* 全景通读工具栏：搜索与 A-Z 快速字母筛选 */
    .reader-toolbar {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 14px 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      position: sticky;
      top: 64px;
      z-index: 30;
      box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4);
    }

    .reader-search-row {
      display: flex;
      gap: 12px;
      align-items: center;
      justify-content: space-between;
    }

    .search-input-box {
      position: relative;
      flex: 1;
    }

    .search-input-box input {
      width: 100%;
      background: #0f172a;
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 9px 36px 9px 14px;
      color: var(--text-main);
      font-size: 14px;
      outline: none;
    }

    .search-input-box input:focus {
      border-color: var(--accent);
    }

    .search-clear-btn {
      position: absolute;
      right: 10px;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 14px;
      display: none;
    }

    .reader-stats {
      font-size: 12px;
      color: var(--text-muted);
      white-space: nowrap;
    }

    /* 字母横向滚动条 */
    .alphabet-nav {
      display: flex;
      gap: 5px;
      overflow-x: auto;
      padding-bottom: 4px;
      -webkit-overflow-scrolling: touch;
    }

    .alphabet-nav::-webkit-scrollbar {
      height: 4px;
    }

    .alphabet-nav::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.15);
      border-radius: 4px;
    }

    .letter-btn {
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-muted);
      border: 1px solid transparent;
      padding: 4px 9px;
      border-radius: 7px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s;
    }

    .letter-btn:hover {
      background: rgba(255, 255, 255, 0.12);
      color: var(--text-main);
    }

    .letter-btn.active {
      background: rgba(56, 189, 248, 0.18);
      color: var(--accent);
      border-color: rgba(56, 189, 248, 0.45);
    }

    /* 全景卡片列表 */
    .reader-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .reader-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 14px 16px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 14px;
      transition: border-color 0.2s, transform 0.15s;
    }

    .reader-card:hover {
      border-color: rgba(56, 189, 248, 0.4);
    }

    .reader-card.playing-active {
      border-color: var(--accent);
      background: rgba(56, 189, 248, 0.06);
    }

    .reader-card-info {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 5px;
      min-width: 0;
    }

    .reader-card-header {
      display: flex;
      align-items: baseline;
      gap: 10px;
      flex-wrap: wrap;
    }

    .reader-card-idx {
      font-size: 11px;
      font-weight: 700;
      color: var(--text-muted);
      background: rgba(255, 255, 255, 0.07);
      padding: 2px 6px;
      border-radius: 5px;
    }

    .reader-card-word {
      font-size: 19px;
      font-weight: 800;
      color: #ffffff;
      letter-spacing: -0.3px;
    }

    .reader-card-phonetic {
      font-size: 13px;
      color: var(--accent);
      font-family: "Lucida Sans Unicode", "Segoe UI", Arial, sans-serif;
    }

    .reader-card-meaning {
      font-size: 13.5px;
      color: #cbd5e1;
      line-height: 1.5;
      user-select: text;
      word-break: break-word;
    }

    .reader-card-actions {
      display: flex;
      gap: 6px;
      align-items: center;
      flex-shrink: 0;
    }

    .btn-reader-sound {
      background: rgba(56, 189, 248, 0.12);
      color: var(--accent);
      border: 1px solid rgba(56, 189, 248, 0.25);
      border-radius: 8px;
      padding: 6px 10px;
      font-size: 13px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 4px;
      cursor: pointer;
    }

    .btn-reader-sound:hover, .btn-reader-sound:active {
      background: var(--accent);
      color: #0f172a;
    }

    .btn-reader-jump {
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-main);
      border: 1px solid transparent;
      border-radius: 8px;
      padding: 6px 10px;
      font-size: 13px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 4px;
      cursor: pointer;
    }

    .btn-reader-jump:hover, .btn-reader-jump:active {
      background: rgba(255, 255, 255, 0.16);
    }

    /* 侧边栏词汇目录富样式 */
    .word-list-box {
      max-height: 360px !important;
    }

    .word-list-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 7px 9px;
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.15s;
      gap: 6px;
    }

    .side-item-info {
      flex: 1;
      min-width: 0;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .side-item-top {
      display: flex;
      align-items: baseline;
      gap: 6px;
    }

    .side-item-word {
      font-weight: 700;
      color: var(--text-main);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      font-size: 13px;
    }

    .side-item-phonetic {
      font-size: 11px;
      color: var(--accent);
      white-space: nowrap;
    }

    .side-item-meaning {
      font-size: 11px;
      color: var(--text-muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      line-height: 1.2;
    }

    .side-speak-btn {
      background: rgba(255, 255, 255, 0.06);
      color: var(--accent);
      border: none;
      padding: 4px 7px;
      border-radius: 6px;
      font-size: 12px;
      cursor: pointer;
      flex-shrink: 0;
    }

    .side-speak-btn:hover {
      background: var(--accent);
      color: #0f172a;
    }
"""

# 在 </style> 前注入
html = html.replace('</style>', css_to_add + '\n  </style>')

# 2. 替换 header，加入模式切换选项卡
old_header = """  <!-- 顶部栏 -->
  <header>
    <div class="logo-area">
      <span class="logo-badge">TTS</span>
      <h1 class="logo-title">雅思 2683 词朗读</h1>
    </div>
    <div class="header-actions">
      <button class="btn-action" id="btn-open-import" style="padding: 6px 12px; font-size:13px;">
        <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>
        导入词库
      </button>
      <button class="btn-action" id="btn-reset" style="padding: 6px 10px; font-size:13px;" title="从头开始">重置</button>
    </div>
  </header>"""

new_header = """  <!-- 顶部栏 -->
  <header>
    <div class="logo-area">
      <span class="logo-badge">IELTS</span>
      <h1 class="logo-title">雅思 2683 核心词汇</h1>
    </div>

    <!-- 模式切换选项卡 -->
    <div class="mode-tabs">
      <button class="tab-btn active" id="tab-btn-player">
        <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg>
        循环伴读
      </button>
      <button class="tab-btn" id="tab-btn-reader">
        <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
        全景通读词书
      </button>
    </div>

    <div class="header-actions">
      <button class="btn-action" id="btn-open-import" style="padding: 6px 12px; font-size:13px;">
        <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>
        词库管理
      </button>
      <button class="btn-action" id="btn-reset" style="padding: 6px 10px; font-size:13px;" title="从头开始">重置</button>
    </div>
  </header>"""

html = html.replace(old_header, new_header)

# 3. 升级 main 容器，支持 #view-player 和 #view-reader 两个视图
old_main_start = '  <main class="container">\n    <!-- 舞台展示与播放控制 -->\n    <div class="player-section">'
new_main_start = """  <main class="container">
    <!-- 视图 1：伴读播放模式 -->
    <div id="view-player">
      <!-- 舞台展示与播放控制 -->
      <div class="player-section">"""
html = html.replace(old_main_start, new_main_start)

# 侧边栏标题处增加“全屏通读 ➔”快捷按钮
old_word_list_title = '<div class="panel-title" style="border:none; padding:0;">\n          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h7"/></svg>\n          单词目录\n        </div>'
new_word_list_title = """<div class="panel-title" style="border:none; padding:0; justify-content:space-between;">
          <div style="display:flex; align-items:center; gap:6px;">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h7"/></svg>
            单词目录
          </div>
          <button id="btn-quick-to-reader" style="font-size:12px; color:var(--accent); background:none; border:none; cursor:pointer; font-weight:600;">
            全景通读 ➔
          </button>
        </div>"""
html = html.replace(old_word_list_title, new_word_list_title)

# 关闭 #view-player 并插入 #view-reader
old_main_end = '      <!-- 单词列表快速跳转 -->\n      <div class="word-list-box">\n        '
# 找到 sidebar 结束处
sidebar_end = '      </div>\n    </div>\n  </main>'
new_sidebar_end = """      </div>
    </div>
    </div><!-- 结束 #view-player -->

    <!-- 视图 2：全景通读手册模式 (A-Z筛选、中英对照、点读发音、搜索) -->
    <div id="view-reader">
      <div class="reader-toolbar">
        <div class="reader-search-row">
          <div class="search-input-box">
            <input type="text" id="reader-search-input" placeholder="输入英文或中文搜索（如 accept 或 接受）...">
            <button class="search-clear-btn" id="reader-search-clear">✕</button>
          </div>
          <span class="reader-stats" id="reader-stats">共 2,596 词</span>
        </div>
        <!-- 字母导航栏 -->
        <div class="alphabet-nav" id="alphabet-nav">
          <!-- 动态渲染 A-Z 按钮 -->
        </div>
      </div>

      <!-- 单词卡片列表 -->
      <div class="reader-list" id="reader-cards-container">
        <!-- 动态渲染单词卡片 -->
      </div>
    </div>
  </main>"""
html = html.replace(sidebar_end, new_sidebar_end)

# 4. JavaScript 逻辑增强
# 找到 renderWordList() 并替换为富内容版本
old_render_word_list = """    function renderWordList() {
      wordListContainer.innerHTML = "";
      words.forEach((item, idx) => {
        const row = document.createElement("div");
        row.className = "word-list-item" + (idx === currentIndex ? " active" : "");
        row.id = `list-word-${idx}`;
        row.innerHTML = `<span>${idx + 1}. ${item.word}</span>`;
        row.addEventListener("click", () => {
          jumpToIndex(idx);
        });
        wordListContainer.appendChild(row);
      });
    }"""

new_render_word_list = """    function renderWordList() {
      wordListContainer.innerHTML = "";
      const fragment = document.createDocumentFragment();
      words.forEach((item, idx) => {
        const row = document.createElement("div");
        row.className = "word-list-item" + (idx === currentIndex ? " active" : "");
        row.id = `list-word-${idx}`;

        const shortMeaning = item.meaning ? item.meaning.substring(0, 26) + (item.meaning.length > 26 ? "..." : "") : "";
        row.innerHTML = `
          <div class="side-item-info">
            <div class="side-item-top">
              <span class="side-item-word">${idx + 1}. ${item.word}</span>
              ${item.phonetic ? `<span class="side-item-phonetic">${item.phonetic}</span>` : ""}
            </div>
            ${shortMeaning ? `<div class="side-item-meaning">${shortMeaning}</div>` : ""}
          </div>
          <button class="side-speak-btn" title="点击单读发音" data-idx="${idx}">🔊</button>
        `;

        row.addEventListener("click", (e) => {
          if (e.target.classList.contains("side-speak-btn")) {
            e.stopPropagation();
            jumpToIndex(idx);
            speakSingleWord(item);
            return;
          }
          jumpToIndex(idx);
          if (isPlaying) {
            playCurrentWord();
          } else {
            speakSingleWord(item);
          }
        });
        fragment.appendChild(row);
      });
      wordListContainer.appendChild(fragment);
    }

    // 单次点读发音工具函数（根据当前是否开启双语伴读发音）
    function speakSingleWord(item) {
      stopSpeaking();
      speakText(item.word, () => {
        if (settings.readChinese && item.meaning) {
          timerId = setTimeout(() => {
            speakChinese(item.meaning);
          }, 300);
        }
      });
    }"""

html = html.replace(old_render_word_list, new_render_word_list)

# 5. 注入全景通读手册的核心控制代码与 Tab 切换
reader_js = """
    // ==========================================
    // 📖 全景通读手册核心逻辑 (A-Z、搜索、点读、伴读联动)
    // ==========================================
    let currentView = "player"; // "player" 或 "reader"
    let currentFilterLetter = "ALL";
    let searchQuery = "";
    let readerRenderLimit = 150; // 初始渲染数量，滚动或切换时平滑加载

    const tabBtnPlayer = document.getElementById("tab-btn-player");
    const tabBtnReader = document.getElementById("tab-btn-reader");
    const viewPlayer = document.getElementById("view-player");
    const viewReader = document.getElementById("view-reader");
    const btnQuickToReader = document.getElementById("btn-quick-to-reader");

    const readerSearchInput = document.getElementById("reader-search-input");
    const readerSearchClear = document.getElementById("reader-search-clear");
    const readerStats = document.getElementById("reader-stats");
    const alphabetNav = document.getElementById("alphabet-nav");
    const readerCardsContainer = document.getElementById("reader-cards-container");

    function switchView(viewName) {
      currentView = viewName;
      if (viewName === "player") {
        tabBtnPlayer.classList.add("active");
        tabBtnReader.classList.remove("active");
        viewPlayer.classList.remove("hidden");
        viewReader.classList.remove("active");
      } else {
        tabBtnPlayer.classList.remove("active");
        tabBtnReader.classList.add("active");
        viewPlayer.classList.add("hidden");
        viewReader.classList.add("active");
        renderReaderView();
        // 自动将当前正在学习的单词滚动到视野内
        setTimeout(() => {
          const currentCard = document.getElementById(`reader-card-${currentIndex}`);
          if (currentCard) {
            currentCard.scrollIntoView({ block: "center", behavior: "smooth" });
          }
        }, 100);
      }
    }

    tabBtnPlayer.addEventListener("click", () => switchView("player"));
    tabBtnReader.addEventListener("click", () => switchView("reader"));
    if (btnQuickToReader) {
      btnQuickToReader.addEventListener("click", () => switchView("reader"));
    }

    // 初始化 A-Z 字母分布导航
    function initAlphabetNav() {
      const counts = {};
      words.forEach(item => {
        const letter = item.word.charAt(0).toUpperCase();
        counts[letter] = (counts[letter] || 0) + 1;
      });

      alphabetNav.innerHTML = "";
      const letters = ["ALL", ..."ABCDEFGHIJKLMNOPQRSTUVWXYZ"];
      letters.forEach(letter => {
        const btn = document.createElement("button");
        btn.className = "letter-btn" + (currentFilterLetter === letter ? " active" : "");
        const count = letter === "ALL" ? words.length : (counts[letter] || 0);
        btn.textContent = letter === "ALL" ? `全部 (${count})` : `${letter} (${count})`;
        btn.addEventListener("click", () => {
          currentFilterLetter = letter;
          alphabetNav.querySelectorAll(".letter-btn").forEach(b => b.classList.remove("active"));
          btn.classList.add("active");
          readerRenderLimit = 150;
          renderReaderView();
        });
        alphabetNav.appendChild(btn);
      });
    }

    // 渲染全景词表
    function renderReaderView() {
      let filtered = words.map((item, idx) => ({ ...item, originalIndex: idx }));

      // 字母筛选
      if (currentFilterLetter !== "ALL") {
        filtered = filtered.filter(item => item.word.toUpperCase().startsWith(currentFilterLetter));
      }

      // 搜索关键字筛选（支持英文或中文）
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        filtered = filtered.filter(item => 
          item.word.toLowerCase().includes(q) || 
          (item.meaning && item.meaning.toLowerCase().includes(q))
        );
      }

      readerStats.textContent = `显示 ${filtered.length} / ${words.length} 词`;

      readerCardsContainer.innerHTML = "";
      if (filtered.length === 0) {
        readerCardsContainer.innerHTML = `<div style="text-align:center; padding: 40px; color:var(--text-muted);">没有找到匹配的单词</div>`;
        return;
      }

      const fragment = document.createDocumentFragment();
      const slice = filtered.slice(0, readerRenderLimit);

      slice.forEach(item => {
        const card = document.createElement("div");
        card.className = "reader-card" + (item.originalIndex === currentIndex ? " playing-active" : "");
        card.id = `reader-card-${item.originalIndex}`;

        card.innerHTML = `
          <div class="reader-card-info">
            <div class="reader-card-header">
              <span class="reader-card-idx">#${item.originalIndex + 1}</span>
              <span class="reader-card-word">${item.word}</span>
              ${item.phonetic ? `<span class="reader-card-phonetic">${item.phonetic}</span>` : ""}
            </div>
            <div class="reader-card-meaning">${item.meaning || "暂无释义"}</div>
          </div>
          <div class="reader-card-actions">
            <button class="btn-reader-sound" title="点击单读发音">
              <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/></svg>
              发音
            </button>
            <button class="btn-reader-jump" title="跳转并播放">
              ▶ 伴读
            </button>
          </div>
        `;

        // 按钮事件：点读发音
        const soundBtn = card.querySelector(".btn-reader-sound");
        soundBtn.addEventListener("click", (e) => {
          e.stopPropagation();
          jumpToIndex(item.originalIndex);
          card.classList.add("playing-active");
          speakSingleWord(item);
        });

        // 按钮事件：跳转到伴读卡片播放
        const jumpBtn = card.querySelector(".btn-reader-jump");
        jumpBtn.addEventListener("click", (e) => {
          e.stopPropagation();
          jumpToIndex(item.originalIndex);
          switchView("player");
          if (!isPlaying) togglePlay(true);
        });

        // 点击卡片本身：选定并发音
        card.addEventListener("click", () => {
          jumpToIndex(item.originalIndex);
          speakSingleWord(item);
          document.querySelectorAll(".reader-card").forEach(c => c.classList.remove("playing-active"));
          card.classList.add("playing-active");
        });

        fragment.appendChild(card);
      });

      readerCardsContainer.appendChild(fragment);

      // 加载更多按钮
      if (filtered.length > readerRenderLimit) {
        const moreBtn = document.createElement("button");
        moreBtn.className = "btn-action";
        moreBtn.style.cssText = "width:100%; padding:12px; margin-top:10px; justify-content:center;";
        moreBtn.textContent = `加载更多 (${readerRenderLimit} / ${filtered.length})...`;
        moreBtn.addEventListener("click", () => {
          readerRenderLimit += 150;
          renderReaderView();
        });
        readerCardsContainer.appendChild(moreBtn);
      }
    }

    // 搜索输入防抖
    let searchDebounceTimer = null;
    readerSearchInput.addEventListener("input", (e) => {
      searchQuery = e.target.value;
      readerSearchClear.style.display = searchQuery ? "block" : "none";
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        readerRenderLimit = 150;
        renderReaderView();
      }, 200);
    });

    readerSearchClear.addEventListener("click", () => {
      readerSearchInput.value = "";
      searchQuery = "";
      readerSearchClear.style.display = "none";
      readerRenderLimit = 150;
      renderReaderView();
    });
"""

# 在 loadSavedData() 调用前插入全景通读初始化
html = html.replace('// 启动\n    loadSavedData();', '// 启动\n    ' + reader_js + '\n    loadSavedData();\n    initAlphabetNav();')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html 全景通读手册视图升级成功！")
