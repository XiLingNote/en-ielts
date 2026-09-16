import json
import re

md_path = r'C:\Users\Enmonster\OneDrive\英文\雅思基础核心词汇2683.md'
html_path = r'D:\workspace\english\index.html'

words = []
with open(md_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line.startswith('|'):
            continue
        parts = [p.strip() for p in line.split('|')[1:-1]]
        if len(parts) >= 4:
            idx, word, phonetic, meaning = parts[0], parts[1], parts[2], parts[3]
            if not idx.isdigit():
                continue
            words.append({
                'word': word.replace('*', '').strip(),
                'phonetic': phonetic.replace('`', '').strip(),
                'meaning': meaning.strip()
            })

print(f"成功从 Markdown 提取核心单词: {len(words)} 个")

# 导出备份 words.json
with open(r'D:\workspace\english\words.json', 'w', encoding='utf-8') as f:
    json.dump(words, f, ensure_ascii=False, indent=2)
print("已导出 words.json")

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 替换默认词库常量
pattern = r'const DEFAULT_WORDS = \[[\s\S]*?\n\s*\];'
replacement = 'const DEFAULT_WORDS = ' + json.dumps(words, ensure_ascii=False) + ';'
new_html, count = re.subn(pattern, replacement, html, count=1)
print(f"DEFAULT_WORDS 替换匹配数量: {count}")

# 替换标题等文案
new_html = new_html.replace('3000 英语单词循环朗读伴读助手', '雅思基础核心词汇 2683 朗读伴读助手')
new_html = new_html.replace('3000 单词朗读', '雅思 2683 词朗读')
new_html = new_html.replace('载入示例 (50词)', '重置为雅思 2683 词库')

# 保证旧缓存自动升级
new_html = re.sub(
    r'(words\s*=\s*JSON\.parse\(savedWords\);)',
    r'\1\n          if (!Array.isArray(words) || words.length <= 50) {\n            words = DEFAULT_WORDS;\n            localStorage.setItem("english_words_3000", JSON.stringify(words));\n          }',
    new_html
)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_html)

print("index.html 更新成功！")
