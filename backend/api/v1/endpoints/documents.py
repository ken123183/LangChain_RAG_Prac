"""
documents.py
文件上傳與處理的 API 端點。
定義了 `/api/v1/documents/upload` 路由，負責接收前端上傳的文件 (PDF/TXT)，
並呼叫 service 層進行文字切塊與轉存為向量。
"""
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Body
from services.document_service import document_service
from services.vector_store_service import vector_store_service

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    api_key: str = Form(""),
    password: str = Form("")
):
    try:
        # Process and split document
        chunks = await document_service.process_and_split(file)
        
        # Add to vector store
        vector_store_service.add_documents(
            chunks=chunks, 
            api_key=api_key,
            password=password
        )
        
        return {"message": "Document processed and stored successfully", "chunks_count": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/load-local")
async def load_local_document(
    filename: str = Body(..., embed=True),
    api_key: str = Body(""),
    password: str = Body("")
):
    """
    從伺服器的 demo_docs 目錄直接載入檔案。
    """
    import os
    file_path = os.path.join(os.getcwd(), "demo_docs", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {filename} not found in demo_docs")

    try:
        # Process and split document using the new local method
        chunks = document_service.process_local_file(file_path)
        
        # Add to vector store
        vector_store_service.add_documents(
            chunks=chunks, 
            api_key=api_key,
            password=password
        )
        
        return {"message": f"Demo file {filename} loaded successfully", "chunks_count": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/view")
async def view_document(filename: str):
    """
    讀取並回傳 demo_docs 目錄下檔案的內容，用於前端預覽。
    """
    import os
    file_path = os.path.join(os.getcwd(), "demo_docs", filename)
    
    if not os.path.exists(file_path):
        # 如果 demo_docs 找不到，也檢查一下上傳目錄 (uploaded_docs)
        file_path = os.path.join(os.getcwd(), "uploaded_docs", filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

    try:
        if filename.endswith(".pdf"):
            # 對於 PDF，我們可以用 PyPDFLoader 萃取純文字回傳
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            content = "\n".join([doc.page_content for doc in docs])
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        return {"filename": filename, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

