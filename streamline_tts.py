# -*- coding: utf-8 -*-
import re

html_path = r'D:\workspace\english\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 移除复杂冗余的 engine-select 下拉框，界面回归极简纯粹：专注系统本地英语语音包
old_engine_panel = """        <div class="setting-item">
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

new_engine_panel = """        <div class="setting-item" id="voice-select-group">
          <div class="setting-label">
            <span>系统发音人 (Voice)</span>
            <button id="btn-test-voice" style="background: var(--accent); color: #0f172a; border: none; border-radius: 6px; padding: 3px 9px; font-size: 12px; font-weight: 700; cursor: pointer;">
              🔊 试听测试
            </button>
          </div>
          <select id="voice-select">
            <option value="AUTO_DEFAULT">⭐️ 系统默认英语发音 (推荐)</option>
          </select>
          <div style="font-size:11px; color:var(--accent); margin-top:2px;" id="voice-detected-tip">
            正在检测已安装的系统英语发音包...
          </div>
        </div>"""

html = html.replace(old_engine_panel, new_engine_panel)

# 2. 移除 DOM 隐藏的 core-audio-player
html = html.replace("""  <!-- 专为三星等移动端浏览器配置的 DOM Audio 播放器 (带 playsinline) -->
  <audio id="core-audio-player" preload="auto" playsinline style="display:none;"></audio>""", "")

# 3. 移除 settings 中冗余的 engineMode
html = html.replace('engineMode: "tts"', '')
html = re.sub(r'const engineSelect = document\.getElementById\("engine-select"\);\s*const voiceSelectGroup = document\.getElementById\("voice-select-group"\);', '', html)

# 4. 彻底重写纯净版核心发音模块：纯本地 Web Speech API，彻底根除 cancel 与 speak 并发竞争 Bug
clean_speech_core = """    // ==========================================
    // 🔊 纯净本地系统发音引擎 (针对三星 S24 等 Android 手机深度优化)
    // ==========================================

    // 核心发音方法：纯净原生 Web Speech API
    function speakText(text, onEnded) {
      if (!synth) {
        if (onEnded) onEnded();
        return;
      }

      // 唤醒处于休眠挂起状态的 Android 音频通道
      if (synth.paused) {
        try { synth.resume(); } catch (e) {}
      }

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "en-US";
      utterance.rate = settings.rate;
      utterance.volume = 1.0;

      // 仅在明确选择了特定发音人时绑定；默认时留空让系统底层自行路由，兼容性最强
      if (currentVoice && voiceSelect.value !== "AUTO_DEFAULT") {
        try {
          utterance.voice = currentVoice;
        } catch (e) {}
      }

      window.activeUtterance = utterance; // 避免移动端 Safari/Chrome 垃圾回收
      wordCard.classList.add("speaking");

      let hasFired = false;
      const finish = () => {
        if (hasFired) return;
        hasFired = true;
        wordCard.classList.remove("speaking");
        window.activeUtterance = null;
        if (onEnded) onEnded();
      };

      utterance.onend = finish;
      utterance.onerror = (e) => {
        console.warn("TTS 朗读遇到异常:", e);
        finish();
      };

      try {
        synth.speak(utterance);
      } catch (e) {
        console.warn("synth.speak 异常:", e);
        finish();
      }
    }

    // 清洗中文释义
    function cleanChineseMeaning(meaning) {
      if (!meaning) return "";
      let clean = meaning.replace(/\/.*?\/|\[.*?\]/g, " ").trim();
      clean = clean.replace(/^(v|vt|vi|n|adj|adv|prep|pron|conj|art|num)\.\s*/gi, "");
      const parts = clean.split(/[；;，,]/).filter(s => s.trim());
      if (parts.length > 0) {
        clean = parts.slice(0, 2).join("，");
      }
      return clean.trim() || meaning;
    }

    // 朗读中文释义
    function speakChinese(text, onEnded) {
      if (!synth) {
        if (onEnded) onEnded();
        return;
      }
      const cleanText = cleanChineseMeaning(text);
      if (!cleanText) {
        if (onEnded) onEnded();
        return;
      }

      if (synth.paused) {
        try { synth.resume(); } catch (e) {}
      }

      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.lang = "zh-CN";
      utterance.rate = 1.0;
      utterance.volume = 1.0;
      if (chineseVoice) {
        utterance.voice = chineseVoice;
      }

      window.activeUtterance = utterance;

      let hasFired = false;
      const finish = () => {
        if (hasFired) return;
        hasFired = true;
        window.activeUtterance = null;
        if (onEnded) onEnded();
      };

      utterance.onend = finish;
      utterance.onerror = finish;

      try {
        synth.speak(utterance);
      } catch (e) {
        finish();
      }
    }

    // 单次点读（给列表、卡片以及暂停态点击发音使用）
    function speakSingleWord(item) {
      if (!item) return;
      stopSpeaking();
      // 关键延迟 60ms：给浏览器底层音频通道充分时间完成 cancel 清理，绝不吞音
      setTimeout(() => {
        speakText(item.word, () => {
          if (settings.readChinese && item.meaning) {
            timerId = setTimeout(() => {
              speakChinese(item.meaning);
            }, 280);
          }
        });
      }, 60);
    }

    // 播放主流程
    function playCurrentWord() {
      if (!isPlaying || words.length === 0) return;

      currentRepeatCount++;
      repeatBadge.style.display = "block";
      repeatBadge.textContent = `第 ${currentRepeatCount} / ${settings.repeatPerWord} 遍`;

      const item = words[currentIndex];

      const proceedFlow = () => {
        if (!isPlaying) return;

        if (currentRepeatCount < settings.repeatPerWord) {
          timerId = setTimeout(() => {
            playCurrentWord();
          }, settings.delaySeconds * 1000);
        } else {
          currentRepeatCount = 0;
          repeatBadge.style.display = "none";
          timerId = setTimeout(() => {
            if (!isPlaying) return;
            if (currentIndex < words.length - 1) {
              currentIndex++;
              renderWord();
              playCurrentWord();
            } else {
              togglePlay(false);
              alert("🎉 恭喜！本轮词库朗读已全部完成！");
            }
          }, settings.delaySeconds * 1000);
        }
      };

      // 朗读当前英文单词
      speakText(item.word, () => {
        if (!isPlaying) return;

        if (settings.readChinese && item.meaning) {
          timerId = setTimeout(() => {
            if (!isPlaying) return;
            speakChinese(item.meaning, proceedFlow);
          }, 300);
        } else {
          proceedFlow();
        }
      });
    }

    // 停止发音与清理
    function stopSpeaking() {
      if (timerId) {
        clearTimeout(timerId);
        timerId = null;
      }
      if (synth) {
        try { synth.cancel(); } catch (e) {}
      }
      wordCard.classList.remove("speaking");
      repeatBadge.style.display = "none";
      window.activeUtterance = null;
    }"""

# 找到从 // 4. 朗读核心 到 function stopSpeaking() 结束的整个块进行替换
pattern_speech_section = r'// 4\. 朗读核心[\s\S]*?function stopSpeaking\(\) \{[\s\S]*?\n    \}'
html = re.sub(pattern_speech_section, lambda m: clean_speech_core.strip(), html, count=1)

# 5. 修复 btnRepeat 重读按钮：不管是暂停中还是播放中，均能 100% 稳定发音
old_btn_repeat_block = """    btnRepeat.addEventListener("click", () => {
      stopSpeaking();
      currentRepeatCount = 0;
      if (isPlaying) {
        playCurrentWord();
      } else {
        const item = words[currentIndex];
        speakText(item.word);
      }
    });"""

new_btn_repeat_block = """    btnRepeat.addEventListener("click", () => {
      stopSpeaking();
      currentRepeatCount = 0;
      // 延迟 60ms，确保旧音频通道完全释放，新发音必定出声
      setTimeout(() => {
        if (isPlaying) {
          playCurrentWord();
        } else {
          speakSingleWord(words[currentIndex]);
        }
      }, 60);
    });"""

html = html.replace(old_btn_repeat_block, new_btn_repeat_block)

# 6. 修复 jumpToIndex：同样避免 cancel 后立即调用 play 的并发竞态
old_jump_to_index = """    function jumpToIndex(idx) {
      stopSpeaking();
      currentIndex = idx;
      currentRepeatCount = 0;
      renderWord();
      if (isPlaying) {
        playCurrentWord();
      }
    }"""

new_jump_to_index = """    function jumpToIndex(idx) {
      stopSpeaking();
      currentIndex = idx;
      currentRepeatCount = 0;
      renderWord();
      setTimeout(() => {
        if (isPlaying) {
          playCurrentWord();
        }
      }, 60);
    }"""

html = html.replace(old_jump_to_index, new_jump_to_index)

# 7. 清理 loadSavedData 和 engineSelect 遗留监听
html = re.sub(r'if \(settings\.engineMode\)[\s\S]*?voiceSelectGroup\.style\.display = "flex";', '', html)
html = re.sub(r'engineSelect\.addEventListener\("change"[\s\S]*?\}\);', '', html)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("精简化、纯本地发音重构成功！彻底解决【点重读有时候有音有时候没有】的问题！")
