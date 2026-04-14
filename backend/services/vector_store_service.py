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

    def reset_store(self):
        """
        透過 Chroma API 徹底清空向量庫，比直接刪除資料夾更穩定。
        """
        import os
        try:
            # 這裡我們不帶 API Key，因為 delete_collection 不需要 Embedding 模型
            # 隨便給一個空的 Embedding Function 即可初始化物件
            from langchain_community.embeddings import FakeEmbeddings
            vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=FakeEmbeddings(size=768)
            )
            vectorstore.delete_collection()
            
            # 為了保險起見，如果目錄還在（空目錄），我們再清一次
            import shutil
            if os.path.exists(self.persist_directory):
                shutil.rmtree(self.persist_directory)
            os.makedirs(self.persist_directory, exist_ok=True)
            
            return True
        except Exception as e:
            print(f"Reset failed: {e}")
            return False

vector_store_service = VectorStoreService()
