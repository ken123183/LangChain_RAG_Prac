"""
documents.py
文件上傳與處理的 API 端點。
定義了 `/api/v1/documents/upload` 路由，負責接收前端上傳的文件 (PDF/TXT)，
並呼叫 service 層進行文字切塊與轉存為向量。
"""
import os
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Body
from services.document_service import document_service
from services.vector_store_service import vector_store_service

router = APIRouter()

def get_demo_dir():
    """智慧偵測 demo_docs 目錄的輔助函數"""
    # 從目前的檔案位置 (backend/api/v1/endpoints/documents.py) 出發
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    # 向上四層到達專案根目錄
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file_dir))))
    
    # 優先檢查專案根目錄下的 demo_docs
    demo_dir = os.path.join(project_root, "demo_docs")
    if os.path.exists(demo_dir):
        return demo_dir, project_root
        
    # 備案：檢查當前目錄下的 demo_docs
    demo_dir = os.path.join(os.getcwd(), "demo_docs")
    if os.path.exists(demo_dir):
        return demo_dir, os.getcwd()
        
    # 備案：檢查當前目錄上一層的 demo_docs
    demo_dir = os.path.join(os.path.dirname(os.getcwd()), "demo_docs")
    if os.path.exists(demo_dir):
        return demo_dir, os.path.dirname(os.getcwd())
        
    return None, None

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
    """從伺服器的 demo_docs 目錄直接載入檔案。"""
    demo_dir, project_root = get_demo_dir()
    if not demo_dir:
        raise HTTPException(status_code=404, detail="demo_docs directory not found")
        
    file_path = os.path.join(demo_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {filename} not found in {demo_dir}")

    try:
        chunks = document_service.process_local_file(file_path)
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
    """讀取並回傳檔案內容用於前端預覽。"""
    demo_dir, project_root = get_demo_dir()
    if not demo_dir:
        raise HTTPException(status_code=404, detail="demo_docs directory not found")
    
    file_path = os.path.join(demo_dir, filename)
    
    # 如果 demo_docs 找不到，也檢查一下上傳目錄 (uploaded_docs)
    if not os.path.exists(file_path):
        upload_dir = os.path.join(project_root, "uploaded_docs")
        file_path = os.path.join(upload_dir, filename)
        
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {filename} not found in any directory")

    try:
        if filename.endswith(".pdf"):
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
