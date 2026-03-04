"""
documents.py
文件上傳與處理的 API 端點。
定義了 `/api/v1/documents/upload` 路由，負責接收前端上傳的文件 (PDF/TXT)，
並呼叫 service 層進行文字切塊與轉存為向量。
"""
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from services.document_service import document_service
from services.vector_store_service import vector_store_service

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    api_key: str = Form(...)
):
    if not api_key:
        raise HTTPException(status_code=400, detail="Google API Key is required")
        
    try:
        # Process and split document
        chunks = await document_service.process_and_split(file)
        
        # Add to vector store
        vector_store_service.add_documents(chunks, api_key)
        
        return {"message": "Document processed and stored successfully", "chunks_count": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

