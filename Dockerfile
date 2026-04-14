# 使用 Python 3.10 輕量版作為基礎鏡像
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴 (ChromaDB 可能需要一些編譯工具，雖然 slim 通常夠用，但保險起見)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝 Python 套件
# 這裡假設 Dockerfile 在根目錄，requirements.txt 在 backend/
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製後端與前端程式碼
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# 設定環境變數 PYTHONPATH，確保模組導入正確
ENV PYTHONPATH=/app/backend

# 設定 Hugging Face Spaces 預設的 Port 7860
# 如果使用 Render，可以在 Render 設定中指定 Port
EXPOSE 7860

# 啟動命令：從根目錄執行 uvicorn，並指定 backend.main:app
# 使用 0.0.0.0 讓外部可以連線
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
