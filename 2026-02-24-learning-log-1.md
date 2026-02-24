---
layout: default
title: 2026-02-24 第一天：使用 GitHub Pages 打造個人部落格
nav_order: -20260224
---

# 今日學習總結：從零開始的 GitHub Pages 之旅

今天是專案開發的第一天，我成功建立了自己的學習日誌網站，並了解了靜態網站建置的核心觀念。

## 1. 熟悉 Git/GitHub 與 IDE 的運作方式
學會了如何使用 PyCharm 這個強大的 IDE 與 GitHub 進行連動。了解到不需要每次都依賴終端機輸入繁瑣的指令，透過 PyCharm 內建的 Git 面板，我可以很視覺化地完成：
- **存檔與版控：** 編輯器會幫我 Auto-save，而 Commit 則是幫程式碼拍下一張安全的「快照」。
- **提交流程：** 熟練了 `Commit` (填寫有意義的 Log) 並且 `Push` 到遠端伺服器的工作流。

## 2. GitHub Pages 與 just-the-docs 主題
了解到不需要架設複雜的伺服器或是安裝像 WordPress 這樣的 CMS 系統。
只要將 `just-the-docs-template` 複製到自己的 Repository 中，修改 `_config.yml` 裡的 `title` 與 `url`，GitHub Actions 就會在背後自動幫我啟動 Jekyll 引擎，將 Markdown 檔編譯成漂亮的 HTML 靜態網頁。

## 3. 深入理解 YAML Front Matter
寫在每篇 `.md` 檔案最上方的 `---` 區塊，是專門寫給 Jekyll 引擎看的設定檔。

### 3.1 `nav_order` 與檔案命名策略
為了解決未來文章越來越多所導致的「排序地獄」，我學到了最佳實務 (Best Practice)：
- **檔名加上日期：** 例如 `2026-02-24-learning-log-1.md`，讓本地端資料夾內的檔案能自動按時間排序，且產生的 URL 也更具專業感。
- **使用負數日期排序：** 設定 `nav_order: -20260224`。因為系統預設數字小的排在前面，加上負號後，就能讓「最新的文章」永遠自動置頂於左側的導覽列之中。

### 3.2 練習 Markdown 語法
這篇文章本身就是最好的練習！我使用了：
- 大標題 (`#`) 與中標題 (`##`)
- 無序清單 (`-`)
- 粗體字強調重點 (`**粗體**`)
- 行內程式碼標記 (`` `程式碼` ``)

明天見！
