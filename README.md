# 外匯內部證照整合題庫

將 113 與 114 年度外匯內部證照題目整合成單一靜態網頁，支援手機與桌機瀏覽。

## 內容

- `quiz.html`: 主題庫頁面，整合 113 與 114 共 640 題
- `index.html`: 入口頁，會導向 `quiz.html`
- `113-interactive.html`: 舊入口，相容導向 `quiz.html`
- `data113.js`: 113 年題庫資料
- `data114.js`: 114 年題庫資料
- `assets/113-crops/`: 113 年逐題圖片題卡
- `scripts/`: 產生 113 年資料的輔助腳本
- 原始 PDF 題本與答案檔

## 使用方式

直接在本機啟動靜態網站：

```bash
cd /Users/changivan/Downloads/外匯內部證照Test
python3 -m http.server 8080 --bind 127.0.0.1
```

瀏覽器開啟：

- `http://127.0.0.1:8080/`
- `http://127.0.0.1:8080/quiz.html`

## Cloudflare Tunnel

若已將子網域指向本機靜態網站，可使用：

- `https://fx.ivan-house.com/`

## 備註

- 113 年題目以原題圖方式呈現，搜尋依 OCR 擷取之題幹文字。
- 114 年題目以文字題卡方式呈現。
- 作答進度使用瀏覽器 `localStorage` 儲存，各裝置分開記錄。
