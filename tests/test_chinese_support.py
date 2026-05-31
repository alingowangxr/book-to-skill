#!/usr/bin/env python3
"""
book-to-skill 中文支援測試腳本

測試項目：
  1. 中文文字書 (TXT) — 章節檢測、目錄檢測、token 估算
  2. 中文技術書 (MD)  — 代碼塊保留、表格保留
  3. 繁體中文書 (HTML) — 編碼檢測、HTML 提取
  4. 中文與英文混合內容
  5. 編碼自動檢測 (GB18030 / BIG5)

用法：
  python3 tests/test_chinese_support.py

執行前需要：
  pip3 install chardet  (可選，編碼檢測測試需要)
"""

import json
import os
import re
import sys
import tempfile
from pathlib import Path

# 加入專案根目錄到 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.extract import (
    estimate_tokens,
    detect_structure,
    detect_chinese_toc,
    detect_chinese_encoding,
    extract_html_file,
    read_text_file,
    extract_html_content,
)

TESTS_DIR = Path(__file__).resolve().parent
PASS = 0
FAIL = 0


def test(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        print(f"  [PASS] {name}")
        PASS += 1
    else:
        print(f"  [FAIL] {name} - {detail}")
        FAIL += 1


def load_text(filename: str) -> str:
    path = TESTS_DIR / filename
    content = read_text_file(str(path))
    if content is None:
        print(f"  [!] Could not read {filename}")
        return ""
    return content


def run_tests():
    print("=" * 60)
    print("[book-to-skill] Chinese Support Test Suite")
    print("=" * 60)

    # ─────────────────────────────────────────────
    # 測試 1：中文文字書 (TXT)
    # ─────────────────────────────────────────────
    print("\n[Test 1] Chinese Text Book (TXT)")
    text = load_text("chinese-book-simple.txt")
    test("1.1 讀取中文 TXT 成功", bool(text))

    # 編碼測試
    test("1.2 UTF-8 編碼正確", "變數" in text, "未找到中文字元")

    # Token 估算
    tokens = estimate_tokens(text)
    test("1.3 Token 估算 > 0", tokens > 0, f"tokens={tokens}")
    test("1.4 Token 估算合理", 100 < tokens < 5000, f"tokens={tokens}")

    # 章節檢測
    structure = detect_structure(text)
    test(
        "1.5 章節檢測 > 0",
        structure["chapters_detected"] > 0,
        f"chapters={structure['chapters_detected']}",
    )
    test(
        "1.6 至少檢測到 5 章",
        structure["chapters_detected"] >= 5,
        f"chapters={structure['chapters_detected']}",
    )

    # 目錄檢測
    test("1.7 目錄檢測成功", structure["has_toc"], "未檢測到目錄")

    # 章節樣本
    test(
        "1.8 章節樣本包含中文",
        any("第" in h for h in structure["chapter_headings_sample"]),
        f"headings={structure['chapter_headings_sample']}",
    )

    # 中文內容標記
    has_chinese = bool(re.findall(r"[\u4e00-\u9fff]", text))
    test("1.9 中文內容檢測", has_chinese)

    # ─────────────────────────────────────────────
    # 測試 2：中文技術書 (MD)
    # ─────────────────────────────────────────────
    print("\n[Test 2] Chinese Technical Book (MD)")
    md_text = load_text("chinese-book-technical.md")
    test("2.1 讀取中文 MD 成功", bool(md_text))

    # 代碼塊保留
    code_blocks = len(re.findall(r"```", md_text))
    test("2.2 代碼塊 > 0", code_blocks > 0, f"code_blocks={code_blocks}")

    # 表格保留
    tables = len(re.findall(r"\|.*\|", md_text))
    test("2.3 表格行 > 0", tables > 0, f"table_rows={tables}")

    # JavaScript 關鍵字
    test("2.4 包含技術內容", "const" in md_text and "function" in md_text)

    # 中英混合檢測
    test("2.5 中英混合內容", "閉包" in md_text and "closure" not in md_text)

    # 章節檢測（MD 有 ## 標題）
    md_structure = detect_structure(md_text)
    test(
        "2.6 MD 章節檢測",
        md_structure["chapters_detected"] > 0,
        f"chapters={md_structure['chapters_detected']}",
    )

    # ─────────────────────────────────────────────
    # 測試 3：繁體中文書 (HTML)
    # ─────────────────────────────────────────────
    print("\n[Test 3] Traditional Chinese Book (HTML)")
    html_text = extract_html_file(str(TESTS_DIR / "chinese-book-traditional.html"))
    if html_text is None:
        print("  [!] Could not extract HTML")
    else:
        test("3.1 HTML 提取成功", bool(html_text.strip()))
        test("3.2 繁體中文保留", "機器學習" in html_text, "未找到繁體中文字元")
        test("3.3 程式碼保留", "perceptron" in html_text, "程式碼遺失")
        test("3.4 表格內容保留", "資訊增益" in html_text, "表格內容遺失")

    # ─────────────────────────────────────────────
    # 測試 4：中文編碼檢測
    # ─────────────────────────────────────────────
    print("\n[Test 4] Chinese Encoding Detection")
    try:
        import chardet

        text_bytes = text.encode("utf-8")
        encoding = detect_chinese_encoding(text_bytes)
        test("4.1 UTF-8 編碼檢測", encoding == "utf-8", f"encoding={encoding}")

        gb_bytes = text.encode("gb18030")
        encoding = detect_chinese_encoding(gb_bytes)
        test("4.2 GB18030 編碼檢測", encoding == "gb18030", f"encoding={encoding}")

        big5_bytes = html_text.encode("big5") if html_text else "測試".encode("big5")
        encoding = detect_chinese_encoding(big5_bytes)
        test("4.3 BIG5 編碼檢測", encoding == "big5", f"encoding={encoding}")
    except ImportError:
        print("  [!] Skipping encoding test (requires chardet)")

    # ─────────────────────────────────────────────
    # 測試 5：中文目錄檢測
    # ─────────────────────────────────────────────
    print("\n[Test 5] Chinese Table of Contents Detection")
    test("5.1 TXT 目錄檢測", detect_chinese_toc(text), "未檢測到 TXT 目錄")
    test("5.2 MD 目錄檢測", detect_chinese_toc(md_text), "未檢測到 MD 目錄")

    # 邊界案例
    test("5.3 空字串不回傳 True", not detect_chinese_toc(""), "空字串誤判為目錄")
    test(
        "5.4 英文不回傳 True",
        not detect_chinese_toc("Table of Contents"),
        "英文目錄不應由 detect_chinese_toc 檢測",
    )

    # ─────────────────────────────────────────────
    # 測試 6：Token 估算準確性
    # ─────────────────────────────────────────────
    print("\n[Test 6] Token Estimation Accuracy")
    pure_english = "Hello world this is a test " * 100
    tokens_en = estimate_tokens(pure_english)
    test("6.1 英文 token 估算", tokens_en > 0, f"tokens={tokens_en}")

    pure_chinese = "中文測試" * 100
    tokens_cn = estimate_tokens(pure_chinese)
    test("6.2 中文 token 估算", tokens_cn > 0, f"tokens={tokens_cn}")

    mixed = "Python 是一種程式語言 " * 50
    tokens_mixed = estimate_tokens(mixed)
    test("6.3 混合 token 估算", tokens_mixed > 0, f"tokens={tokens_mixed}")

    # 中文 token 應小於字元數（因為 1 token ≈ 1.5 字元）
    test(
        "6.4 中文 token < 字元數",
        tokens_cn < len(pure_chinese),
        f"tokens={tokens_cn}, chars={len(pure_chinese)}",
    )

    # ─────────────────────────────────────────────
    # 測試 7：整本書提取模擬
    # ─────────────────────────────────────────────
    print("\n【測試 7】整本書提取模擬")
    # 模擬 extract.py 的 main 函數邏輯
    test_files = {
        "chinese-book-simple.txt": "TXT",
        "chinese-book-technical.md": "MD",
        "chinese-book-traditional.html": "HTML",
    }

    for filename, fmt in test_files.items():
        filepath = TESTS_DIR / filename
        if filename.endswith(".html"):
            content = extract_html_file(str(filepath))
        elif filename.endswith(".txt") or filename.endswith(".md"):
            content = load_text(filename)
        else:
            content = load_text(filename)
        tokens = estimate_tokens(content)
        structure = detect_structure(content)
        has_chinese = bool(re.findall(r"[\u4e00-\u9fff]", content))

        test(
            f"7.{list(test_files.keys()).index(filename) + 1} [{fmt}] 提取成功",
            bool(content),
        )
        test(
            f"7.{list(test_files.keys()).index(filename) + 1}b "
            f"[{fmt}] 中文檢測={has_chinese}",
            has_chinese,
        )
        test(
            f"7.{list(test_files.keys()).index(filename) + 1}c "
            f"[{fmt}] 章節={structure['chapters_detected']}>0",
            structure["chapters_detected"] > 0,
        )

    # ─────────────────────────────────────────────
    # 總結
    # ─────────────────────────────────────────────
    print("\n" + "=" * 60)
    total = PASS + FAIL
    print(f"Results: {PASS}/{total} passed", end="")
    if FAIL > 0:
        print(f"  ({FAIL} failed)")
    else:
        print(" - ALL PASSED!")
    print("=" * 60)

    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(run_tests())
