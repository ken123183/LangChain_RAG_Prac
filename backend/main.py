try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from core.config import settings
from api.v1.api_router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve Frontend Static Files
# 智慧偵測：嘗試在當前目錄或上一層目錄尋找 frontend
current_dir = os.getcwd()
frontend_path = os.path.join(current_dir, "frontend")
if not os.path.exists(frontend_path):
    # 如果沒找到，往上一層找 (適用於在 backend 目錄啟動的情況)
    frontend_path = os.path.join(os.path.dirname(current_dir), "frontend")

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {"message": f"Welcome to {settings.PROJECT_NAME}. Frontend directory not found."}
