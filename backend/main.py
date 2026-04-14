"""
main.py
FastAPI 應用程式的主要進入點。
負責初始化 FastAPI 實例、設定 CORS 中介軟體 (Middleware)，並載入所有的 API 路由 (Routers)。
"""
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
# Assume we run the app from the project root
frontend_path = os.path.join(os.getcwd(), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_path, "index.html"))
else:
    @app.get("/")
    def root():
        return {"message": f"Welcome to {settings.PROJECT_NAME}. Frontend directory not found."}
