# -*- coding: utf-8 -*-
html_path = r'D:\workspace\english\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 在设置面板中加入发音音源选择下拉框
old_setting_panel = """        <div class="setting-item">
          <label class="setting-label">发音人 (Voice)</label>
          <select id="voice-select">
            <option value="">正在检测发音人...</option>
          </select>
        </div>"""

new_setting_panel = """        <div class="setting-item">
          <label class="setting-label">发音音源 (Audio Source)</label>
          <select id="engine-select">
            <option value="online">🎙️ 真人原声词典 (推荐·兼容三星/UC/苹果/免装语音包)</option>
            <option value="tts">🤖 系统本地 TTS 引擎 (完全离线模式)</option>
          </select>
        </div>

        <div class="setting-item" id="voice-select-group" style="display:none;">
          <label class="setting-label">系统 TTS 发音人 (Voice)</label>
          <select id="voice-select">
            <option value="">正在检测发音人...</option>
          </select>
        </div>"""

html = html.replace(old_setting_panel, new_setting_panel)

# 2. 修改 settings 对象，默认使用 online
old_settings = """    let settings = {
      rate: 1.0,
      repeatPerWord: 2,
      delaySeconds: 1.5,
      voiceURI: "",
      readChinese: false,
      keepAwake: true
    };"""

new_settings = """    let settings = {
      rate: 1.0,
      repeatPerWord: 2,
      delaySeconds: 1.5,
      voiceURI: "",
      readChinese: false,
      keepAwake: true,
      engineMode: "online" // "online" (真人词典原声) 或 "tts" (系统本地语音)
    };"""

html = html.replace(old_settings, new_settings)

# 3. DOM 引用与 loadSavedData
old_dom_ref = 'const voiceSelect = document.getElementById("voice-select");'
new_dom_ref = """const engineSelect = document.getElementById("engine-select");
    const voiceSelectGroup = document.getElementById("voice-select-group");
    const voiceSelect = document.getElementById("voice-select");"""
html = html.replace(old_dom_ref, new_dom_ref)

old_load_settings = 'keepAwakeToggle.checked = settings.keepAwake !== false;'
new_load_settings = """keepAwakeToggle.checked = settings.keepAwake !== false;
      if (settings.engineMode) {
        engineSelect.value = settings.engineMode;
      }
      voiceSelectGroup.style.display = settings.engineMode === "tts" ? "flex" : "none";"""
html = html.replace(old_load_settings, new_load_settings)

# 4. 重构核心发音方法：增加 playWord(item, onEnded)
old_speak_text = """    // 4. 朗读核心 (带移动端防回收保护与中英文双语能力)
    function speakText(text, onEnded) {"""

new_speak_text = """    // 4. 朗读核心 (支持在线真人原声词典与系统本地 TTS 双引擎，完美兼容三星/UC等手机)
    let wordAudioPlayer = new Audio();

    function playWord(item, onEnded) {
      if (settings.engineMode === "tts") {
        speakTextTTS(item.word, onEnded);
        return;
      }

      // 🎙️ 模式一：真人词典原声音频流 (免装语音包，三星浏览器/UC浏览器 100% 响声)
      wordAudioPlayer.src = `https://dict.youdao.com/dictvoice?audio=${encodeURIComponent(item.word)}&type=2`;
      wordAudioPlayer.playbackRate = settings.rate;
      wordCard.classList.add("speaking");

      let isFinished = false;
      const finish = () => {
        if (isFinished) return;
        isFinished = true;
        wordCard.classList.remove("speaking");
        if (onEnded) onEnded();
      };

      wordAudioPlayer.onended = finish;
      wordAudioPlayer.onerror = () => {
        console.warn("在线真人音频请求失败，自动无缝降级到本地 TTS 引擎");
        speakTextTTS(item.word, finish);
      };

      wordAudioPlayer.play().catch(err => {
        console.warn("音频自动播放被拦截，降级到 TTS:", err);
        speakTextTTS(item.word, finish);
      });
    }

    function speakTextTTS(text, onEnded) {"""

html = html.replace(old_speak_text, new_speak_text)

# 5. 更新 playCurrentWord() 中的调用
html = html.replace('speakText(item.word, () => {', 'playWord(item, () => {')

# 6. 更新 stopSpeaking()：同时停止音频播放器
old_stop_speaking = """    function stopSpeaking() {
      if (timerId) clearTimeout(timerId);
      if (synth) synth.cancel();
      wordCard.classList.remove("speaking");
      repeatBadge.style.display = "none";
      window.activeUtterance = null;
    }"""

new_stop_speaking = """    function stopSpeaking() {
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

html = html.replace(old_stop_speaking, new_stop_speaking)

# 7. 更新 speakSingleWord(item)
old_speak_single = """    function speakSingleWord(item) {
      stopSpeaking();
      speakText(item.word, () => {
        if (settings.readChinese && item.meaning) {
          timerId = setTimeout(() => {
            speakChinese(item.meaning);
          }, 300);
        }
      });
    }"""

new_speak_single = """    function speakSingleWord(item) {
      stopSpeaking();
      playWord(item, () => {
        if (settings.readChinese && item.meaning) {
          timerId = setTimeout(() => {
            speakChinese(item.meaning);
          }, 300);
        }
      });
    }"""

html = html.replace(old_speak_single, new_speak_single)

# 8. 绑定 engineSelect 变更事件
old_voice_select_change = """    voiceSelect.addEventListener("change", () => {
      const found = voices.find(v => v.voiceURI === voiceSelect.value);"""

new_voice_select_change = """    engineSelect.addEventListener("change", (e) => {
      settings.engineMode = e.target.value;
      voiceSelectGroup.style.display = settings.engineMode === "tts" ? "flex" : "none";
      localStorage.setItem("english_words_settings", JSON.stringify(settings));
    });

    voiceSelect.addEventListener("change", () => {
      const found = voices.find(v => v.voiceURI === voiceSelect.value);"""

html = html.replace(old_voice_select_change, new_voice_select_change)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html 真人在线原声 + 本地 TTS 双引擎升级完成！")
