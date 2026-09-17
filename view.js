#!/usr/bin/env node

/**
 * 雅思基础核心词汇 2588 终端全景交互查看器
 * 零外部依赖，纯原生 Node.js，支持 Windows 终端彩色卡片、翻页、快跳、搜索、发音朗读
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const { exec } = require('child_process');

// 保证 Windows 终端 UTF-8 编码
if (process.platform === 'win32') {
  try {
    exec('chcp 65001');
  } catch (e) {}
}

const wordsFile = path.join(__dirname, 'words.json');
if (!fs.existsSync(wordsFile)) {
  console.error('\x1b[31m[错误] 找不到词库文件: ' + wordsFile + '\x1b[0m');
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
  bgHighlight: '\x1b[43;30m', // 搜索高亮背景
};

// 获取终端适宜排版宽度
function getCardWidth() {
  const cols = process.stdout.columns || 80;
  return Math.max(50, Math.min(84, cols - 6));
}

// 格式化全景卡片
function renderCard(item, index, highlightKeyword = '') {
  const width = getCardWidth();
  const numStr = `#${index + 1}`;
  const wordStr = item.word;
  let phoneticStr = '';
  if (item.phonetic) {
    const rawPh = item.phonetic.startsWith('/') ? item.phonetic : `/${item.phonetic}/`;
    phoneticStr = `   ${c.brightMagenta}${rawPh}${c.reset}`;
  }

  // 搜索关键字高亮
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

function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// 单词发音 (Windows 原生 SpeechSynthesizer)
function speakWord(word) {
  if (process.platform === 'win32') {
    const safeWord = word.replace(/'/g, "''");
    exec(`powershell -NoProfile -Command "(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('${safeWord}')"`, () => {});
  }
}

// -------------------------------------------------------------
// 命令行参数快捷模式 (非交互)
// -------------------------------------------------------------
const args = process.argv.slice(2);
if (args.length > 0) {
  const arg1 = args[0].toLowerCase();

  // 1. 字母直达: 如 view a 或 node view.js b
  if (arg1.length === 1 && arg1 >= 'a' && arg1 <= 'z') {
    const matched = words.map((w, idx) => ({ ...w, origIdx: idx })).filter(w => w.word.toLowerCase().startsWith(arg1));
    console.log(`\n${c.bold}${c.brightCyan}📖 雅思核心词库 · 字母 [${arg1.toUpperCase()}] 分组 (共 ${matched.length} 词)${c.reset}\n`);
    matched.forEach(item => {
      console.log(renderCard(item, item.origIdx));
    });
    process.exit(0);
  }

  // 2. 搜索模式: 如 view /finance 或 view 词义
  if (arg1.startsWith('/') || isNaN(arg1)) {
    const query = arg1.startsWith('/') ? arg1.slice(1) : arg1;
    const matched = words.map((w, idx) => ({ ...w, origIdx: idx })).filter(w => 
      w.word.toLowerCase().includes(query) || (w.meaning && w.meaning.includes(query))
    );
    console.log(`\n${c.bold}${c.brightGreen}🔍 搜索 [${query}] 匹配结果 (共 ${matched.length} 词)${c.reset}\n`);
    matched.slice(0, 50).forEach(item => {
      console.log(renderCard(item, item.origIdx, query));
    });
    if (matched.length > 50) {
      console.log(`${c.yellow}⚠️ 仅展示前 50 条匹配，可直接运行无需参数进入交互翻页模式。${c.reset}`);
    }
    process.exit(0);
  }

  // 3. 数字区间: 如 view 1 20 (从第1个打印到第20个)
  const startNum = parseInt(arg1, 10);
  const count = args[1] ? parseInt(args[1], 10) : 10;
  const startIdx = Math.max(0, Math.min(words.length - 1, startNum - 1));
  const slice = words.slice(startIdx, startIdx + count);
  console.log(`\n${c.bold}${c.brightCyan}📖 雅思核心词库 · #${startIdx + 1} ~ #${startIdx + slice.length} (共 ${slice.length} 词)${c.reset}\n`);
  slice.forEach((item, i) => {
    console.log(renderCard(item, startIdx + i));
  });
  process.exit(0);
}

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

function saveProgress(idx) {
  try {
    const payload = {
      lastIndex: idx,
      lastWord: words[idx] ? words[idx].word : '',
      pageSize: pageSize,
      updatedAt: new Date().toISOString()
    };
    fs.writeFileSync(progressFile, JSON.stringify(payload, null, 2), 'utf8');
  } catch (e) {}
}

// -------------------------------------------------------------
// 交互模式 (Interactive Mode)
// -------------------------------------------------------------
const savedProgress = loadProgress();
let currentIndex = savedProgress ? savedProgress.lastIndex : 0;
let pageSize = savedProgress && savedProgress.pageSize ? savedProgress.pageSize : 5;
let welcomeMessage = savedProgress 
  ? `欢迎回来！已自动恢复上次阅读进度：#${savedProgress.lastIndex + 1} "${savedProgress.lastWord}"` 
  : '';

function clearScreen() {
  try {
    console.clear();
  } catch (e) {
    process.stdout.write('\x1b[2J\x1b[0;0H');
  }
}

function displayCurrentPage(message = '', searchKeyword = '') {
  // 每次翻页或变动位置自动持久化保存进度
  saveProgress(currentIndex);

  clearScreen();
  const width = getCardWidth();
  const endIdx = Math.min(words.length, currentIndex + pageSize);
  const currentWord = words[currentIndex] ? words[currentIndex].word : '';
  const currentLetter = currentWord ? currentWord[0].toUpperCase() : '';

  console.log(
    `${c.bold}${c.brightCyan}📖 雅思基础核心词汇 2,588 终端全景查看器${c.reset}  ` +
    `${c.dim}[字母: ${c.brightYellow}${currentLetter}${c.reset}${c.dim} · #${currentIndex + 1}~#${endIdx} / 共 ${words.length} 词 · 每页 ${pageSize} 词]${c.reset}`
  );
  console.log(`${c.gray}${'─'.repeat(width)}${c.reset}`);

  for (let i = currentIndex; i < endIdx; i++) {
    console.log(renderCard(words[i], i, searchKeyword));
  }

  console.log(`${c.gray}${'─'.repeat(width)}${c.reset}`);
  const showMsg = message || welcomeMessage;
  if (showMsg) {
    console.log(`${c.brightYellow}🔔 ${showMsg}${c.reset}`);
    welcomeMessage = ''; // 欢迎提示仅在启动时显示一次
  }
  console.log(
    `${c.bold}快捷指令:${c.reset} ` +
    `[${c.brightGreen}Enter${c.reset}:下页] ` +
    `[${c.brightGreen}b${c.reset}:上页] ` +
    `[${c.brightGreen}:a~:z${c.reset}:跳字母] ` +
    `[${c.brightGreen}:序号${c.reset}:跳词] ` +
    `[${c.brightGreen}:top${c.reset}:重置首词] ` +
    `[${c.brightGreen}/词${c.reset}:搜索] ` +
    `[${c.brightGreen}+/-${c.reset}:调页容] ` +
    `[${c.brightGreen}s${c.reset}:朗读] ` +
    `[${c.brightGreen}q${c.reset}:退出]`
  );
}

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: `${c.cyan}词库导航 > ${c.reset}`
});

displayCurrentPage();
rl.prompt();

rl.on('line', (line) => {
  const cmd = line.trim();

  if (cmd === 'q' || cmd === 'quit' || cmd === 'exit') {
    console.log(`\n${c.brightGreen}👋 备考加油，雅思 6.0 一战必过！${c.reset}\n`);
    process.exit(0);
  } else if (cmd === '' || cmd === 'n' || cmd === 'next') {
    if (currentIndex + pageSize < words.length) {
      currentIndex += pageSize;
      displayCurrentPage();
    } else {
      displayCurrentPage('已经到达词库末尾！');
    }
  } else if (cmd === 'b' || cmd === 'p' || cmd === 'prev') {
    if (currentIndex > 0) {
      currentIndex = Math.max(0, currentIndex - pageSize);
      displayCurrentPage();
    } else {
      displayCurrentPage('已经是最前一页！');
    }
  } else if (cmd === '+' || cmd === '=') {
    pageSize = Math.min(50, pageSize + 5);
    displayCurrentPage(`每页展示数已调整为: ${pageSize} 词`);
  } else if (cmd === '-' || cmd === '_') {
    pageSize = Math.max(3, pageSize - 5);
    displayCurrentPage(`每页展示数已调整为: ${pageSize} 词`);
  } else if (cmd.startsWith(':size')) {
    const s = parseInt(cmd.replace(':size', '').trim(), 10);
    if (!isNaN(s) && s > 0) {
      pageSize = Math.min(100, s);
      displayCurrentPage(`每页展示数已调整为: ${pageSize} 词`);
    }
  } else if (cmd === 's' || cmd === 'speak' || cmd === 'play') {
    const w = words[currentIndex].word;
    speakWord(w);
    displayCurrentPage(`正在朗读当前首词: "${w}"`);
  } else if (cmd.startsWith(':')) {
    const target = cmd.slice(1).trim().toLowerCase();
    if (target === 'top' || target === 'reset' || target === 'first' || target === 'start') {
      currentIndex = 0;
      displayCurrentPage('已回到词库首词 (#1)');
    } else if (/^\d+$/.test(target)) {
      const targetNum = parseInt(target, 10);
      currentIndex = Math.max(0, Math.min(words.length - pageSize, targetNum - 1));
      displayCurrentPage(`已跳转至序号 #${targetNum}`);
    } else if (target.length === 1 && target >= 'a' && target <= 'z') {
      const idx = words.findIndex(w => w.word.toLowerCase().startsWith(target));
      if (idx !== -1) {
        currentIndex = idx;
        displayCurrentPage(`已跳转至字母 [${target.toUpperCase()}] 开头`);
      } else {
        displayCurrentPage(`词库中无 [${target.toUpperCase()}] 开头的单词`);
      }
    } else {
      displayCurrentPage(`无效跳转，格式如 ':a'、':500' 或 ':top'`);
    }
  } else if (cmd.startsWith('/') || cmd.startsWith('?')) {
    const query = cmd.slice(1).trim().toLowerCase();
    if (query) {
      const idx = words.findIndex(w => 
        w.word.toLowerCase().includes(query) || (w.meaning && w.meaning.includes(query))
      );
      if (idx !== -1) {
        currentIndex = idx;
        displayCurrentPage(`找到匹配 "${query}" 的词条: #${idx + 1} "${words[idx].word}"`, query);
      } else {
        displayCurrentPage(`未找到包含 "${query}" 的词条`);
      }
    }
  } else if (/^\d+$/.test(cmd)) {
    const targetNum = parseInt(cmd, 10);
    currentIndex = Math.max(0, Math.min(words.length - pageSize, targetNum - 1));
    displayCurrentPage(`已跳转至序号 #${targetNum}`);
  } else if (cmd.length === 1 && cmd.toLowerCase() >= 'a' && cmd.toLowerCase() <= 'z') {
    const letter = cmd.toLowerCase();
    const idx = words.findIndex(w => w.word.toLowerCase().startsWith(letter));
    if (idx !== -1) {
      currentIndex = idx;
      displayCurrentPage(`已跳转至字母 [${letter.toUpperCase()}] 开头`);
    }
  } else {
    // 默认执行搜索
    const query = cmd.toLowerCase();
    const idx = words.findIndex(w => 
      w.word.toLowerCase().includes(query) || (w.meaning && w.meaning.includes(query))
    );
    if (idx !== -1) {
      currentIndex = idx;
      displayCurrentPage(`找到匹配 "${query}" 的词条: #${idx + 1} "${words[idx].word}"`, query);
    } else {
      displayCurrentPage(`未找到相关词条，可输入 /关键词 搜索`);
    }
  }

  rl.prompt();
});
