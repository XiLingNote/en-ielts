# -*- coding: utf-8 -*-
import re

html_path = r'D:\workspace\english\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 彻底根治小屏幕（如三星 S24 等 360px 宽度）横向滚动条问题
# 增加全局容器与全景卡片的移动端防溢出 CSS
s24_responsive_css = """
    /* 📱 三星 S24 等窄屏移动端超强防溢出 (彻底杜绝横向滚动条) */
    html, body {
      overflow-x: hidden !important;
      max-width: 100vw !important;
      width: 100% !important;
    }

    .container {
      max-width: 100% !important;
      width: 100% !important;
      min-width: 0 !important;
      overflow-x: hidden !important;
      padding: 12px 10px 40px 10px !important;
    }

    #view-player, #view-reader {
      max-width: 100% !important;
      width: 100% !important;
      min-width: 0 !important;
      overflow-x: hidden !important;
    }

    .reader-toolbar {
      max-width: 100% !important;
      width: 100% !important;
      min-width: 0 !important;
      padding: 12px !important;
    }

    .alphabet-nav {
      max-width: 100% !important;
      width: 100% !important;
      min-width: 0 !important;
      overflow-x: auto !important;
      -webkit-overflow-scrolling: touch !important;
    }

    .reader-list {
      max-width: 100% !important;
      width: 100% !important;
      min-width: 0 !important;
      overflow-x: hidden !important;
    }

    .reader-card {
      max-width: 100% !important;
      width: 100% !important;
      min-width: 0 !important;
      word-break: break-word !important;
      overflow-wrap: anywhere !important;
    }

    .reader-card-info {
      max-width: 100% !important;
      width: 100% !important;
      min-width: 0 !important;
    }

    .reader-card-meaning {
      white-space: normal !important;
      word-break: break-word !important;
      overflow-wrap: anywhere !important;
      max-width: 100% !important;
      line-height: 1.55 !important;
    }

    @media (max-width: 640px) {
      .reader-card {
        flex-direction: column !important;
        align-items: stretch !important;
        padding: 12px 14px !important;
        gap: 10px !important;
      }

      .reader-card-actions {
        width: 100% !important;
        display: flex !important;
        justify-content: flex-end !important;
        padding-top: 8px !important;
        border-top: 1px solid rgba(255, 255, 255, 0.06) !important;
      }

      .reader-search-row {
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 8px !important;
      }

      .reader-stats {
        text-align: right !important;
        font-size: 11px !important;
      }

      .current-word {
        font-size: clamp(26px, 8.5vw, 42px) !important;
      }

      .word-meaning {
        font-size: 14px !important;
        word-break: break-word !important;
        overflow-wrap: anywhere !important;
      }

      header {
        padding: 10px 12px !important;
      }

      .tab-btn {
        padding: 5px 10px !important;
        font-size: 12px !important;
      }
    }
"""

html = html.replace('</style>', s24_responsive_css + '\n  </style>')

# 2. 在 DOM 中注入专用的隐藏音频播放器，并在控制区增加“发音测试”按钮与音源快切
dom_audio = """
  <!-- 专为三星等移动端浏览器配置的 DOM Audio 播放器 (带 playsinline) -->
  <audio id="core-audio-player" preload="auto" playsinline style="display:none;"></audio>
"""
html = html.replace('</body>', dom_audio + '\n</body>')

# 3. 重构底层播放逻辑：
# 解决 3 个核心 Bug：
# 1) 移动端浏览器对双重回调 (onerror + play().catch) 的并发冲突拦截
# 2) synth.cancel() 紧跟 synth.speak() 导致 Android 朗读直接被取消
# 3) 三星 S24 强制指定 currentVoice 失败的静音 Bug
new_audio_engine_js = """
    // ==========================================
    // 🔊 强化版多源发音引擎 (完美适配三星 S24、UC、Chrome、Safari)
    // ==========================================
    const coreAudioPlayer = document.getElementById("core-audio-player");
    let currentPlaySessionId = 0; // 防止异步双重回调重入冲突

    // 核心播放入口 (智能三级容灾：有道原声 -> 百度原声 -> 系统 TTS)
    function playWord(item, onEnded) {
      const sessionId = ++currentPlaySessionId;
      wordCard.classList.add("speaking");

      let finished = false;
      const done = () => {
        if (finished || sessionId !== currentPlaySessionId) return;
        finished = true;
        wordCard.classList.remove("speaking");
        if (onEnded) onEnded();
      };

      // 模式 A：用户明确选择纯本地 TTS
      if (settings.engineMode === "tts") {
        speakTextTTS(item.word, done);
        return;
      }

      // 模式 B：在线真人词典原声 (优先有道，次选备用源，最后回退 TTS)
      const encodedWord = encodeURIComponent(item.word.trim());
      const primaryUrl = `https://dict.youdao.com/dictvoice?audio=${encodedWord}&type=2`;
      const fallbackUrl = `https://fanyi.baidu.com/gettts?lan=en&text=${encodedWord}&spd=4&source=web`;

      let triedFallback = false;

      coreAudioPlayer.src = primaryUrl;
      coreAudioPlayer.playbackRate = settings.rate;

      coreAudioPlayer.onended = () => {
        done();
      };

      const handleAudioError = () => {
        if (finished || sessionId !== currentPlaySessionId) return;
        if (!triedFallback) {
          triedFallback = true;
          console.warn("主音源加载异常，尝试备用真人音源...");
          coreAudioPlayer.src = fallbackUrl;
          coreAudioPlayer.play().catch(handleAudioError);
        } else {
          console.warn("在线音频均受限，无缝切换为系统本地 TTS 朗读...");
          speakTextTTS(item.word, done);
        }
      };

      coreAudioPlayer.onerror = handleAudioError;

      // 触发播放
      const playPromise = coreAudioPlayer.play();
      if (playPromise !== undefined) {
        playPromise.catch(err => {
          console.warn("音频自动播放被浏览器拦截，转为 TTS 兜底:", err);
          handleAudioError();
        });
      }
    }

    // 系统 TTS 朗读核心 (专为 Android/三星 S24 优化，绝不在 speak 前立即 cancel)
    function speakTextTTS(text, onEnded) {
      if (!synth) {
        if (onEnded) onEnded();
        return;
      }

      // 仅在已有发音卡住时才 cancel，避免 Chromium/Android 立即取消 upcoming speak 的 bug
      if (synth.speaking || synth.pending) {
        synth.cancel();
      }

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "en-US";
      utterance.rate = settings.rate;

      // 针对三星 S24：优先匹配真实有效的声音，若无或匹配有风险，直接使用默认 en-US
      if (currentVoice && currentVoice.lang && currentVoice.lang.toLowerCase().startsWith("en")) {
        try {
          utterance.voice = currentVoice;
        } catch (e) {}
      }

      window.activeUtterance = utterance; // 避免移动端垃圾回收
      wordCard.classList.add("speaking");

      let hasFired = false;
      const finishTTS = () => {
        if (hasFired) return;
        hasFired = true;
        wordCard.classList.remove("speaking");
        window.activeUtterance = null;
        if (onEnded) onEnded();
      };

      utterance.onend = finishTTS;
      utterance.onerror = (e) => {
        console.warn("TTS 发音遇到错误:", e);
        finishTTS();
      };

      try {
        synth.speak(utterance);
      } catch (e) {
        console.warn("synth.speak 抛出异常:", e);
        finishTTS();
      }
    }
"""

# 替换旧的 playWord 和 speakTextTTS 实现
old_engine_pattern = r'let wordAudioPlayer = new Audio\(\);[\s\S]*?function speakTextTTS\(text, onEnded\) \{[\s\S]*?\n    \}'
html = re.sub(old_engine_pattern, new_audio_engine_js.strip(), html, count=1)

# 更新 stopSpeaking：同时停止 coreAudioPlayer
old_stop_code = """    function stopSpeaking() {
      if (timerId) clearTimeout(timerId);
      if (synth) synth.cancel();
      if (wordAudioPlayer) {
        wordAudioPlayer.pause();
        wordAudioPlayer.currentTime = 0;
      }
      wordCard.classList.remove("speaking");
      repeatBadge.style.display = "none";
      window.activeUtterance = null;
    }"""

new_stop_code = """    function stopSpeaking() {
      currentPlaySessionId++; // 废弃先前的一切异步回调
      if (timerId) clearTimeout(timerId);
      if (synth) synth.cancel();
      if (coreAudioPlayer) {
        coreAudioPlayer.pause();
        coreAudioPlayer.currentTime = 0;
      }
      wordCard.classList.remove("speaking");
      repeatBadge.style.display = "none";
      window.activeUtterance = null;
    }"""

html = html.replace(old_stop_code, new_stop_code)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("针对三星 S24 屏幕宽度防溢出与多源音频引擎优化成功！")
