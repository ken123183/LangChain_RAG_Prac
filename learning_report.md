# 學習與開發紀錄報告 (Learning Report)

## 專案概述
本專案目標是從零開始打造一個基於 **LangChain** 與 **Google Gemini** 的 RAG (檢索增強生成) 系統。
為了符合現代化的 Clean Code 原則與系統擴展性，我們採用了**前後端分離 (Frontend-Backend Separation)** 的架構：
- **後端 (Backend)**: 使用 Python FastAPI 提供 RESTful API，負責處理文件上傳、文字切塊、向量化、ChromaDB 儲存，以及與 LLM 的對話檢索邏輯。
- **前端 (Frontend)**: 使用最輕量化的純網頁技術 (Vanilla HTML, CSS, JavaScript) 實作，透過 Fetch API 與後端溝通，實作精美的深色系 (Dark Mode) 聊天應用介面。

---

## 理論基礎與相關技術 (Theory & Technology)

在實作本專案前，需了解以下核心 RAG 理論與技術名詞：

### 1. RAG (Retrieval-Augmented Generation) 檢索增強生成
大型語言模型 (LLM) 最大的弱點是「幻覺」(Hallucination) 與「知識庫未即時更新」。
RAG 技術透過**先搜尋 (Retrieve) 企業內部或特定領域文檔**，將找到的資訊作為上下文送給 LLM 閱讀，然後再請 LLM **回答問題 (Generate)**，確保了回答的真實性與準確度。

### 2. 資料前處理與切塊 (Chunking)
語言模型的輸入長度 (Token Size) 是有上限的，我們不能直接把整本 1000 頁的說明書丟給模型。
- **Text Splitter**：我們使用了 LangChain 的 `RecursiveCharacterTextSplitter` 將長文檔以約 1,000 字為單位切分成多個「組塊 (Chunks)」，同時保留了 100 字的 `chunk_overlap` (組塊重疊)，確保在段落交界處的語意不會被硬生生切斷。

### 3. Sentence Embedding (句向量/詞嵌入)
電腦看不懂文字，只能計算數字的距離。
- **GoogleGenerativeAIEmbeddings**：將文本組塊轉換為具有數百或數千維度的高維度向量 (Vector)。語意相近的句子，在向量空間中的幾何距離就會越近（例如計算 Cosine Similarity）。

### 4. Vector Database (向量資料庫)
傳統的 SQL 資料庫只能比對文字是否完全相同，但 RAG 需要的是「語義搜尋」。
- **ChromaDB**：本專案採用的開源向量資料庫，它能將文件向量儲存在硬碟中 (Persist Database)，當使用者發出查詢 (Query) 時，將 Query 也轉為向量，並使用 KNN 等演算法在 Chroma 中快速找出「幾何距離最近」的 Top-K 個文件區塊。

### 5. LCEL (LangChain Expression Language)
LangChain 推出的一種宣告式語法，用於快速將各個模組 (Prompt, Retriever, LLM, Parser) 用 `|` 符號像 unix pipeline 一樣串接起來。
在專案中，我們用它取代了舊版封裝過度且難以追蹤原始碼的 `RetrievalQA` Chain 工具。

---

## 開發流程紀錄

1. **規劃與架構設計**
   - 放棄最初的 Streamlit 方案，改採更嚴謹的 FastAPI 後端，並將邏輯拆分為 `documents` 與 `chat` 兩個 Endpoints。
   - 建立 `services` 層 (`document_service.py`, `vector_store_service.py`, `llm_service.py`) 以確保單一職責 (SRP)。

2. **基礎環境建置**
   - 建立 Python 虛擬環境 (`venv`) 確保套件隔離。
   - 撰寫 `requirements.txt` 並且定義了環境變數讀取機制 (`core/config.py`)。

3. **純前端介面開發**
   - 撰寫無框架的 HTML/CSS/JS。
   - 實作了側邊欄 (輸入 API Key、上傳檔案) 與聊天區塊，並加上了載入中的狀態顯示。

4. **系統整合與踩坑 (Troubleshooting)**
   - 在前後端串接測試時，我們遇到了數個由套件更新與官方 API 異動所導致的嚴重問題，以下詳述。

---

## 系統全流程運作解析 (End-to-End Execution Flow)

為了更清楚理解系統在背後是如何運作的，以下將以「使用者上傳文件並發問」的完整生命週期為例：

### 階段一：知識庫建立流程 (Data Ingestion)
當使用者在前端網頁點擊 **「Train Model」** 上傳文件時：
1. **Frontend (UI)**：網頁 JavaScript 攔截表單，將 PDF 檔案與 Google API Key 打包成 `FormData`，透過 Fetch API 發出 `POST /api/v1/documents/upload` 請求。
2. **Backend (FastAPI)**：路由端點 `documents.py` 接收到上傳的檔案。
3. **Document Service (切塊)**：
   - 伺服器先將 PDF 暫存在本地硬碟。
   - 呼叫 LangChain 的 `PyPDFLoader` 讀取文字內容。
   - 關鍵步驟：呼叫 `RecursiveCharacterTextSplitter` 將長達數萬字的內容，**硬性切割 (Chunking)** 成 1,000 字一段的「組塊 (Chunks)」，並保留 100 字的上下文重疊 (Overlap)。
4. **Vector Store Service (向量化與儲存)**：
   - 將這些文字 Chunks 透過網路送到 Google API (`gemini-embedding-001`)。
   - Google 會將每一段文字轉換成高維度的**數學向量 (Vector Embeddings)**。
   - 後端將這些「文字 + 對應的向量」存入本機的實體向量庫 **ChromaDB** 中 (`./chroma_db` 資料夾)。

### 階段二：檢索與生成流程 (Retrieval & Generation)
當使用者在前端聊天框輸入問題並按下 **送出 (按 Enter)** 時：
1. **Frontend (UI)**：JavaScript 將提問文字 (Query) 與 API Key 打包成 JSON，發出 `POST /api/v1/chat` 請求。
2. **Backend (FastAPI)**：路由端點 `chat.py` 接收到 JSON 請求後，轉交給 `llm_service.py` 處理。
3. **Vector Retrieval (語意檢索)**：
   - 系統首先將使用者的「提問文字」再次透過 Google 轉換為向量。
   - 在 **ChromaDB** 中執行相似度比對 (如 K-Nearest Neighbors 演算法)，找出之前存進去、與提問「幾何距離最近、語意最相關」的前 K 個 (預設為 3 段) 文件組塊。
4. **LLM Service (大腦生成)**：
   - 利用 **LCEL (Langchain Expression Language)**，將找出的前 3 段文檔內容組合為「上下文 (Context)」。
   - 把 Context 與使用者的 Question 一起塞入準備好的**提示詞模板 (Prompt Template)**，告訴 AI：「請『只』根據這些上下文回答問題」。
   - 將完整的 Prompt 送給 Google 大語言模型 (`gemini-2.5-flash`)。
5. **最終產出 (Output)**：FastAPI 接收到 Gemini 產生的最終答案後，連同「剛剛參考的那 3 段文檔來源 (Sources)」，一起打包回傳給前端網頁顯示。

---

## 遇到的挑戰與解決方案 (Troubleshooting)

### 🚨 挑戰一：LangChain 與生態系套件的版本衝突
**問題描述**：
初期我們鎖定了 `langchain==0.2.1` 等舊版號，但在後續安裝 `langchain-chroma` 與 `pypdf` 時，引發了 `pydantic_v1` 的相依性衝突，甚至導致 `ModuleNotFoundError: No module named 'langchain.chains'` 的錯誤。

**解決方案**：
- 我們決定將 `requirements.txt` 中所有 LangChain 相關套件（包含 `langchain`, `langchain-core`, `langchain-community`, `langchain-chroma`, `langchain-google-genai`）全部**解除版號限制並升級到最新版**。
- 將棄用的匯入路徑 `langchain.text_splitter` 更新為現代化的 `langchain_text_splitters`。

### 🚨 挑戰二：棄用的 RetrievalQA Chain
**問題描述**：
升級到最新版的 LangChain 後，原本在 `llm_service.py` 中使用的 `from langchain.chains import RetrievalQA` 寫法失效，因為官方已經逐漸淘汰舊版的 Chain 架構。

**解決方案**：
- 我們重新撰寫了生成回應的邏輯，全面擁抱 **LCEL (LangChain Expression Language)**。
- 使用 `ChatPromptTemplate` 建立 Prompt，並將 Retriever 檢索出來的文檔文字直接餵給 LLM 進行手工調用 (Invoke)。這不僅修復了錯誤，還讓程式碼更容易被追蹤與自訂來源出處。

### 🚨 挑戰三：Google Embedding 模型名稱變更 (404 Not Found)
**問題描述**：
前端呼叫上傳文件 API 時，後端報錯：`models/embedding-001 is not found`。改用 `text-embedding-004` 依然報錯。

**解決方案**：
- 撰寫測試腳本 `list_models.py` 直接調用 Google API 查詢該 API Key 實際能用的模型清單。
- 確認正確的嵌入模型名稱應該是 **`models/gemini-embedding-001`**，更新 `vector_store_service.py` 後順利解決。

### 🚨 挑戰四：Google LLM 模型名稱變更 (404 Not Found)
**問題描述**：
上傳文件解決後，在聊天時又遇到錯誤：`models/gemini-1.5-flash is not found`。

**解決方案**：
- 同樣透過 `list_models.py` 查詢，發現 Google 已經將合法呼叫模型升級為 **`models/gemini-2.5-flash`**。
- 更新 `llm_service.py` 中的模型指定名稱，順利解決問答失敗的問題。

---

## 參考文獻與學習資源 (References)

1. **RAG 基礎理論與教學**
   - [LangChain 官方文件 - Q&A with RAG](https://python.langchain.com/v0.2/docs/tutorials/rag/)
   - [What is Request-Augmented Generation (RAG)? - IBM](https://www.ibm.com/topics/retrieval-augmented-generation)
2. **LCEL 語法學習**
   - [LangChain Expression Language (LCEL) 官方文件](https://python.langchain.com/v0.2/docs/concepts/#langchain-expression-language)
3. **相關套件 API 文件**
   - [FastAPI 官方文檔](https://fastapi.tiangolo.com/)
   - [ChromaDB 官方文檔](https://docs.trychroma.com/)
   - [Google AI Studio (Gemini API 提供者)](https://aistudio.google.com/)

---

## 專案建構流程與工程細節 (Step-by-Step Engineering Details)

如果您想要重新打造這個專案，或是將此架構應用到您的正式專案中，請參考以下的 Step-by-Step 流程：

### 第一步：環境與基礎設施 (Infrastructure)
1. **建立 Python 虛擬環境**
   避免全域套件污染，強烈建議在專案中透過 `python -m venv venv` 建立獨立環境。
2. **依賴套件管理 (`requirements.txt`)**
   專案的核心套件有三個陣營：
   - 後端框架：`fastapi`, `uvicorn[standard]`, `pydantic-settings`
   - AI/RAG：`langchain`, `langchain-core`, `langchain-chroma`, `langchain-google-genai`
   - 檔案處理：`python-multipart` (處理 HTTP 表單上傳), `pypdf` (解析 PDF 檔)
   *(注意：如果套件衝突，最好的方法通常是將這幾個 Langchain 生態系的套件全部取消版號鎖定，讓 pip 自行解析最新版本)*

### 第二步：後端服務分層搭建 (Backend Services)
我們遵循了 **單一職責原則 (SRP)** 與 **分層設計**：
1. **環境變數注入 (`core/config.py`)**：使用 Pydantic BaseSettings 建立全域設定，這讓管理 API 路徑或是資料庫位置變得非常容易。
2. **服務層 (`services/`)**：
   - **`document_service.py`**：專門處理從 FastAPI 接收到的 `UploadFile`。將其暫存到硬碟後，使用 `PyPDFLoader` 或 `TextLoader` 載入，並立刻使用 `RecursiveCharacterTextSplitter` 進行切塊。
   - **`vector_store_service.py`**：負責宣告 Google 的 Embedding 模型 (目前為 `models/gemini-embedding-001`)。提供建立向量 (`add_documents`) 與回傳檢索器物件 (`get_retriever`) 兩個方法。
   - **`llm_service.py`**：RAG 邏輯的大腦。宣告 Gemini LLM (`models/gemini-2.5-flash`)，利用 **LCEL** 語法 (`ChatPromptTemplate` 結合 Retriever) 手動組裝 Prompt 並呼叫 LLM 提供帶有來源 (Sources) 的回答。

### 第三步：後端 API 端點暴露 (API Endpoints)
不再將所有邏輯塞在 `main.py` 中，而是透過 `api_router.py` 進行模組化。
1. **`endpoints/documents.py`**：提供 `POST /api/v1/documents/upload`，接收 `multipart/form-data`。呼叫 `document_service` 切塊後，交給 `vector_store_service` 存入 DB。
2. **`endpoints/chat.py`**：提供 `POST /api/v1/chat`，接收 JSON。直接呼叫 `llm_service` 處理問答邏輯並將回答回傳給前端。

### 第四步：純前端開發 (Vanilla Frontend)
為了展示最高效、免編譯的前後端分離：
1. **切版 (`index.html` & `style.css`)**：設計深色主題、響應式的現代化 UI。介面包含「API Key 設定區」、「文件上傳區」與「聊天區」。
2. **狀態與 API 呼叫 (`script.js`)**：
   - **狀態保留**：實作 `localStorage` 存放使用者的 Google API Key，免去每次重整都要重新輸入的麻煩。
   - **整合 Fetch API**：撰寫異步函式 (`async/await`) 向後端的 `/upload` 與 `/chat` 發送請求，並實作讀取中的 UI 變化 (加載中文字、鎖定按鈕)。

### 第五步：系統除錯與觀測
在使用 `uvicorn main:app --reload` 啟動後，後端若出錯能第一時間在終端機看到完整 Traceback。這也是我們能快速抓出舊版 Langchain 寫法錯誤 (如 `RetrievalQA` 失效) 的重要關鍵。

---
**結論**：
透過這次的實作，我們不僅建立了一個架構優良的 RAG 系統，更學到了在 AI 領域開發中非常重要的一課：**開源套件 (LangChain) 與雲端模型 (Google Gemini) 的迭代速度非常快**。開發者無法完全依賴舊有的程式碼或網路教學，必須具備動態查詢 API 文件、寫測試腳本列出可用資源、以及擁抱新架構 (如 LCEL) 的能力。
