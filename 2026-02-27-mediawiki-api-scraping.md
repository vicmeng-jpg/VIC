---
layout: default
title: "使用 PowerShell 與 MediaWiki API 抓取維基音檔"
parent: 我的學習日誌
nav_order: -20260227
---

# 使用 PowerShell 與 MediaWiki API 抓取維基音檔
**日期：2026-02-27**

今天在幫部落格文章嵌入維基百科（Wikimedia Commons）的音效檔《尼姆羅德》(Nimrod) 時，學到了一個很棒的網路爬蟲與 API 應用技巧。
### 思路
原本我以為只要在網頁上對著音檔按右鍵「複製連結」就可以了，但實務上常常會遇到兩個問題：
1. **網址不穩定**：維基百科的後台會將檔案打散在不同的雜湊資料夾中，直接複製的網址有時會失效。
2. **權限被拒 (403 Forbidden)**：如果直接使用 PowerShell 的 `Invoke-WebRequest` 去抓取某些公開頁面的網址，可能會被伺服器阻擋。
3. **考慮創用CC的問題**：如何避免繁瑣的人工CC檢查。

為了解決這個問題，我學習了如何正確地串接 **MediaWiki API（維基百科的官方開放 API）**，透過解析 JSON 格式的回應，來精準且合法地取得真實的下載連結與授權資訊。

---

## 實作步驟紀錄

### 第一步：向 MediaWiki API 請求檔案資訊 (JSON)

我們可以使用 PowerShell 的 `Invoke-RestMethod` 命令，向維基共享資源的 API 發送請求。這樣做會回傳結構化的 JSON 資料。

```powershell
$response = Invoke-RestMethod -Uri "https://commons.wikimedia.org/w/api.php?action=query&titles=File:Elgar;_Enigma_variations,_Theme_IX._Nimrod.ogg&prop=imageinfo&iiprop=url&format=json"
```

**API 參數解析：**
*   `action=query`：表示這是一個查詢動作。
*   `titles=File:...`：指定我們要查詢的目標檔案頁面名稱。
*   `prop=imageinfo` 及 `iiprop=url`：要求 API 回傳該檔案的**真實網址 (URL)**。
*   `format=json`：要求使用 JSON 格式回傳，方便程式後續讀取。

### 第二步：從 JSON 中精確萃取真實下載網址

API 會將結果放在一個隨機產生的頁面 ID（例如 `"-1"`）底下。我們需要動態取得這個 ID，才能深入 JSON 結構把 `url` 提取出來：

```powershell
# 1. 取得 API 回傳的所有頁面資料
$pages = $response.query.pages

# 2. 動態取得那串未知的頁面 ID (例如 "-1")
$firstKey = ($pages | Get-Member -MemberType NoteProperty)[0].Name 

# 3. 進入結構深處，把真實的 url 抓出來
$url = $pages.$firstKey.imageinfo[0].url 
```

此時，`$url` 變數裡面就會儲存著真正的下載路徑，例如：`https://upload.wikimedia.org/.../Elgar...Nimrod.ogg`。

### 第三步：正式下載音檔並存入專案

拿到正確且不會被阻擋的 URL 後，再使用 `Invoke-WebRequest`，將檔案從真實路徑下載下來，並存到專案的 `assets/` 資料夾中：

```powershell
Invoke-WebRequest -Uri $url -OutFile "c:\Users\vicme\.gemini\antigravity\scratch\my_learning_blog\assets\Nimrod.ogg"
```

### 第四步：確認版權宣告 (授權條款)

在使用網路資源時，確認授權條款非常重要。我們可以把剛才的第一步稍微修改，把屬性換成請求原數據（`iiprop=extmetadata`）：

```powershell
$response = Invoke-RestMethod -Uri "https://commons.wikimedia.org/w/api.php?action=query&titles=File:Elgar;_Enigma_variations,_Theme_IX._Nimrod.ogg&prop=imageinfo&iiprop=extmetadata&format=json"
```

解析這個回傳值後，我發現它標記為 `pd`（Public Domain 公有領域），表示不需要特別標註姓名標示（Attribution）。這讓我能在部落格文章中，安心地附上 `(Public Domain)` 的說明。

---

## 結論

這次的經驗讓我學到：**與其去網頁的 HTML 原始碼裡瞎猜或者處理可能會變動的網址，不如直接呼叫官方 API。** API 會直接告訴我們最標準、最新的正確資訊。這不僅提升了爬蟲的穩定度，也是更專業的開發方式！
