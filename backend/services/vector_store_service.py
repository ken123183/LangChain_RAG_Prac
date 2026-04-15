"""
vector_store_service.py
向量資料庫服務。
負責與本機的 ChromaDB 進行互動。
已切換為本地 HuggingFace 模型，不再依賴 Google API 進行文檔向量化。
1. 將文檔區塊透過 all-MiniLM-L6-v2 轉換為向量後儲存 (`add_documents`)。
2. 建立檢索器 (Retriever) 進行語意搜尋 (`get_retriever`)。
"""
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from core.config import settings

class VectorStoreService:
    def __init__(self):
        self.persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        # 使用本地開源模型：快、免費、無限額度
        # 模型會自動下載到本地快取
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    def add_documents(self, chunks: list, api_key: str = "", password: str = ""):
        """
        將文檔片段存入向量資料庫。
        注意：現在已不再需要 api_key 進行 Embedding。
        """
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        return True
        
    def get_retriever(self, api_key: str = ""):
        """
        獲取檢索器，搜尋最相關的前 3 名片段。
        """
        vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
        return vectorstore.as_retriever(search_kwargs={"k": 3})

vector_store_service = VectorStoreService()
