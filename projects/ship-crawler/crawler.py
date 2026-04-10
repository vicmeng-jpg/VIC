import os
import re
import requests
import glob
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs

base_url = "https://www.ncsu.org.tw/"

def download_file(url, filename):
    print(f"    👉 下載中: {filename} ...", end="", flush=True)
    try:
        response = requests.get(url, stream=True, timeout=15)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(" ✅ 完成")
    except Exception as e:
        print(f" ❌ 失敗 ({e})")

def get_all_batches(session, max_pages=10):
    """取得所有梯次清單"""
    batches = []
    batch_map = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6'}
    start_url = "https://www.ncsu.org.tw/training4.php"
    
    print("正在掃描官方網站清單，請稍候...")
    for page in range(1, max_pages + 1):
        url = f"{start_url}?page={page}"
        try:
            resp = session.get(url, timeout=10)
            resp.raise_for_status()
        except:
            break
            
        soup = BeautifulSoup(resp.content, "html.parser")
        tests_1_links = soup.find_all('a', href=re.compile(r'tests_1\.php\?id='))
        
        if not tests_1_links:
            break
            
        for a in tests_1_links:
            title = a.get_text(strip=True)
            href = a.get('href')
            full_url = urljoin(base_url, href)
            
            m = re.search(r'(\d+)年(?:度)?(.+?)梯次', title)
            y, b = "未知", "未知"
            if m:
                y = m.group(1)
                b_raw = m.group(2).strip()
                
                # 若為正規的「第X梯次」，把「第」拔掉
                if b_raw.startswith('第'):
                    b = b_raw[1:]
                else:
                    b = b_raw
                    
                for k, v in batch_map.items():
                    b = b.replace(k, v)
                    
            batches.append({
                "year": y,
                "batch": b,
                "title": title,
                "url": full_url
            })
    return batches

def get_clean_text(element):
    """協助過濾不必要的換行與雜訊"""
    return " ".join(element.stripped_strings)

def normalize_text(text):
    """正規化字串，去除不必要的空白、括號、以及新舊制等干擾文字，並統一注音一與國字一"""
    if not text: return ""
    t = text.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "").replace("\xa0", "").replace("　", "")
    t = t.replace("◎", "").replace("新制", "").replace("舊制", "").replace("(", "").replace(")", "").replace("（", "").replace("）", "")
    t = t.replace("ㄧ", "一") # 注音的 ㄧ 換成國字的 一
    return t.strip()

def extract_subjects_from_page(t2_soup):
    """從科目頁面 (tests_2.php) 解析所有可用下載的科目名稱"""
    # 擴展支援各種常見的考題檔案附檔名
    pdf_links = t2_soup.find_all('a', href=re.compile(r'\.(pdf|xls|xlsx|doc|docx|zip)$', re.IGNORECASE))
    if not pdf_links:
        pdf_links = t2_soup.find_all('a', string=re.compile(r'下載'))
        
    subjects = []
    for a in pdf_links:
        # 通常科目名稱會跟下載連結放在同一個 <tr>
        tr = a.find_parent('tr')
        subj_name = ""
        if tr:
            # 取得整行文字，然後去掉多餘空白和"下載"字樣
            text = tr.get_text(" ", strip=True).replace("下載", "").strip()
            if text:
                subj_name = text
                
        # 備用方案: 從上一個節點找
        if not subj_name:
            prev = a.previous_sibling
            while prev:
                if prev.name is None:
                    t = str(prev).strip()
                    if t and t != '下載':
                        subj_name = t
                        break
                elif prev.name != 'a':
                    t = prev.get_text(strip=True)
                    if t and t != '下載':
                        subj_name = t
                        break
                prev = prev.previous_sibling
                
        if not subj_name:
            subj_name = f"未命名科目_{len(subjects)+1}"
            
        # 避免重複加入
        if subj_name not in [s["name"] for s in subjects]:
            subjects.append({"name": subj_name, "href": a.get("href")})
            
    return subjects

def main():
    print("========================================")
    print("🚢 船員評估試題 智慧批次爬蟲系統 啟動")
    print("========================================")
    session = requests.Session()
    
    # 步驟 1: 取得所有梯次與尋找起點
    batches = get_all_batches(session, max_pages=10)
    if not batches:
        print("無法取得網路資料。")
        return
        
    print(f"成功取得 {len(batches)} 筆梯次紀錄。")
    print("\n【步驟 1: 選擇起始梯次】")
    # 將所有年度撈出來並依照數字排序
    all_years = sorted(list(set(b["year"] for b in batches)), key=int, reverse=True)
    if all_years:
        print(f"目前系統收錄的年度範圍從 {all_years[-1]} 年 到 {all_years[0]} 年")
    
    # === 互動迴圈：選擇年度 ===
    while True:
        user_year = input(f"👉 請輸入起始「年度」 (例如: {all_years[0]}): ").strip()
        if user_year in all_years:
            break
        print(f"⚠️ 找不到 {user_year} 年度的資料，請重新輸入 (可選：{', '.join(all_years[:5])}...等)")
        
    year_batches = [b for b in batches if b["year"] == user_year]
    # 由於梯次有可能是「新增1」，我們讓它先對字串進行自訂排序：純數字排前面，文字排後面
    def sort_batch(x):
        return int(x) if x.isdigit() else (999, x)
    
    available_batch_nums = sorted(list(set(b["batch"] for b in year_batches)), key=sort_batch)
    print(f"\n✅ {user_year} 年度的可選梯次有： {', '.join(available_batch_nums)}")
    
    # === 互動迴圈：選擇梯次 ===
    while True:
        user_batch = input("👉 請輸入起始「梯次」: ").strip()
        if user_batch in available_batch_nums:
            break
        print(f"⚠️ 找不到第 {user_batch} 梯次，請重新輸入 (可選：{', '.join(available_batch_nums)})")
        
    # 找出該年度與梯次的起始 index
    start_index = 0
    for i, b in enumerate(batches):
        if b["year"] == user_year and b["batch"] == user_batch:
            start_index = i
            break
            
    start_batch = batches[start_index]
    print(f"\n✅ 鎖定起始梯次: {start_batch['title']}\n網址: {start_batch['url']}")
    
    # 步驟 2: 進入該梯次，選擇類別
    print("\n【步驟 2: 顯示類別連結 (確認id & Name_1=)】")
    try:
        t1_resp = session.get(start_batch['url'], timeout=10)
        t1_resp.raise_for_status()
    except Exception as e:
        print(f"無法讀取類別網頁: {e}")
        return
        
    t1_soup = BeautifulSoup(t1_resp.content, "html.parser")
    class_links = t1_soup.find_all('a', href=re.compile(r'tests_2\.php\?id='))
    if not class_links:
        print("此梯次找不到任何考試類別！")
        return
        
    classes = []
    for i, a in enumerate(class_links):
        href = a.get("href")
        qs = parse_qs(urlparse(href).query)
        # 精確從 URL 推論出 Name_1，若沒有再 fallback 到文字
        c_name = qs.get("Name_1", [a.get_text(strip=True)])[0]
        classes.append({"name": c_name, "href": href})
        print(f"  [{i+1}] {c_name}")
        
    class_choice = input(f"\n👉 請選擇您的類別編號 (1-{len(classes)}): ").strip()
    if not class_choice.isdigit() or not (1 <= int(class_choice) <= len(classes)):
        print("輸入無效，程式結束。")
        return
        
    selected_class = classes[int(class_choice)-1]
    target_class_name = selected_class["name"]
    print(f"\n✅ 已鎖定類別: {target_class_name}")
    
    # 步驟 3: 進入類別，選擇科目
    print("\n【步驟 3: 顯示有哪些科目】")
    t2_url = urljoin(base_url, selected_class["href"])
    try:
        t2_resp = session.get(t2_url, timeout=10)
        t2_resp.raise_for_status()
    except Exception as e:
        print(f"無法讀取科目網頁: {e}")
        return
        
    t2_soup = BeautifulSoup(t2_resp.content, "html.parser")
    subjects = extract_subjects_from_page(t2_soup)
    
    if not subjects:
        print("在此類別下找不到可下載的科目！")
        return
        
    for i, subj in enumerate(subjects):
        print(f"  [{i+1}] {subj['name']}")
        
    subj_choice = input(f"\n👉 請選擇要下載的科目，可多選，請用逗號隔開 (例如: 1,3) 或輸入 'all' 全選: ").strip().lower()
    
    chosen_subject_names = []
    if subj_choice == 'all':
        chosen_subject_names = [s["name"] for s in subjects]
    else:
        indices = [int(x.strip()) for x in subj_choice.split(',') if x.strip().isdigit()]
        for idx in indices:
            if 1 <= idx <= len(subjects):
                chosen_subject_names.append(subjects[idx-1]["name"])
                
    if not chosen_subject_names:
        print("沒有選擇任何科目，程式結束。")
        return
        
    print("\n✅ 選定要批次抓取的目標科目:")
    for c in chosen_subject_names:
        print(f"   - {c}")
        
    # 詢問是否要自動前進
    print("\n【準備就緒】")
    auto_mode = input("👉 批次下載這梯次後，是否要在歷史資料中「自動找尋下一梯(舊梯次)」並直接跳過無此類別梯次？(Y/n/Enter預設Yes): ").strip().lower()
    auto_mode = auto_mode in ['y', 'yes', '']
    
    # 步驟 4 & 5: 結合！開始巡迴處理
    print("\n========================================")
    print("【步驟 4&5: 批次下載與自動追溯開始】")
    print("========================================")
    for i in range(start_index, len(batches)):
        b = batches[i]
        print(f"\n[目標處理] {b['year']}年度 第{b['batch']}梯次")
        
        # === 啟動「預先檢查」機制 ===
        # 在發送網路請求前，先檢查是不是這個梯次我們要的科目都已經在電腦裡了
        all_exist = True
        missing_targets = []
        for target_name in chosen_subject_names:
            expected_prefix = f"{b['year']}_{b['batch']}_{target_name}".replace("/", "_")
            # 利用 glob 尋找任意副檔案名的檔案 (例如 .pdf, .xls)
            existing_files = glob.glob(f"{expected_prefix}.*")
            if existing_files:
                print(f"    [略過] {existing_files[0]} (資料夾下已有先前下載資料，不重複下載)")
            else:
                missing_targets.append(target_name)
                all_exist = False
                
        if all_exist:
            print("  ⏭️ 您選定的所有科目在此梯次都已經存在了，自動跳過網路尋找！")
            if not auto_mode:
                chk = input("\n👉 本梯次已存在。是否繼續往舊年度尋找？(y/N): ")
                if chk.strip().lower() not in ['y', 'yes']:
                    print("\n✅ 指令中止。")
                    break
            continue
            
        # 尋找這個梯次裡面的該類別
        try:
            t1_resp = session.get(b['url'], timeout=10)
            t1_soup = BeautifulSoup(t1_resp.content, "html.parser")
            
            # 尋找這個梯次裡面的該類別
            class_a = None
            norm_target_class = normalize_text(target_class_name)
            available_classes = []
            
            for a in t1_soup.find_all('a', href=re.compile(r'tests_2\.php\?id=')):
                qs = parse_qs(urlparse(a.get('href')).query)
                c_name = qs.get("Name_1", [a.get_text(strip=True)])[0]
                available_classes.append((c_name, a))
                
                if norm_target_class in normalize_text(c_name):
                    class_a = a
                    break
            
            if not class_a:
                print(f"  ⚠️ 警告：本梯次找不到舊類別名稱「{target_class_name}」")
                print("  這通常是因為早期考試制度沒有合併或名稱不同 (例如一二等分開)。請手動選擇對應的替代類別：")
                for c_idx, (c_name, _) in enumerate(available_classes):
                    print(f"    [{c_idx+1}] {c_name}")
                print("    [0] 直接跳過本梯次")
                
                while True:
                    ans = input("  👉 請選擇 (0 或對應編號): ").strip()
                    if ans == '0':
                        break
                    if ans.isdigit() and 1 <= int(ans) <= len(available_classes):
                        new_class_name, class_a = available_classes[int(ans)-1]
                        print(f"  ✅ 類別已重新切換為: {new_class_name} (後續更舊的梯次將自動沿用此名稱)")
                        target_class_name = new_class_name
                        break
                        
            if not class_a:
                print(f"  ⏭️ 確認跳過本梯次。")
                if not auto_mode:
                    chk = input("\n👉 是否繼續往舊年度尋找？(y/N): ")
                    if chk.strip().lower() not in ['y', 'yes']: break
                continue
                
            # 尋找類別內的該科目們
            t2_resp = session.get(urljoin(base_url, class_a['href']), timeout=10)
            t2_soup = BeautifulSoup(t2_resp.content, "html.parser")
            batch_subjects = extract_subjects_from_page(t2_soup)
            
            found_any = False
            # 只針對還沒下載的科目進行比對抓取
            for target_name in missing_targets:
                pdf_url = None
                norm_tgt = normalize_text(target_name)
                
                # 1. 從抽出來的列表正規化比對
                for bs in batch_subjects:
                    if norm_tgt in normalize_text(bs["name"]):
                        pdf_url = bs["href"]
                        break
                        
                # 2. 如果沒有，暴力遍歷當頁所有檔案連結，往上找整個區塊的純文字比對
                if not pdf_url:
                    all_pdf_links = t2_soup.find_all('a', href=re.compile(r'\.(pdf|xls|xlsx|doc|docx|zip)$', re.IGNORECASE))
                    if not all_pdf_links:
                        all_pdf_links = t2_soup.find_all('a', string=re.compile(r'下載'))
                        
                    for a in all_pdf_links:
                        parent = a.find_parent('tr') or a.find_parent('table') or a.find_parent()
                        if parent and norm_tgt in normalize_text(parent.get_text()):
                            pdf_url = a.get('href')
                            break
                                
                if pdf_url:
                    found_any = True
                    full_pdf_url = urljoin(base_url, pdf_url)
                    
                    # 取得雲端檔案真正的副檔名 (例如 .pdf 或 .xls)
                    ext = os.path.splitext(urlparse(full_pdf_url).path)[1]
                    if not ext: ext = ".pdf" # 備用防呆
                    
                    filename = f"{b['year']}_{b['batch']}_{target_name}{ext}".replace("/", "_")
                    download_file(full_pdf_url, filename)
                else:
                    print(f"    [未發現] 本梯次沒有 '{target_name}' 可下載")
                    
        except Exception as e:
            print(f"  ❌ 讀取時發生錯誤: {e}")
            continue
            
        if not auto_mode:
            chk = input("\n👉 本梯次處理完畢。是否繼續往舊年度尋找？(y/N): ")
            if chk.strip().lower() not in ['y', 'yes']:
                print("\n✅ 指令中止。")
                break
                
    if auto_mode:
       print("\n✅ 所有梯次掃描完畢！")

if __name__ == "__main__":
    main()
