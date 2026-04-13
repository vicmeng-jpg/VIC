---
layout: default
title: Ship Exam Crawler
parent: Projects (專案中心)
nav_order: 1
---

# 船員評估試題 智慧批次爬蟲系統


這是一個使用 Python 撰寫的自動化爬蟲工具，可以進入[中華海員總工會官方網站](https://www.ncsu.org.tw/training4.php)自動獲取歷年梯次的「船員評估試題」。

## 功能特色
- 歷史資料探勘：支援自動往更舊的年度/梯次尋找。
- 智慧比對：會自動過濾並找出對應的科目檔案。
- 重複防重：若該科目檔案已完成下載，將自動忽略跳過，節省網路資源。
- 介面導向：全自動的互動對話終端機，選擇梯次與課目非常直觀。

## 目錄結構
- `crawler.py`: 爬蟲主程式
- `requirements.txt`: 第三方針對套件依賴清單

## 安裝方式
請確認您的電腦已經安裝 Python 3.8 或以上版本。開啟終端機並執行：
```bash
pip install -r requirements.txt
```

## 執行方式
```bash
python crawler.py
```
執行後依據畫面上的中文提示操作即可。
