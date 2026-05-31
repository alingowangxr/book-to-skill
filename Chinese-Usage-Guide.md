# 🇨🇳 book-to-skill 中文書籍使用指南

## 簡介

book-to-skill 支援將中文技術書籍轉換為結構化的 Agent 技能。
本文檔提供完整的中文書籍處理流程與範例。

---

## 1. 快速開始

### 1.1 安裝與設定

```bash
# 確保在 Claude Code 或 Amp 環境中已安裝 book-to-skill
# 如果有新的腳本更新，請拉取最新版本
```

### 1.2 處理中文 PDF 書籍

```bash
# 交互模式（推薦）：會詢問書籍類型，選擇 "Chinese / CJK"
/book-to-skill ~/books/python-ru-men.pdf

# 指定中文模式（跳過交互詢問）
/book-to-skill ~/books/深入理解計算機系統.pdf --mode chinese

# 指定 slug 名稱
/book-to-skill ~/books/數據密集型應用系統設計.pdf ddia-chinese
```

### 1.3 處理中文 EPUB 書籍

```bash
# EPUB 會自動檢測中文內容，無需指定模式
/book-to-skill ~/books/重構改善既有代碼設計.epub

# 或使用明確 slug
/book-to-skill ~/books/領域驅動設計.epub ddd-chinese
```

### 1.4 處理中文純文字/TXT/Markdown 文件

```bash
# 自動檢測編碼（支援 UTF-8、GB18030、BIG5）
/book-to-skill ~/notes/系統設計面試.md
```

---

## 2. 完整工作流程範例

### 2.1 範例：處理《Python 從入門到實踐》

**Step 1: 執行轉換**
```bash
$ /book-to-skill ~/Downloads/python-crash-course.pdf python-crash-course-zh

> "What kind of content does this book have?"
> 3  # 選擇 "Chinese / CJK"
```

**預期輸出：**
```
🀄 Chinese/CJK mode selected — using Chinese-optimized extraction...
Extracting PDF: ~/Downloads/python-crash-course.pdf
Mode: chinese — using Chinese-optimized extraction...
Trying pdftotext with Chinese layout... OK

Extraction complete:
   Format  : PDF
   Method  : pdftotext-chinese
   Pages   : 356
   Words   : 98,432
   Chinese : 45,321 chars detected
   Tokens  : ~48K
   Chapters: 20 detected
   ToC     : yes
```

**Step 2: 確認成本估算**
```
📖 Source detected: python-crash-course.pdf (PDF)
📄 Pages: ~356 | Words: ~98K | Source tokens: ~48K

💰 Estimated token cost (Full Conversion):
   Input:  ~62K tokens
   Output: ~29K tokens
   Total:  ~91K tokens

➡  Proceed with Full Conversion?
```

**Step 3: 選擇目的**
```
> "What should this skill help you do?"
> 1  # Apply the author's frameworks while working
```

**Step 4: 生成完成**
```
✅ Skill created: ~/.config/agents/skills/python-crash-course-zh/

📚 Book: Python 從入門到實踐 — Eric Matthes
📄 Pages: ~356 | Chapters: 20

Files generated:
  SKILL.md         — core frameworks + index    (~4K tokens)
  chapters/        — 20 chapter summaries       (~1K each, ~20K total)
  glossary.md      — key terms                  (~1.5K tokens)
  patterns.md      — techniques & patterns      (~2K tokens)
  cheatsheet.md    — quick reference            (~1K tokens)
  ─────────────────────────────────────────────────────
  Total skill size: ~28.5K tokens
```

### 2.2 使用生成的技能

```bash
# 載入核心框架
/python-crash-course-zh

# 查詢特定主題（AI 會自動讀取相關章節）
/python-crash-course-zh 列表推導式
/python-crash-course-zh 類別繼承
/python-crash-course-zh 異常處理

# 讀取特定章節
/python-crash-course-zh ch08
/python-crash-course-zh ch15

# 瀏覽所有章節
/python-crash-course-zh "你有什麼章節？"
/python-crash-course-zh "what chapters do you have?"
```

---

## 3. 中文書籍處理提示

### 3.1 PDF 處理建議

| 書籍類型 | 建議模式 | 原因 |
|----------|----------|------|
| 中文程式設計書 | `--mode chinese` | 保留代碼佈局 |
| 中文管理/社科書籍 | `--mode chinese` | 優化文字提取 |
| 中英混雜技術書 | `--mode chinese` | 自動檢測編碼 |
| 掃描版中文 PDF | `--mode technical` | 使用 Docling OCR 佈局重構 |

### 3.2 編碼相容性

```bash
# 如果遇到編碼問題，確認文件編碼
file -I ~/books/chinese-book.pdf
# 或使用 Python 檢測
python3 -c "
with open('~/books/chinese-book.pdf', 'rb') as f:
    import chardet
    print(chardet.detect(f.read(10000)))
"
```

支援的編碼順序：
1. UTF-8 with BOM (`utf-8-sig`)
2. UTF-8
3. **GB18030**（GB2312/GBK 超集）
4. **BIG5**（繁體中文）
5. CP1252
6. Latin-1

### 3.3 繁簡體書籍

book-to-skill 支援繁體和簡體中文書籍：

```bash
# 繁體中文書籍（自動檢測 BIG5 編碼）
/book-to-skill ~/books/TAOCP-中文版.epub taocp-chinese

# 簡體中文書籍
/book-to-skill ~/books/演算法導論.pdf algorithms-cn
```

### 3.4 生成後的技能使用

中文技能支援中英文查詢：

```bash
# 中文查詢
/ddia-chinese 複製與分區
/ddia-chinese 一致性哈希

# 英文查詢
/ddia-chinese replication
/ddia-chinese consistent hashing

# 混合查詢
/ddia-chinese 第5章 replication
```

---

## 4. 進階使用

### 4.1 手動指定編碼

如果需要手動指定編碼，可以直接修改提取後的文件：

```bash
# 提取後，如果發現亂碼，可以手動轉換編碼
iconv -f gb18030 -t utf-8 /tmp/book_skill_work/full_text.txt -o /tmp/book_skill_work/full_text_utf8.txt

# 然後重新運行生成步驟
```

### 4.2 自定義中文框架提取

在 SKILL.md 生成過程中，AI 會自動：
1. 保留中文框架/術語原名
2. 在括號中提供英文翻譯（如有需要）
3. 按照中文語義結構組織知識

範例輸出：
```markdown
## Core Frameworks & Mental Models

### 依賴注入 (Dependency Injection)
Use `依賴注入` when a class needs external services without hard-coding their implementations.
- **When to use**: A module depends on abstractions, not concrete implementations
- **How**: Pass dependencies through constructors or setters
- **Anti-pattern**: 服務定位器 (Service Locator) — hides dependencies, makes testing harder

### 開閉原則 (Open/Closed Principle)
Classes should be open for extension but closed for modification.
- **When to use**: Adding new behavior without changing existing code
- **How**: Use polymorphism, composition, or strategy pattern
```

### 4.3 處理混合語言書籍

許多技術書包含中英混合內容。chinese 模式會自動處理：

```bash
# 中英混合書籍：比如代碼注釋是英文但正文是中文
/book-to-skill ~/books/flask-web開發.pdf flask-cn
```

生成的技能會保留：
- 英文程式碼片段（保持原樣）
- 中文框架解釋（翻譯 + 原文對照）
- 中英雙語術語表

---

## 5. 常見問題

### Q1: 提取後出現亂碼？
A: 嘗試使用 technical 模式：
```bash
/book-to-skill ~/book.pdf --mode chinese
```
如果仍然亂碼，可能是 PDf 編碼特殊，請在 [GitHub Issues](https://github.com/virgiliojr94/book-to-skill/issues) 回報。

### Q2: 章節檢測不準確？
A: 目前支援的模式：
- `第X章`（第1章、第一章、第百章）
- `第X節`、`第X节`
- `一、`、`二、`等中文數字序列
- 英文 `Chapter N`、`Section N`

如果您的書使用其他格式，請提供樣例。

### Q3: 可以處理繁體中文嗎？
A: 可以。`read_text_file()` 會自動嘗試 `big5` 編碼。

### Q4: Token 估算準確嗎？
A: 中文使用字元數估算（1 token ≈ 1.5 字元），英文使用單詞估算。混合內容使用混合算法。誤差通常在 ±20% 以內。

### Q5: 如何貢獻中文支援改進？
A: 歡迎 PR！改進方向包括：
- 更多中文章節格式支援
- 更好的中文分詞（可選 jieba 整合）
- 中文 NLP 框架提取
- 測試用例貢獻

---

## 6. 實戰案例

### 案例：從《領域驅動設計》中文版建立技能

```bash
# 執行轉換
/book-to-skill ~/books/領域驅動設計-中文版.pdf ddd-cn

# 使用技能進行開發
/ddd-cn 聚合根設計
  → AI 自動讀取相關章節，提供聚合根設計原則和範例

/ddd-cn 限界上下文
  → 解釋限界上下文的概念、識別方法和實作建議

/ddd-cn ch04
  → 載入第4章：領域隔離
```

### 案例：從《數據密集型應用系統設計》建立實戰技能

```bash
/book-to-skill ~/downloads/DDIA-中文版.pdf ddia-cn

# 在系統設計面試中使用
/ddia-cn 數據複製策略
/ddia-cn 分區方法比較
/ddia-cn 一致性模型

# 在架構設計中使用
/ddia-cn 選擇 NoSQL 還是 SQL
/ddia-cn 事務隔離級別
```

---

## 7. 技術參考

### 支援的中文章節格式

| 格式 | 範例 | 支援狀態 |
|------|------|----------|
| 「第」+數字+「章」 | 第1章、第12章 | ✅ |
| 「第」+中文數字+「章」 | 第一章、第十二章 | ✅ |
| 「第」+數字+「節/节」 | 第1節、第2节 | ✅ |
| 中文數字+「、」 | 一、、二、 | ✅ |
| 數字+點+空格 | 1. 概述 | ✅ |
| 英文 Chapter N | Chapter 5 | ✅ |

### 提取方式比較

| 模式 | 適用場景 | 速度 | 品質 |
|------|----------|------|------|
| `--mode chinese` | 中文技術書籍 | ⚡ 快 | ⭐⭐⭐ |
| `--mode technical` | 中英混雜 + 複雜排版 | 🐢 慢 | ⭐⭐⭐⭐⭐ |
| `--mode text` | 純文字中文書 | ⚡ 快 | ⭐⭐ |
| `--mode chinese` + Docling | 掃描版中文 PDF | 🐢 慢 | ⭐⭐⭐⭐⭐ |

---

## 附錄：快速命令參考

```bash
# 基本轉換
/book-to-skill <path> [slug]

# 中文模式轉換
/book-to-skill <path> --mode chinese

# 指定 slug
/book-to-skill ~/book.pdf my-chinese-skill

# 僅分析
/book-to-skill ~/book.pdf --analyze

# 使用已提取的分析結果生成
# 將分析報告提供給 AI，AI 會跳過提取步驟
```

---

> 問題或建議？請在 [GitHub Issues](https://github.com/virgiliojr94/book-to-skill/issues) 反饋。
