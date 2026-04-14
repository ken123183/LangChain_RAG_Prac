"""
chat.py
問答與檢索對話的 API 端點。
定義了 `/api/v1/chat` 路由，負責接收前端使用者的提問 (Query)，
並交由 LLM Service 進行向量庫檢索與最終答案生成。
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.llm_service import llm_service

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    api_key: str = ""
    password: str = ""

@router.post("/")
def chat(request: ChatRequest):
    try:
        reply, sources = llm_service.generate_response(
            query=request.query, 
            api_key=request.api_key,
            password=request.password
        )
        return {"reply": reply, "sources": sources}
    except Exception as e:
        # Standardize error message for missing credentials
        if "API Key" in str(e) or "Password" in str(e):
            raise HTTPException(status_code=401, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

