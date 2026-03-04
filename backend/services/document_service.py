"""
document_service.py
文件處理服務。
負責將使用者上傳的文件 (PDF 或 TXT) 儲存至本機暫存，
接著使用 LangChain 原生的 Loader 讀取文字，並透過 TextSplitter 將長文檔切分為適合長度的小區塊 (Chunks)。
這些 Chunks 後續將送入 Vector Store 初始化為向量。
"""
import os
import shutil
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentService:
    def __init__(self):
        self.upload_dir = "./uploaded_docs"
        os.makedirs(self.upload_dir, exist_ok=True)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )

    async def process_and_split(self, file: UploadFile):
        # Save file locally temporarily
        file_path = os.path.join(self.upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Load document
        if file.filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path, encoding="utf8")
            
        docs = loader.load()
        
        # Split text
        chunks = self.text_splitter.split_documents(docs)
        
        # Opt: remove file after process or keep it
        return chunks

document_service = DocumentService()
