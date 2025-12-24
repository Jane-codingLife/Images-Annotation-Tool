# Image Annotation Tool

一個使用 Tkinter + Pillow 製作的圖片標註工具。

## 功能
- 資料夾圖片瀏覽
- Canvas 圖片顯示與自動縮放
- 文字標註與自動儲存
- SQLite 儲存標註資料
- Image 放大檢視

## 專案結構
- controllers：資料流控制
- models：圖片與資料庫存取
- views：UI 與 Image 獨立檢視

## 執行方式
```bash
# requirements.txt (最低可執行環境清單) 
# pip install -r (一次將清單全安裝好)
pip install -r requirements.txt
python main.py
