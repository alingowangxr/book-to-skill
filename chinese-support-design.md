# 中文書籍支持優化方案

## 一、現狀分析

### 1.1 已實現的支持
- ✅ Unicode 編碼支持（UTF-8、GBK、GB2312）
- ✅ 基本中文章節檢測（「第X章」格式）
- ✅ 中文目錄檢測（「目錄」「目录」）
- ✅ 中文 token 估算（字符數近似）

### 1.2 主要限制
| 限制類別 | 具體問題 | 影響程度 |
|----------|----------|----------|
| **文本提取** | PDF 中文布局可能錯位 | 高 |
| **結構檢測** | 複雜中文章節格式支持不足 | 高 |
| **分詞精度** | 無中文分詞，token 估算不準確 | 中 |
| **框架提取** | 無中文 NLP，框架識別依賴 AI 推理 | 中 |
| **編碼處理** | 部分中文編碼未覆蓋 | 低 |

## 二、優化方案

### 2.1 文本提取優化

#### 2.1.1 PDF 中文提取增強
```python
# 新增中文 PDF 提取策略
def extract_pdf_chinese(pdf_path: str, mode: str) -> str:
    """
    中文 PDF 提取策略：
    1. 優先使用 Docling（佈局感知，支持中文表格）
    2. 回退到 pdftotext + 中文布局優化
    3. 最終回退到 PyPDF2/pdfminer
    """
    if mode == "technical":
        # 技術書籍：Docling 最佳
        text = extract_with_docling(pdf_path)
        if text:
            return text
    
    # 中文文本優化：嘗試 pdftotext 的 -layout 模式
    text = extract_with_pdftotext_layout(pdf_path)
    if text:
        return text
    
    # 回退到標準提取
    return extract_with_pdftotext(pdf_path)
```

#### 2.1.2 編碼自動檢測與轉換
```python
def detect_and_convert_encoding(text: bytes) -> str:
    """
    自動檢測中文編碼並轉換
    支持：UTF-8, GB2312, GBK, GB18030, BIG5
    """
    import chardet
    
    # 檢測編碼
    detection = chardet.detect(text)
    encoding = detection['encoding']
    
    # 常見中文編碼映射
    chinese_encodings = {
        'gb2312': 'gb18030',  # gb18030 是 gb2312 的超集
        'gbk': 'gb18030',
        'big5': 'big5',
    }
    
    if encoding in chinese_encodings:
        encoding = chinese_encodings[encoding]
    
    try:
        return text.decode(encoding)
    except (UnicodeDecodeError, LookupError):
        # 回退到 utf-8 with errors='replace'
        return text.decode('utf-8', errors='replace')
```

### 2.2 結構檢測優化

#### 2.2.1 增強的中文章節模式
```python
def create_chinese_chapter_patterns():
    """創建全面的中文章節檢測模式"""
    patterns = {
        # 章級標題
        'chapter': [
            r'第[一二三四五六七八九十百千零\d]+章',
            r'第\d+章',
            r'Chapter\s+\d+',
            r'CHAPTER\s+\d+',
        ],
        # 節級標題
        'section': [
            r'第[一二三四五六七八九十百千零\d]+節',
            r'第\d+節',
            r'第[一二三四五六七八九十百千零\d]+节',
            r'第\d+节',
            r'Section\s+\d+',
        ],
        # 部分標題
        'part': [
            r'第[一二三四五六七八九十百千零\d]+部分',
            r'第\d+部分',
            r'Part\s+[IVX]+',
            r'PART\s+[IVX]+',
        ],
        # 數字+點格式
        'numbered': [
            r'^\d+\.\s+[^\d]',  # 1. 標題
            r'^\d+\.\d+\s+',    # 1.1 子標題
        ],
        # 中文數字+頓號格式
        'chinese_numbered': [
            r'^[一二三四五六七八九十]+、',  # 一、
            r'^[一二三四五六七八九十]+[．.]',  # 一. 或 一．
        ],
    }
    return patterns
```

#### 2.2.2 中文目錄檢測增強
```python
def detect_chinese_toc(text: str) -> bool:
    """檢測中文目錄"""
    toc_keywords = [
        # 繁體中文
        '目錄', '章節目錄', '本書目錄', '內容目錄',
        # 簡體中文
        '目录', '章节目录', '本书目录', '内容目录',
        # 混合格式
        '目 录', '目　录',
    ]
    
    lines = text[:50000].splitlines()
    for line in lines[:100]:  # 只檢查前100行
        line_stripped = line.strip()
        if line_stripped in toc_keywords:
            return True
    
    return False
```

### 2.3 Token 估算優化

#### 2.3.1 混合 token 估算算法
```python
def estimate_tokens_chinese(text: str) -> int:
    """
    改進的中文 token 估算
    考慮：中文字符、英文單詞、標點符號
    """
    import re
    
    # 統計中文字符
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]', text))
    
    # 統計英文單詞
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    
    # 統計數字
    numbers = len(re.findall(r'\d+', text))
    
    # 統計標點符號
    punctuation = len(re.findall(r'[^\w\s]', text))
    
    # 混合估算
    # 中文：1 token ≈ 1.5 字符
    # 英文：1 token ≈ 0.75 單詞
    # 數字：1 token ≈ 2 數字
    # 標點：不計入 token
    
    chinese_tokens = chinese_chars / 1.5
    english_tokens = english_words / 0.75
    number_tokens = numbers / 2
    
    total_tokens = chinese_tokens + english_tokens + number_tokens
    
    return max(int(total_tokens), 1)
```

### 2.4 中文框架提取工作流程

#### 2.4.1 中文框架提取步驟
```markdown
## 中文書籍框架提取流程

### Step 1: 中文文本預處理
1. 繁簡體統一（可選）
2. 中文分詞（使用 jieba）
3. 詞性標註
4. 命名實體識別

### Step 2: 框架識別
1. **核心概念提取**
   - 專有名詞（技術術語）
   - 方法論名稱（「XX方法」、「XX模型」）
   - 原則和規則（「XX原則」、「XX定律」）

2. **模式識別**
   - 「當...時，使用...」格式
   - 「首先...其次...最後...」步驟
   - 「避免...因為...」反模式

### Step 3: 框架結構化
```json
{
  "name": "框架名稱（中文）",
  "english_name": "Framework Name (英文)",
  "description": "框架描述",
  "when_to_use": "使用場景",
  "how_to_use": "使用步驟",
  "anti_patterns": ["反模式1", "反模式2"],
  "chapter": "章節引用"
}
```

### Step 4: 生成中文 SKILL.md
- 使用中文框架名稱
- 保留英文技術術語（如必要）
- 提供中英對照（可選）
```

## 三、技術實施

### 3.1 新增依賴
```python
# requirements-chinese.txt
chardet>=4.0.0          # 編碼檢測
jieba>=0.42.1           # 中文分詞（可選）
opencc-python-reimplemented>=0.1.6  # 繁簡轉換（可選）
```

### 3.2 代碼修改計劃

#### 3.2.1 修改 extract.py
1. 添加中文編碼檢測函數
2. 增強 PDF 中文提取策略
3. 改進結構檢測算法
4. 優化 token 估算

#### 3.2.2 修改 SKILL.md
1. 添加中文書籍處理指示
2. 更新步驟 3 的結構分析邏輯
3. 添加中文框架提取指南

### 3.3 測試策略

#### 3.3.1 測試用例
1. **中文技術書籍 PDF**
   - 包含代碼示例
   - 包含表格
   - 包含公式

2. **中文管理書籍**
   - 大段文字
   - 框架和模型
   - 案例研究

3. **繁簡體混合書籍**
   - 繁體中文書籍
   - 簡體中文書籍
   - 混合編碼書籍

#### 3.3.2 驗證指標
1. 章節檢測準確率
2. 框架提取完整性
3. Token 估算誤差率
4. 處理時間性能

## 四、實施路線圖

### 階段 1：基礎支持（1-2天）
- [x] 修改章節檢測模式
- [x] 添加中文目錄檢測
- [x] 改進 token 估算
- [ ] 添加中文編碼檢測

### 階段 2：提取優化（2-3天）
- [ ] 優化 PDF 中文提取
- [ ] 添加繁簡體轉換支持
- [ ] 測試各種中文格式

### 階段 3：框架提取（3-5天）
- [ ] 設計中文框架提取工作流程
- [ ] 添加中文 NLP 處理（可選）
- [ ] 創建中文 SKILL.md 模板

### 階段 4：測試與文檔（2-3天）
- [ ] 創建測試用例
- [ ] 編寫使用文檔
- [ ] 性能優化

## 五、風險與限制

### 5.1 技術風險
1. **中文分詞精度**: jieba 對技術術語可能不準確
2. **編碼兼容性**: 部分特殊編碼可能無法識別
3. **性能影響**: 中文處理可能增加提取時間

### 5.2 解決方案
1. **術語詞典**: 添加技術術語詞典提高分詞精度
2. **編碼回退**: 多層編碼檢測機制
3. **可選功能**: 中文 NLP 作為可選依賴

### 5.3 最壞情況
如果中文支持不理想，可以：
1. 回退到純文本提取
2. 依賴 AI 代理進行中文理解
3. 提供中文手動處理指南

## 六、預期成果

### 6.1 功能提升
1. 中文書籍章節檢測準確率 > 90%
2. 中文 token 估算誤差 < 20%
3. 支持常見中文編碼格式
4. 生成結構化的中文 SKILL.md

### 6.2 用戶體驗
1. 無需手動配置即可處理中文書籍
2. 自動識別中文章節結構
3. 生成可用的中文框架和模式
4. 保持與英文書籍相同的使用方式

### 6.3 兼容性
1. 向後兼容現有英文書籍處理
2. 不影響現有功能
3. 可選的中文增強功能