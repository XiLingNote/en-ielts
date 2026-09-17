#!/usr/bin/env node

/**
 * 雅思基础核心词汇 2588 - 终端查看器 (带微服务生产日志伪装模式)
 * 零外部依赖，纯原生 Node.js
 * 支持微服务日志流伪装 (Stealth Log)、全景卡片模式 (Card)、断点续读、语音朗读
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const { exec } = require('child_process');

// 统一 UTF-8 编码
if (process.platform === 'win32') {
  try {
    exec('chcp 65001');
  } catch (e) {}
}

// 终端窗口标题伪装 (彻底隐藏雅思/背词字眼)
function setTerminalTitle(title) {
  process.stdout.write(`\x1b]0;${title}\x07`);
}
setTerminalTitle('spring-boot:run (app-service-gateway.log)');

const wordsFile = path.join(__dirname, 'words.json');
if (!fs.existsSync(wordsFile)) {
  console.error('\x1b[31m[ERROR] Missing dataset file: ' + wordsFile + '\x1b[0m');
  process.exit(1);
}

const words = JSON.parse(fs.readFileSync(wordsFile, 'utf8'));

// ANSI 颜色方案
const c = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  dim: '\x1b[2m',
  underline: '\x1b[4m',
  cyan: '\x1b[36m',
  brightCyan: '\x1b[96m',
  green: '\x1b[32m',
  brightGreen: '\x1b[92m',
  yellow: '\x1b[33m',
  brightYellow: '\x1b[93m',
  magenta: '\x1b[35m',
  brightMagenta: '\x1b[95m',
  white: '\x1b[37m',
  gray: '\x1b[90m',
  bgHighlight: '\x1b[43;30m',
};

// -------------------------------------------------------------
// 进度持久化记忆 (断点续读功能)
// -------------------------------------------------------------
const progressFile = path.join(__dirname, '.progress.json');

function loadProgress() {
  try {
    if (fs.existsSync(progressFile)) {
      const data = JSON.parse(fs.readFileSync(progressFile, 'utf8'));
      if (typeof data.lastIndex === 'number' && data.lastIndex >= 0 && data.lastIndex < words.length) {
        return data;
      }
    }
  } catch (e) {}
  return null;
}

function saveProgress(idx, mode, size) {
  try {
    const payload = {
      lastIndex: idx,
      lastWord: words[idx] ? words[idx].word : '',
      viewMode: mode,
      pageSize: size,
      updatedAt: new Date().toISOString()
    };
    fs.writeFileSync(progressFile, JSON.stringify(payload, null, 2), 'utf8');
  } catch (e) {}
}

const savedProgress = loadProgress();
let currentIndex = savedProgress ? savedProgress.lastIndex : 0;
let viewMode = savedProgress && savedProgress.viewMode ? savedProgress.viewMode : 'log'; // 默认'log'微服务日志伪装模式，或'card'全景卡片模式
let pageSize = savedProgress && savedProgress.pageSize ? savedProgress.pageSize : 5;

// 获取终端宽度
function getTerminalWidth() {
  return Math.max(60, Math.min(100, (process.stdout.columns || 85) - 4));
}

function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// -------------------------------------------------------------
// 渲染器 1：微服务生产日志流 (思路1 · 最强摸鱼伪装)
// -------------------------------------------------------------
function renderLogLine(item, index, highlightKeyword = '') {
  const now = new Date();
  const timeStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ` +
                  `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}.` +
                  `${String(100 + (index % 899)).padStart(3, '0')}`;

  const thread = `[nio-8080-exec-${(index % 8) + 1}]`;
  const level = `${c.green}INFO ${c.reset}`;
  const logger = `${c.cyan}c.m.service.LexiconRegistry${c.reset}`;
  const idxStr = `#${String(index + 1).padStart(4, '0')}`;

  const rawWord = item.word;
  const rawPhonetic = item.phonetic ? ` (${item.phonetic.replace(/^\/|\/$/g, '')})` : '';
  let meaning = item.meaning || '';

  // 关键词高亮
  let wordDisplay = `${c.brightYellow}"${rawWord}"${c.reset}`;
  if (highlightKeyword) {
    const reg = new RegExp(`(${escapeRegExp(highlightKeyword)})`, 'gi');
    wordDisplay = wordDisplay.replace(reg, `${c.bgHighlight}$1${c.reset}`);
    meaning = meaning.replace(reg, `${c.bgHighlight}$1${c.reset}`);
  }

  return `${c.gray}${timeStr}${c.reset} ${c.dim}${thread}${c.reset} ${level} ${logger} - [${c.brightCyan}${idxStr}${c.reset}] token=${wordDisplay}${c.magenta}${rawPhonetic}${c.reset} :: ${c.white}${meaning}${c.reset}`;
}

// -------------------------------------------------------------
// 渲染器 2：全景卡片模式 (可按 m 随时切回)
// -------------------------------------------------------------
function renderCard(item, index, highlightKeyword = '') {
  const width = getTerminalWidth();
  const numStr = `#${index + 1}`;
  const wordStr = item.word;
  let phoneticStr = '';
  if (item.phonetic) {
    const rawPh = item.phonetic.startsWith('/') ? item.phonetic : `/${item.phonetic}/`;
    phoneticStr = `   ${c.brightMagenta}${rawPh}${c.reset}`;
  }

  let displayWord = `${c.bold}${c.brightYellow}${wordStr}${c.reset}`;
  let displayMeaning = item.meaning || '暂无释义';

  if (highlightKeyword) {
    const reg = new RegExp(`(${escapeRegExp(highlightKeyword)})`, 'gi');
    displayWord = displayWord.replace(reg, `${c.bgHighlight}$1${c.reset}${c.bold}${c.brightYellow}`);
    displayMeaning = displayMeaning.replace(reg, `${c.bgHighlight}$1${c.reset}${c.white}`);
  }

  const lineTop = `${c.gray}┌── ${c.brightCyan}${c.bold}${numStr}${c.reset}${c.gray} ${'─'.repeat(Math.max(2, width - numStr.length - 5))}${c.reset}`;
  const lineWord = `${c.gray}│${c.reset}   ${displayWord}${phoneticStr}`;
  const lineMeaning = `${c.gray}│${c.reset}   ${c.white}${displayMeaning}${c.reset}`;
  const lineBottom = `${c.gray}└${'─'.repeat(Math.max(4, width - 1))}${c.reset}`;

  return [lineTop, lineWord, lineMeaning, lineBottom].join('\n');
}

// 单词发音 (Windows 原生 SpeechSynthesizer)
function speakWord(word) {
  if (process.platform === 'win32') {
    const safeWord = word.replace(/'/g, "''");
    exec(`powershell -NoProfile -Command "(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('${safeWord}')"`, () => {});
  }
}

// -------------------------------------------------------------
// 命令行非交互快捷打印
// -------------------------------------------------------------
const args = process.argv.slice(2);
if (args.length > 0) {
  const arg1 = args[0].toLowerCase();

  // 1. 字母直达: 如 view a
  if (arg1.length === 1 && arg1 >= 'a' && arg1 <= 'z') {
    const matched = words.map((w, idx) => ({ ...w, origIdx: idx })).filter(w => w.word.toLowerCase().startsWith(arg1));
    console.log(`\n${c.gray}[cluster-prod-node01] filter=prefix:${arg1.toUpperCase()} total=${matched.length}${c.reset}\n`);
    matched.forEach(item => {
      console.log(viewMode === 'card' ? renderCard(item, item.origIdx) : renderLogLine(item, item.origIdx));
    });
    process.exit(0);
  }

  // 2. 搜索模式: 如 view /finance
  if (arg1.startsWith('/') || isNaN(arg1)) {
    const query = arg1.startsWith('/') ? arg1.slice(1) : arg1;
    const matched = words.map((w, idx) => ({ ...w, origIdx: idx })).filter(w => 
      w.word.toLowerCase().includes(query) || (w.meaning && w.meaning.includes(query))
    );
    console.log(`\n${c.gray}[cluster-prod-node01] grep="${query}" matched=${matched.length}${c.reset}\n`);
    matched.slice(0, 50).forEach(item => {
      console.log(viewMode === 'card' ? renderCard(item, item.origIdx, query) : renderLogLine(item, item.origIdx, query));
    });
    process.exit(0);
  }

  // 3. 数字范围: 如 view 1 5
  const startNum = parseInt(arg1, 10);
  const count = args[1] ? parseInt(args[1], 10) : 5;
  const startIdx = Math.max(0, Math.min(words.length - 1, startNum - 1));
  const slice = words.slice(startIdx, startIdx + count);
  slice.forEach((item, i) => {
    console.log(viewMode === 'card' ? renderCard(item, startIdx + i) : renderLogLine(item, startIdx + i));
  });
  process.exit(0);
}

// -------------------------------------------------------------
// 交互模式 (Interactive Mode)
// -------------------------------------------------------------
function clearScreen() {
  try {
    console.clear();
  } catch (e) {
    process.stdout.write('\x1b[2J\x1b[0;0H');
  }
}

let initialWelcome = savedProgress 
  ? `Restored session offset: #${savedProgress.lastIndex + 1} (${savedProgress.lastWord})`
  : '';

function displayCurrentPage(message = '', searchKeyword = '') {
  saveProgress(currentIndex, viewMode, pageSize);
  clearScreen();

  const width = getTerminalWidth();
  const endIdx = Math.min(words.length, currentIndex + pageSize);
  const currentWord = words[currentIndex] ? words[currentIndex].word : '';
  const currentLetter = currentWord ? currentWord[0].toUpperCase() : '';

  if (viewMode === 'log') {
    // 伪装微服务实时日志头部
    console.log(`${c.gray}[cluster-prod-01] tail -f /var/log/app-service.log (PID: 19482, offset: #${currentIndex + 1}~#${endIdx} / ${words.length})${c.reset}`);
    console.log(`${c.gray}${'─'.repeat(width)}${c.reset}`);

    for (let i = currentIndex; i < endIdx; i++) {
      console.log(renderLogLine(words[i], i, searchKeyword));
    }

    console.log(`${c.gray}${'─'.repeat(width)}${c.reset}`);
    const showMsg = message || initialWelcome;
    if (showMsg) {
      console.log(`${c.dim}[system] ${showMsg}${c.reset}`);
      initialWelcome = '';
    }
    console.log(
      `${c.dim}[Enter:next] [b:prev] [:a~:z:group] [:num:offset] [/key:grep] [s:ping] [m:mode] [q:exit]${c.reset}`
    );
  } else {
    // 全景卡片模式
    console.log(
      `${c.bold}${c.brightCyan}📖 雅思核心基础词汇 2,588 查看器${c.reset}  ` +
      `${c.dim}[字母: ${c.brightYellow}${currentLetter}${c.reset}${c.dim} · #${currentIndex + 1}~#${endIdx} / 共 ${words.length} 词 · 每页 ${pageSize} 词]${c.reset}`
    );
    console.log(`${c.gray}${'─'.repeat(width)}${c.reset}`);

    for (let i = currentIndex; i < endIdx; i++) {
      console.log(renderCard(words[i], i, searchKeyword));
    }

    console.log(`${c.gray}${'─'.repeat(width)}${c.reset}`);
    const showMsg = message || initialWelcome;
    if (showMsg) {
      console.log(`${c.brightYellow}🔔 ${showMsg}${c.reset}`);
      initialWelcome = '';
    }
    console.log(
      `${c.bold}快捷指令:${c.reset} ` +
      `[${c.brightGreen}Enter${c.reset}:下页] ` +
      `[${c.brightGreen}b${c.reset}:上页] ` +
      `[${c.brightGreen}:a~:z${c.reset}:跳字母] ` +
      `[${c.brightGreen}:序号${c.reset}:跳词] ` +
      `[${c.brightGreen}/词${c.reset}:搜索] ` +
      `[${c.brightGreen}m${c.reset}:切模式] ` +
      `[${c.brightGreen}s${c.reset}:朗读] ` +
      `[${c.brightGreen}q${c.reset}:退出]`
    );
  }
}

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: viewMode === 'log' ? `${c.green}app@cluster-node01:~$ ${c.reset}` : `${c.cyan}词库导航 > ${c.reset}`
});

displayCurrentPage();
rl.prompt();

rl.on('line', (line) => {
  const cmd = line.trim();

  if (cmd === 'q' || cmd === 'quit' || cmd === 'exit') {
    if (viewMode === 'log') {
      console.log(`\n${c.gray}[system] Process detached from session (PID: 19482). Bye.${c.reset}\n`);
    } else {
      console.log(`\n${c.brightGreen}👋 备考加油，雅思 6.0 一战必过！${c.reset}\n`);
    }
    process.exit(0);
  } else if (cmd === 'm' || cmd === 'mode') {
    // 一键切换模式：log 日志流 vs card 全景卡片
    viewMode = (viewMode === 'log') ? 'card' : 'log';
    rl.setPrompt(viewMode === 'log' ? `${c.green}app@cluster-node01:~$ ${c.reset}` : `${c.cyan}词库导航 > ${c.reset}`);
    displayCurrentPage(`Switched view mode to: [${viewMode.toUpperCase()}]`);
  } else if (cmd === '' || cmd === 'n' || cmd === 'next') {
    if (currentIndex + pageSize < words.length) {
      currentIndex += pageSize;
      displayCurrentPage();
    } else {
      displayCurrentPage('Reached end of event stream');
    }
  } else if (cmd === 'b' || cmd === 'p' || cmd === 'prev') {
    if (currentIndex > 0) {
      currentIndex = Math.max(0, currentIndex - pageSize);
      displayCurrentPage();
    } else {
      displayCurrentPage('Already at beginning');
    }
  } else if (cmd === '+' || cmd === '=') {
    pageSize = Math.min(50, pageSize + 5);
    displayCurrentPage(`Buffer window adjusted to: ${pageSize}`);
  } else if (cmd === '-' || cmd === '_') {
    pageSize = Math.max(2, pageSize - 5);
    displayCurrentPage(`Buffer window adjusted to: ${pageSize}`);
  } else if (cmd.startsWith(':size')) {
    const s = parseInt(cmd.replace(':size', '').trim(), 10);
    if (!isNaN(s) && s > 0) {
      pageSize = Math.min(100, s);
      displayCurrentPage(`Buffer window adjusted to: ${pageSize}`);
    }
  } else if (cmd === 's' || cmd === 'ping' || cmd === 'speak') {
    const w = words[currentIndex].word;
    speakWord(w);
    displayCurrentPage(viewMode === 'log' ? `Ping audio frame sent for [${w}] (200 OK)` : `正在朗读当前首词: "${w}"`);
  } else if (cmd.startsWith(':')) {
    const target = cmd.slice(1).trim().toLowerCase();
    if (target === 'top' || target === 'reset' || target === 'first' || target === 'start') {
      currentIndex = 0;
      displayCurrentPage('Reset stream to offset #1');
    } else if (/^\d+$/.test(target)) {
      const targetNum = parseInt(target, 10);
      currentIndex = Math.max(0, Math.min(words.length - pageSize, targetNum - 1));
      displayCurrentPage(`Jumped to offset #${targetNum}`);
    } else if (target.length === 1 && target >= 'a' && target <= 'z') {
      const idx = words.findIndex(w => w.word.toLowerCase().startsWith(target));
      if (idx !== -1) {
        currentIndex = idx;
        displayCurrentPage(`Filtered to group [${target.toUpperCase()}]`);
      } else {
        displayCurrentPage(`No entries for group [${target.toUpperCase()}]`);
      }
    } else {
      displayCurrentPage(`Invalid argument, e.g. ':a', ':500' or ':top'`);
    }
  } else if (cmd.startsWith('/') || cmd.startsWith('?')) {
    const query = cmd.slice(1).trim().toLowerCase();
    if (query) {
      const idx = words.findIndex(w => 
        w.word.toLowerCase().includes(query) || (w.meaning && w.meaning.includes(query))
      );
      if (idx !== -1) {
        currentIndex = idx;
        displayCurrentPage(`Grep match found: #${idx + 1} "${words[idx].word}"`, query);
      } else {
        displayCurrentPage(`No grep match for "${query}"`);
      }
    }
  } else if (/^\d+$/.test(cmd)) {
    const targetNum = parseInt(cmd, 10);
    currentIndex = Math.max(0, Math.min(words.length - pageSize, targetNum - 1));
    displayCurrentPage(`Jumped to offset #${targetNum}`);
  } else if (cmd.length === 1 && cmd.toLowerCase() >= 'a' && cmd.toLowerCase() <= 'z') {
    const letter = cmd.toLowerCase();
    const idx = words.findIndex(w => w.word.toLowerCase().startsWith(letter));
    if (idx !== -1) {
      currentIndex = idx;
      displayCurrentPage(`Filtered to group [${letter.toUpperCase()}]`);
    }
  } else {
    const query = cmd.toLowerCase();
    const idx = words.findIndex(w => 
      w.word.toLowerCase().includes(query) || (w.meaning && w.meaning.includes(query))
    );
    if (idx !== -1) {
      currentIndex = idx;
      displayCurrentPage(`Grep match found: #${idx + 1} "${words[idx].word}"`, query);
    } else {
      displayCurrentPage(`Unknown command, use /keyword to grep`);
    }
  }

  rl.prompt();
});
