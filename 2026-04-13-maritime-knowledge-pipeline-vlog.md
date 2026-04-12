---
layout: default
title: "Vlog：建立我的輪機知識預處理流水線"
parent: Learning Logs
nav_order: -20260413
---

# ⚓ Vlog：從數位荒漠到知識綠洲 —— 輪機預處理流水線的誕生

*   **日期：** 2026/04/13
*   **心情：** 突破重圍的成就感
*   **關鍵字：** #RAG #輪機工程 #自動化 #NotebookLM

---

## 📽️ 紀錄背景

在我的海事考證之路上，我擁有上百本專業的輪機書籍，但它們大多數是「掃描版 PDF」。這意味著：
1.  **搜尋不能**：沒有文字層，無法搜尋關鍵字。
2.  **AI 無能**：直接丟給 NotebookLM，它只能看到一片像素，RAG (檢索增強生成) 效果極差。
3.  **體積臃腫**：動輒 100MB+ 的檔案，不符合現代 AI 工具的限制。

今天，我初步完成了這套專為輪機專業打造的「自動化預處理流水線」**構想與基礎架構**。目前程式碼正在密集編寫中，尚未進行大規模測試，但整體的知識提取藍圖已經清晰。

---

## 🏗️ 系統架構構想 (Architectural Concept)

這套流水線不只是簡單的格式轉換，而是一場對知識的「提取手術」，我們規劃了以下四大核心模塊：

1.  **Docker OCR (骨架重塑)**：
    利用多核心 CPU 調用 `OCRmyPDF`，將簡體掃描件轉化為可搜尋的文字層，同時進行體積優化。這是所有運算的基礎。
2.  **智慧目錄識別 (邏輯掃描 - 研發中)**：
    針對無書籤的電子書，規劃透過自動掃描目錄頁，利用正規表達式 (Regex) 智慧匹配章節與頁碼，實現自動化切片，這是目前最具挑戰性的部分。
3.  **S2T 與專業辭典複寫 (文化轉譯)**：
    整合 `OpenCC` 並掛載自定義的 `maritime_dict.json`。這步的目的是在轉換為繁體的過程中，強制修正輪機專業術語（如：泵 -> 幫浦），確保 AI 理解不偏差。
4.  **Markdown 與圖片自動嵌入**：
    預期產出結構乾淨的 Markdown，並在提取圖片的同時，於文字檔中自動標記圖片編號，達成圖文互參。

---

## 📉 預期目標與反思

### ⚠️ 現狀聲明 (Status Update)
> [!WARNING]
> 目前專案處於**架構準備階段 (Architecting Phase)**。腳本已完成初步邏輯撰寫，但尚未通過穩定性測試與海量資料驗證。

### 🧪 預期指標 (Expected Goals)
- **檢索精準度**：目標提升 70% (透過 MD 格式優化 NotebookLM 抓取)。
- **自動化程度**：實現「放進檔案 -> 執行腳本 -> 得到結果」的零干預流程。
- **詞彙正確率**：透過人工持續維護的辭典，達成專業術語的高精準轉換。

### 💡 心得筆記
「資料管理不等於知識管理。」
過去我只是在收集 PDF，現在我想嘗試如何「喚醒」這些知識。雖然目前還在架構階段，但這個過程讓我重新思考了海事技術文件的數位價值。

這不僅是為了解決這次考試，更是為了建立一套能跟隨我一輩子的個人技術手冊。

---

## 🗺️ 下一步 (The Roadmap)
- [ ] 完成核心腳本 `maritime_preprocessor.py` 的首輪測試。
- [ ] 驗證目錄識別演算在不同掃描品質下的表現。
- [ ] 擴展 `maritime_custom_dict.json` 的術語收錄範圍。

---

> **相關程式碼參考：**
> - [maritime_preprocessor.py](file:///c:/Users/vicme/.gemini/antigravity/scratch/my_learning_blog/scripts/maritime_preprocessor.py)
> - [maritime_custom_dict.json](file:///c:/Users/vicme/.gemini/antigravity/scratch/my_learning_blog/scripts/maritime_custom_dict.json)
