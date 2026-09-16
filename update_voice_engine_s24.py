# -*- coding: utf-8 -*-
import re

html_path = r'D:\workspace\english\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 调整 settings 默认使用 "tts"（用户已确认手机装有英语语音包）
html = html.replace('engineMode: "online"', 'engineMode: "tts"')

# 2. 设置面板：发音人选择框保持常驻，并增加【🔊 试听测试】按钮
old_voice_panel = """        <div class="setting-item">
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

new_voice_panel = """        <div class="setting-item">
          <label class="setting-label">发音模式 (Engine)</label>
          <select id="engine-select">
            <option value="tts">🤖 手机系统英语语音包 (已安装·离线极速)</option>
            <option value="online">🎙️ 在线真人词典原声 (备用网络模式)</option>
          </select>
        </div>

        <div class="setting-item" id="voice-select-group">
          <div class="setting-label">
            <span>系统发音人 (Voice)</span>
            <button id="btn-test-voice" style="background: var(--accent); color: #0f172a; border: none; border-radius: 6px; padding: 2px 8px; font-size: 11px; font-weight: 700; cursor: pointer;">
              🔊 试听发音
            </button>
          </div>
          <select id="voice-select">
            <option value="">系统默认自动选择</option>
          </select>
          <div style="font-size:11px; color:var(--accent); margin-top:2px;" id="voice-detected-tip">
            已开启系统本地语音包
          </div>
        </div>"""

html = html.replace(old_voice_panel, new_voice_panel)

# 3. 增强 initVoices：首选选项增加“系统默认自动选择 (无需绑定)”，这对三星 S24 兼容性最佳！
old_init_voices = """      voiceSelect.innerHTML = "";
      if (voices.length === 0) {
        const opt = document.createElement("option");
        opt.textContent = "手机默认英语发音";
        voiceSelect.appendChild(opt);
        return;
      }

      let selectedIndex = 0;
      voices.forEach((voice, index) => {
        const option = document.createElement("option");
        option.value = voice.voiceURI;
        option.textContent = `${voice.name} (${voice.lang})`;

        if (settings.voiceURI && voice.voiceURI === settings.voiceURI) {
          selectedIndex = index;
        } else if (!settings.voiceURI && (
          voice.name.includes("Samantha") || 
          voice.name.includes("Siri") || 
          voice.name.includes("Natural") || 
          voice.lang === "en-US"
        )) {
          selectedIndex = index;
        }

        voiceSelect.appendChild(option);
      });

      voiceSelect.selectedIndex = selectedIndex;
      currentVoice = voices[selectedIndex];"""

new_init_voices = """      voiceSelect.innerHTML = "";
      
      // 添加“系统默认”项作为最稳妥的兼容选项
      const defaultOpt = document.createElement("option");
      defaultOpt.value = "AUTO_DEFAULT";
      defaultOpt.textContent = "⭐️ 系统默认英语发音 (最稳)";
      voiceSelect.appendChild(defaultOpt);

      let foundIdx = -1;
      voices.forEach((voice, index) => {
        const option = document.createElement("option");
        option.value = voice.voiceURI;
        option.textContent = `${voice.name} (${voice.lang})`;

        if (settings.voiceURI && voice.voiceURI === settings.voiceURI) {
          foundIdx = index + 1;
        } else if (!settings.voiceURI && foundIdx === -1 && (
          voice.lang === "en-US" || voice.name.includes("Samsung") || voice.name.includes("Google")
        )) {
          foundIdx = index + 1;
        }

        voiceSelect.appendChild(option);
      });

      if (foundIdx > 0 && foundIdx < voiceSelect.options.length) {
        voiceSelect.selectedIndex = foundIdx;
        currentVoice = voices[foundIdx - 1];
      } else {
        voiceSelect.selectedIndex = 0;
        currentVoice = null; // 为 null 时浏览器自动指派系统活跃语音包
      }

      const tipEl = document.getElementById("voice-detected-tip");
      if (tipEl) {
        tipEl.textContent = `已识别到 ${voices.length} 个英语发音包`;
      }"""

html = html.replace(old_init_voices, new_init_voices)

# 4. 彻底解决 Android / 三星浏览器 SpeechSynthesis 挂起 Bug
old_tts_core = """    // 系统 TTS 朗读核心 (专为 Android/三星 S24 优化，绝不在 speak 前立即 cancel)
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
    }"""

new_tts_core = """    // 系统 TTS 朗读核心 (专为三星 S24/Android 深度优化)
    function speakTextTTS(text, onEnded) {
      if (!synth) {
        if (onEnded) onEnded();
        return;
      }

      // 唤醒可能处于挂起休眠态的 Android 语音通道
      if (synth.paused) {
        try { synth.resume(); } catch (e) {}
      }

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "en-US";
      utterance.rate = settings.rate;
      utterance.volume = 1.0;

      // 如果选定了具体发音人且有效，则绑定；若是默认选项则不锁死 voice，让手机系统自主调度
      if (currentVoice && voiceSelect.value !== "AUTO_DEFAULT") {
        try {
          utterance.voice = currentVoice;
        } catch (e) {}
      }

      window.activeUtterance = utterance;
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
        console.warn("TTS 发音事件异常:", e);
        finishTTS();
      };

      try {
        synth.speak(utterance);
      } catch (e) {
        console.warn("synth.speak 触发异常:", e);
        finishTTS();
      }
    }"""

html = html.replace(old_tts_core, new_tts_core)

# 5. 绑定 voiceSelect 和 btn-test-voice 测试按钮
old_voice_change = """    voiceSelect.addEventListener("change", () => {
      const found = voices.find(v => v.voiceURI === voiceSelect.value);
      if (found) {
        currentVoice = found;
        settings.voiceURI = found.voiceURI;
        localStorage.setItem("english_words_settings", JSON.stringify(settings));
      }
    });"""

new_voice_change = """    voiceSelect.addEventListener("change", () => {
      if (voiceSelect.value === "AUTO_DEFAULT") {
        currentVoice = null;
        settings.voiceURI = "";
      } else {
        const found = voices.find(v => v.voiceURI === voiceSelect.value);
        if (found) {
          currentVoice = found;
          settings.voiceURI = found.voiceURI;
        }
      }
      localStorage.setItem("english_words_settings", JSON.stringify(settings));
    });

    // 试听测试发音
    const btnTestVoice = document.getElementById("btn-test-voice");
    if (btnTestVoice) {
      btnTestVoice.addEventListener("click", () => {
        const curWord = words[currentIndex] ? words[currentIndex].word : "Hello";
        speakTextTTS(`Hello, ${curWord}`, () => {
          console.log("试听完成");
        });
      });
    }"""

html = html.replace(old_voice_change, new_voice_change)

# 6. loadSavedData 恢复设置逻辑
old_restore_voice = """      if (settings.engineMode) {
        engineSelect.value = settings.engineMode;
      }
      voiceSelectGroup.style.display = settings.engineMode === "tts" ? "flex" : "none";"""

new_restore_voice = """      if (settings.engineMode) {
        engineSelect.value = settings.engineMode;
      } else {
        settings.engineMode = "tts";
        engineSelect.value = "tts";
      }
      voiceSelectGroup.style.display = "flex";"""

html = html.replace(old_restore_voice, new_restore_voice)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("精准绑定三星 S24 本地英语读音包与试听测试按钮完成！")
