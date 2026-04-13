# 📄 Maritime OCR Pipeline (海事知識預處理管線)

本專案旨在解決海軍工程、輪機專業書籍（多為大型簡體 PDF）的數位化與知識檢索問題。透過自動化腳本，將 PDF 轉換為結構良好的繁體 Markdown 文件，以便匯入 NotebookLM 或進行 RAG 分析。

## 🛠️ 技術棧
- **Python**: 核心邏輯處理。
- **PyMuPDF (fitz)**: PDF 解析與 TOC 提取。
- **pymupdf4llm**: 高品質 Markdown 轉換。
- **OpenCC**: 簡繁轉換 (s2twp 台灣慣用語模式)。
- **Docker**: (計畫中) 提供穩定的環境隔離。

## 📁 結構說明
- `maritime_preprocessor.py`: PDF 轉 Markdown 的核心處理腳本。
- `maritime_custom_dict.json`: 針對輪機專業詞彙的校正對應表。
- `docker-ocr-cmd.sh`: 執行 OCR 的指令模板。
- `requirements.txt`: 必要元件清單。

## 🚀 快速開始
1. 將 PDF 放入 `inbox/` 資料夾。
2. 執行 `python maritime_preprocessor.py`。
3. 在 `processed/` 資料夾查看成果。

---

*「將厚重的課本轉化為流動的數據。」*
