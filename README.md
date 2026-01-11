# Image Annotation Tool

一個使用 **Python + Tkinter** 開發的桌面應用程式，用於瀏覽本機圖片並為每張圖片建立對應的文字註記內容，已註記資料會儲存於 SQLite 資料庫中。

本專案以 **MVC 架構** 為核心設計，並刻意將 Controller 設計為可 API 化的形式，讓未來轉為 Web / Cloud 架構時可以低成本擴充。

---

## ✨ Features
- 本機圖片資料夾瀏覽
- 圖片切頁（上一張 / 下一張 / 指定索引 / 清單）
- 圖片與文字註記 一對一 關聯
- SQLite 儲存註記資料
- Dirty flag 機制，自動儲存，避免切頁時遺失註記
- 集中式 logging 設定
- 分層錯誤處理（工程師 log / 使用者提示）

---

## 🧠 Architecture Overview
### 本專案採用 **MVC（Model–View–Controller）架構**：

- **Model**
  - 圖片來源（Image Repository）
  - 資料庫存取（Annotation DB）
- **Controller**
  - 業務邏輯中樞
  - 負責圖片與註記的對應、接受與回應邏輯
  - 不包含任何 UI 控制程式碼
- **View**
  - Tkinter UI
  - 負責顯示畫面與使用者互動
  - 不直接操作資料庫或圖片來源

### 為什麼 Controller 可以視為 API？

#### Controller：
- 接收明確參數
- 回傳資料或拋出例外
- 不依賴 GUI 元件

#### 因此在未來可以：
- 被 Web API（FastAPI / Flask）直接重用
- 作為後端服務的一部分

---

## 📁 Project Structure

```text
Images-Annotation-Tool/
│
├─ controllers/
│   └─ image_controller.py      # 業務邏輯（可 API 化）
│
├─ models/
│   ├─ image_repository.py      # 圖片來源（目前為本機）
│   └─ annotation_db.py         # SQLite 資料庫操作
│
├─ views/
│   ├─ main_window.py           # Tkinter UI
│   └─ image_viewer.py          # 放大檢視圖片視窗
│
├─ config/
│   └─ logging_config.py        # 集中式 logging 設定
│
├─ main.py                      # 程式進入點
├─ requirements.txt
└─ README.md
```

---

## 🚀 Installation
> 使用虛擬環境可避免套件版本衝突，確保專案可重現性
```text
git clone https://github.com/Jane-codingLife/Images-Annotation-Tool.git
cd Images-Annotation-Tool

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

---

## ▶️ Usage
```commandline
python main.py
```
### 操作流程：
1. 啟動程式
2. 選擇資料庫檔案(.db)
3. 選擇圖片資料夾 
4. 使用 [上一張 / 下一張 / 清單] >> 瀏覽圖片
5. 在文字框輸入對應註記
6. 切頁時自動儲存註記資料

---

## ⚠ Error Handling & Logging

### Error Handling 設計原則

- **Model / Controller**
    - 拋出原始錯誤 
    - Controller 會將錯誤包裝成可理解的應用層錯誤

- **View**
    - 僅顯示整理過的錯誤訊息 
    - 不顯示 stack trace

#### 此設計可避免：
>    - UI 被技術細節污染
>    - 使用者看到不必要的錯誤資訊

### Logging 設計

- 使用集中式 `logging_config.py`
- 各模組使用 `logging.getLogger(__name__)`
- 依 logger hierarchy 區分模組來源 
- 詳細錯誤與 stack trace 僅寫入 log 檔，供工程師除錯使用

---

### 🧪 Testing（未來規劃）
為確保核心業務邏輯在功能擴充後仍保持正確性，未來將補上自動化測試：
- Controller 行為測試
- Dirty flag 儲存邏輯測試
- 資料庫寫入一致性測試

### 🔄 CI（未來規劃）
後續將導入 GitHub Actions：
- 每次 push 自動建立環境 
- 安裝相依套件 
- 執行測試 
- 確保專案可重現與穩定性

---

### 🌱 Future Improvements
- 雲端圖片來源（HTTP / S3 / GCS） 
- Web API（FastAPI） 
- 前後端分離 
- 使用者帳號與權限 
- 批次圖片管理功能