---
title: My Rag Demo
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

# LangChain RAG 系統 (前後端分離版)

這是一個基於 **LangChain**、**Google Gemini** (**Gemini 2.5 Flash**)、以及 **ChromaDB** 實作的 RAG (Retrieval-Augmented Generation, 檢索增強生成) 系統。
系統架構採用標準的**前後端分離 (Frontend-Backend Separation)** 設計，確保了程式碼的可維護性 (Clean Code) 與未來的擴充性。

## 系統架構

> **💡 進階閱讀推薦**
> 關於本專案的詳細開發歷程、踩坑紀錄 (包含 LangChain 版本升級與 Gemini 模型更名的應對)、以及 RAG 的核心理論與運作資料流解析，請參閱專案內的 [學習與開發紀錄報告 (learning_report.md)](./learning_report.md)。

1. **後端 (Backend API)**
   - **Framework**: FastAPI (Python)
     - *選擇原因*：輕量、高效、內建非同步 (Asynchronous) 支援與 Swagger UI，非常適合開發獨立的 Microservice 與 API 給前端呼叫。比起 Django 或 Flask，它更能體現現代化 Web API 的最佳實踐。
   - **LLM/Embedding**: Google Gemini (`models/gemini-2.5-flash`, `models/gemini-embedding-001`)
     - *選擇原因*：提供大額度免費額度供開發者練手測試，且 2.5 flash 模型回覆速度極快，非常適合取代昂貴的 OpenAI 進行概念驗證 (PoC)。
   - **Vector Database**: ChromaDB (本機持久化儲存)
     - *選擇原因*：完全開源、安裝簡單 (`pip install`)，無需依賴繁重的 Docker 或外部雲端服務即可在本機建立完整的向量儲存引擎。
   - **核心架構**: 採用 `services/`, `core/`, `api/endpoints/` 分層架構；並使用 LangChain Expression Language (LCEL) 取代舊版高度封裝的 Chain 撰寫問答邏輯，讓資料流變得清楚好 Debug。

2. **前端  (Frontend App)**
   - **Framework**: 純網頁技術 (Vanilla HTML, CSS, JavaScript)
     - *選擇原因*：為了專注體驗「前後端分離 API 串接」的核心精神。刻意避開 React/Vue 等需利用 Node.js 與 Webpack/Vite 複雜打包的框架，回歸最原始但同樣能實作動態 UI (Dark Mode) 與本地暫存 (LocalStorage) 的技術。

## 專案目錄結構

```text
RAG-prac/
├── backend/                       # FastAPI 後端專案
│   ├── .env                       # (選用) 環境變數檔
│   ├── requirements.txt           # Python 套件依賴
│   ├── main.py                    # 伺服器啟動進入點
│   ├── api/v1/endpoints/          # API 路由設定 (上傳、聊天)
│   ├── core/                      # 全域設定檔 (Config)
│   ├── services/                  # 核心業務邏輯
│   │   ├── document_service.py    # 處理 PDF/TXT 檔案讀取與字串切塊
│   │   ├── vector_store_service.py# 負責 ChromaDB 的向量建立與檢索
│   │   └── llm_service.py         # 實作 LCEL 建構 prompt 與呼叫 Gemini
│   └── chroma_db/                 # 向量資料庫本地儲存資料夾 (自動生成)
│
└── frontend/                      # Vanilla JS 前端專案
    ├── index.html                 # 應用主畫面
    ├── style.css                  # UI 樣式表
    └── script.js                  # 介面互動與 API 串接邏輯
```

## 如何啟動與執行

### 1. 啟動後端 FastAPI
請開啟終端機，依序執行下列指令：

```bash
cd backend

# 建立並啟動虛擬環境 (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 安裝所需套件 (請確保安裝最新版 LangChain 相關套件)
pip install -r requirements.txt

# 啟動伺服器
uvicorn main:app --reload
```
看到 `Uvicorn running on http://127.0.0.1:8000` 即代表啟動成功。

### 2. 開啟前端介面
不需要啟動任何伺服器。
直接在檔案總管中對著 `frontend/index.html` **點擊兩下**，使用您習慣的瀏覽器 (Chrome, Edge 等) 開啟即可。

### 3. 使用流程
1. **輸入金鑰**：在左側側邊欄輸入您的 **Google API Key** 並點擊保存 (Save Key)。
2. **上傳文件**：點擊選擇檔案 (僅支援 `.pdf`, `.txt`)，並點擊 **Train Model** 進行上傳處理。
   *(此時後端會將文件切塊、轉換為向量並存入本地的 ChromaDB 中)*
3. **進行問答**：上傳成功後，即可於右側聊天框輸入問題，系統將會根據文檔內容進行檢索與回答，並附上來源參考。

## 注意事項與已知問題排除

- **API Key 權限**：本專案寫死使用了 `models/gemini-2.5-flash` 與 `models/gemini-embedding-001`。如果您遇到 404 Not Found 錯誤，請確認您的 Google API Key 是否有權限存取該模型版本。
- **後端套件衝突**：若未來 `langchain` 套件改版導致啟動錯誤，請善用 `venv` 隔離環境，並檢查官方文件關於 `langchain_core` 或 `langchain_chroma` 的最新引用路徑。

## 專案後續發展與優化指南 (Future Developments)

當本專案要從「練手 PoC」升級為「正式的商用 PDF Chat 平台」，您可以考慮從以下幾個方向進行優化：

### 1. 處理大量或複雜 PDF (Document Parsing)
目前使用的 `PyPDFLoader` 對於純文字的 PDF 表現良好，但無法理解圖表或複雜排版。
*   **進階解析器**：改用如 `UnstructuredPDFLoader` 或 `LlamaParse`，它們能保留 PDF 中的表格、標題階層甚至解析圖片內的文字 (OCR)。
*   **非同步背景處理**：當使用者上傳上百頁的 PDF 時，API 會卡住很久。請引入 **Celery + Redis** 或是 FastAPI `BackgroundTasks`，讓前端先拿到「處理中」的狀態，等後端切塊與 Embedding 完成後再透過 WebSocket 通知前端。

### 2. 向量資料庫 Chunk 的最佳化管理 (Vector DB / Chunking Strategy)
目前我們是「固定字數 1000」一刀切，這很容易導致一句話或一個段落被攔腰截斷，嚴重影響 RAG 檢索準確率。
*   **語語切塊 (Semantic Chunking)**：與其按字數切，不如按「段落 (Paragraph)」、「標題 (Header)」切塊。Langchain 提供了 `MarkdownHeaderTextSplitter`，如果能先將 PDF 轉為 Markdown 再切塊，效果會大幅提升。
*   **Parent-Document Retriever (父子檢索)**：將文檔切成極小的 Chunk (例如 200 字) 存入向量庫以求「高精準比對」；但當比對中時，回傳給 LLM 閱讀的卻是包含該小片段的「完整段落 (1000字以上的 Parent Document)」以提供完整上下文。
*   **對話過濾與資料隔離 (Metadata Filtering)**：在呼叫 `Chroma.from_documents` 時，為 Chunk 加上 `metadata={"user_id": "123", "doc_name": "report.pdf"}`。檢索時加入過濾條件，確保使用者 A 只會根據他自己上傳的文件進行問答，不會檢索到使用者 B 的機密履歷。

### 3. 加入對話記憶 (Memory)
目前的系統每一次發問都是獨立的 (`Stateless`)，AI 記不住您上一句說了什麼。
*   **實作**：在 FastAPI 後端引入 Langchain 的 `RunnableWithMessageHistory`，搭配 Redis 或 SQL 資料庫儲存每一個 Session ID 的 `chat_history`。提問時，將歷史對話與新問題一併送給 LLM 進行總結 (Condense Question)，再進行檢索。
