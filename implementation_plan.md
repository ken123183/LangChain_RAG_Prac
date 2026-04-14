# Langchain RAG 系統詳細實作計畫 (Clean Code & 前後端分離版)
為達成**前後端分離 (Frontend-Backend Separation)** 及遵循 **Clean Code 原則**，我們的系統架構將會拆分為獨立的 **Backend API (FastAPI)** 與 **Frontend App (React/Vite 或純前端方案)**。
## 系統需求與核心技術堆疊
### 1. 後端 (Backend API) - Python
*   **Web Framework**: **FastAPI** (高效能、自帶 Swagger UI 測試介面、適合微服務與前後端分離架構)。
*   **處理框架**: **Langchain**。
*   **語言與向量模型**: **Google Gemini 1.5** (`ChatGoogleGenerativeAI`) 與 **Google Embeddings** (`GoogleGenerativeAIEmbeddings`)。
*   **向量資料庫**: **ChromaDB**。
*   **Clean Code 原則**:
    *   **分層架構 (Layered Architecture)**：區分 Routers (處理 HTTP)、Services (處理業務邏輯)、Repositories (處理資料庫與 API 互動)。
    *   **單一職責 (SRP)**：每個類別或函式只負責一件事情（例如載入文件的與檢索的邏輯完全拆開）。
    *   **依賴注入 (Dependency Injection)**：利用 FastAPI 的 `Depends` 機制注入設定與服務，降低耦合度。
### 2. 前端 (Frontend App)
*   **技術選型**: **純網頁 (Vanilla HTML / CSS / JavaScript)**。
*   *採用原生的 HTML 結構與 Vanilla JS Fetch API 直接與後端溝通，無須建置與編譯，最輕量化且完全前後端分離。*
*   **功能**:
    *   設定頁面：輸入 Google API Key。
    *   上傳元件：將檔案以 `multipart/form-data` API 請求發送至後端。
    *   聊天介面：透過 REST API (`POST /chat`) 傳送使用者問題並接收回答。
## 系統架構與資料流 (Data Flow)
**前端 (Browser/UI) <==== HTTP REST API ====> 後端 (FastAPI + Langchain)**
### 後端 API 設計 (Endpoints)
1. **`POST /api/v1/documents/upload`**
   - 前端傳送檔案與 Google API Key。
   - 後端 Service 接收檔案、切塊、呼叫 Embedding API 寫入 ChromaDB，回傳成功狀態。
2. **`POST /api/v1/chat`**
   - 前端傳送 `{ "query": "使用者問題", "api_key": "..." }`。
   - 後端 Service 將 Query 轉向量、檢索 Chroma、組裝 Prompt、呼叫 Gemini，回傳解答文字與來源 (Sources)。
## 專案目錄與檔案結構規劃 (Clean Code)
```text
langchain-rag/
├── backend/                       # 後端專案根目錄
│   ├── .env.example
│   ├── requirements.txt
│   ├── main.py                    # FastAPI 進入點，負責註冊 Routers 與啟動
│   ├── api/
│   │   └── v1/
│   │       ├── api_router.py      # 總路由註冊
│   │       ├── endpoints/
│   │       │   ├── documents.py   # 文件上傳相關 API (/upload)
│   │       │   └── chat.py        # 聊天問答相關 API (/chat)
│   │       └── dependencies.py    # FastAPI 依賴注入 (例如驗證 API Key)
│   ├── core/
│   │   └── config.py              # 全域設定檔 (Pydantic BaseSettings)
│   └── services/
│       ├── document_service.py    # 負責 File Loader 與 TextSplitter 邏輯
│       ├── vector_store_service.py# 負責 ChromaDB 的互動 (儲存、檢索)
│       └── llm_service.py         # 負責建構 Langchain RAG Chain 與呼叫 Gemini
│
└── frontend/                      # 前端專案根目錄 (純網頁)
    ├── index.html                 # 主畫面 (包含上傳區、設定區、聊天區)
    ├── style.css                  # UI 樣式設計 (自訂精美介面)
    └── script.js                  # 實作與 FastAPI 溝通的 API 請求與畫面互動邏輯
```
### Clean Code 實踐亮點
- **無狀態 (Stateless) API**: 後端本身不儲存使用者的對話狀態 (Session)，由前端維護對話紀錄，每次提問帶上歷史訊息，或由後端輕量化紀錄對話 ID，符合 REST 架構。
- **解耦 (Decoupling)**: 前端這輩子不會知道 Langchain 或 Chroma 的存在；後端 API 端點 (`endpoints/`) 內部也不會有複雜邏輯，業務邏輯全部封裝於 `services/` 中方便獨立進行單元測試。
## 執行與開發步驟
1. **基礎後端建設**: 建立 FastAPI 專案，設定 `core/config.py` 與基礎路由。
2. **後端服務層實作**:
   - `document_service.py` 實作上傳解讀。
   - `vector_store_service.py` 實作存入與檢索。
   - `llm_service.py` 實作 Langchain `RetrievalQA` 邏輯。
3. **後端 API 串接**: 在 `api/v1/endpoints` 暴露介面，使用 Swagger UI 驗證 API 是否能正確回應。
4. **前端介面實作**: 建立純網頁的 `index.html`, `style.css`, `script.js`，實作與 FastAPI 溝通的 API 串接與聊天畫面。
