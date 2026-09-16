# -*- coding: utf-8 -*-
html_path = r'D:\workspace\english\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 注入模拟熄屏的 CSS
css_fake_screen = """
    /* 🕶️ 模拟熄屏遮罩 (纯黑防误触，装口袋畅听) */
    .fake-screen-overlay {
      position: fixed;
      inset: 0;
      background: #000000 !important;
      z-index: 999999;
      display: none;
      flex-direction: column;
      justify-content: space-between;
      align-items: center;
      padding: 40px 24px calc(env(safe-area-inset-bottom) + 30px) 24px;
      user-select: none;
      -webkit-user-select: none;
      touch-action: none;
    }

    .fake-screen-top {
      display: flex;
      align-items: center;
      gap: 8px;
      color: rgba(255, 255, 255, 0.2);
      font-size: 13px;
      letter-spacing: 0.5px;
    }

    .fake-pulse {
      width: 8px;
      height: 8px;
      background: #38bdf8;
      border-radius: 50%;
      opacity: 0.4;
      animation: fakePulse 2s infinite ease-in-out;
    }

    @keyframes fakePulse {
      0%, 100% { transform: scale(0.9); opacity: 0.3; }
      50% { transform: scale(1.3); opacity: 0.8; }
    }

    .fake-screen-center {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      gap: 12px;
    }

    .fake-word {
      color: rgba(255, 255, 255, 0.4);
      font-size: 32px;
      font-weight: 800;
      letter-spacing: -0.5px;
    }

    .fake-phonetic {
      color: rgba(56, 189, 248, 0.4);
      font-size: 15px;
    }

    .fake-meaning {
      color: rgba(255, 255, 255, 0.25);
      font-size: 14px;
      max-width: 320px;
      line-height: 1.4;
    }

    .fake-screen-bottom {
      color: rgba(255, 255, 255, 0.18);
      font-size: 12px;
      letter-spacing: 1px;
      text-align: center;
      border: 1px dashed rgba(255, 255, 255, 0.1);
      padding: 8px 18px;
      border-radius: 20px;
    }
"""

html = html.replace('</style>', css_fake_screen + '\n  </style>')

# 2. 在控制栏中加入【🕶️ 模拟熄屏】按钮
old_btn_row = """        <!-- 按钮控制组 (大尺寸，防误触，单手舒适点击) -->
        <div class="btn-row">
          <button class="btn-action" id="btn-prev" title="上一个">"""

new_btn_row = """        <!-- 按钮控制组 (大尺寸，防误触，单手舒适点击) -->
        <div class="btn-row">
          <button class="btn-action" id="btn-prev" title="上一个">"""

# 在 btn-row 下方增加模拟熄屏按钮行
btn_fake_html = """        <!-- 模拟熄屏听背按钮 (突破各大手机浏览器锁屏杀后台限制) -->
        <div style="display: flex; justify-content: center; margin-top: -4px;">
          <button class="btn-action" id="btn-fake-screen-off" style="width: 100%; max-width: 320px; justify-content: center; background: rgba(56, 189, 248, 0.12); color: var(--accent); border: 1px solid rgba(56, 189, 248, 0.3); font-size: 13.5px; font-weight: 700; gap: 8px; min-height: 42px;">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
            🕶️ 模拟熄屏听背 (放口袋/防误触防中断)
          </button>
        </div>
"""

target_insert = '        <!-- 手机专属提示 -->\n        <div class="mobile-tip">'
html = html.replace(target_insert, btn_fake_html + '\n' + target_insert)

# 3. 在 body 末尾加入模拟熄屏浮层 HTML
fake_screen_overlay_html = """
  <!-- 🕶️ 模拟熄屏遮罩浮层 -->
  <div id="fake-screen-overlay" class="fake-screen-overlay">
    <div class="fake-screen-top">
      <div class="fake-pulse"></div>
      <span>口袋听背模式运行中 (已防误触)</span>
    </div>
    <div class="fake-screen-center">
      <div class="fake-word" id="fake-word-text">accept</div>
      <div class="fake-phonetic" id="fake-phonetic-text">/əkˈsept/</div>
      <div class="fake-meaning" id="fake-meaning-text">v. 接受，收受</div>
    </div>
    <div class="fake-screen-bottom">
      👆 双击或长按任意位置退出熄屏
    </div>
  </div>
"""

html = html.replace('</body>', fake_screen_overlay_html + '\n</body>')

# 4. 加入 JS 逻辑
fake_screen_js = """
    // ==========================================
    // 🕶️ 模拟熄屏模式逻辑 (绕过 UC、微信等锁屏强制杀后台)
    // ==========================================
    const btnFakeScreenOff = document.getElementById("btn-fake-screen-off");
    const fakeScreenOverlay = document.getElementById("fake-screen-overlay");
    const fakeWordText = document.getElementById("fake-word-text");
    const fakePhoneticText = document.getElementById("fake-phonetic-text");
    const fakeMeaningText = document.getElementById("fake-meaning-text");
    let isFakeScreenOn = false;

    function enterFakeScreen() {
      isFakeScreenOn = true;
      fakeScreenOverlay.style.display = "flex";
      updateFakeScreenDisplay();

      // 自动开始播放
      if (!isPlaying) {
        togglePlay(true);
      }

      // 尝试进入全屏（部分浏览器支持）
      try {
        if (document.documentElement.requestFullscreen) {
          document.documentElement.requestFullscreen().catch(() => {});
        } else if (document.documentElement.webkitRequestFullscreen) {
          document.documentElement.webkitRequestFullscreen();
        }
      } catch (e) {}
    }

    function exitFakeScreen() {
      isFakeScreenOn = false;
      fakeScreenOverlay.style.display = "none";
      try {
        if (document.exitFullscreen) {
          document.exitFullscreen().catch(() => {});
        } else if (document.webkitExitFullscreen) {
          document.webkitExitFullscreen();
        }
      } catch (e) {}
    }

    function updateFakeScreenDisplay() {
      if (!isFakeScreenOn || words.length === 0) return;
      const item = words[currentIndex];
      if (!item) return;
      fakeWordText.textContent = item.word;
      fakePhoneticText.textContent = item.phonetic || "";
      fakeMeaningText.textContent = item.meaning ? (item.meaning.length > 36 ? item.meaning.substring(0, 36) + "..." : item.meaning) : "";
    }

    if (btnFakeScreenOff) {
      btnFakeScreenOff.addEventListener("click", enterFakeScreen);
    }

    // 双击退出
    fakeScreenOverlay.addEventListener("dblclick", exitFakeScreen);

    // 触屏长按退出 (移动端专属防误触)
    let touchTimer = null;
    fakeScreenOverlay.addEventListener("touchstart", (e) => {
      e.preventDefault();
      touchTimer = setTimeout(() => {
        exitFakeScreen();
      }, 500); // 长按 500 毫秒退出
    }, { passive: false });

    fakeScreenOverlay.addEventListener("touchend", () => {
      if (touchTimer) clearTimeout(touchTimer);
    });

    fakeScreenOverlay.addEventListener("touchmove", () => {
      if (touchTimer) clearTimeout(touchTimer);
    });
"""

# 在 renderWord() 中挂载 updateFakeScreenDisplay()
html = html.replace('updateMediaSession();', 'updateMediaSession();\n      updateFakeScreenDisplay();')

# 在 script 末尾插入 fake_screen_js
html = html.replace('</script>', fake_screen_js + '\n  </script>')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html 模拟熄屏听背模式添加成功！")
