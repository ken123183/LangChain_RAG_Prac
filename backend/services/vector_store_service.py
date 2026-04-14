"""
vector_store_service.py
向量資料庫服務。
負責與本機的 ChromaDB 進行互動。主要功能有二：
1. 將 document_service 切好的文檔區塊，透過 Google Embedding 模型轉換為向量後儲存 (`add_documents`)。
2. 建立檢索器 (Retriever)，讓 LLM Service 在回答階段可以用來尋找最相關的前 K 篇文檔 (`get_retriever`)。
"""
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from core.config import settings

from core.auth import get_effective_api_key

class VectorStoreService:
    def __init__(self):
        self.persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        
    def _get_embeddings(self, api_key: str = "", password: str = ""):
        effective_key = get_effective_api_key(api_key, password)
        return GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001", 
            google_api_key=effective_key
        )

    def add_documents(self, chunks: list, api_key: str = "", password: str = ""):
        embeddings = self._get_embeddings(api_key, password)
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=self.persist_directory
        )
        return True
        
    def get_retriever(self, api_key: str):
        embeddings = self._get_embeddings(api_key)
        vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=embeddings
        )
        return vectorstore.as_retriever(search_kwargs={"k": 3})

    def get_retriever(self, api_key: str):
        embeddings = self._get_embeddings(api_key)
        vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=embeddings
        )
        return vectorstore.as_retriever(search_kwargs={"k": 3})

vector_store_service = VectorStoreService()
