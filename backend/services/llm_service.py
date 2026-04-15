"""
llm_service.py
大型語言模型服務 (RAG 核心大腦)。
使用最新的 LangChain Expression Language (LCEL) 架構。
接收使用者的提問後，先呼叫 vector_store_service.get_retriever() 尋找相關文檔上下文 (Context)，
再將 Context 與 Question 塞入提示詞 (Prompt Template)，最後丟給 Google Gemini 模型生成回答。
並回傳答案與引用來源。
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from core.auth import get_effective_api_key
from services.vector_store_service import vector_store_service

class LLMService:
    def generate_response(self, query: str, api_key: str = "", password: str = ""):
        # Get effective API key using auth helper
        effective_api_key = get_effective_api_key(api_key, password)

        # 智慧模型切換邏輯
        if effective_api_key.startswith("gsk_"):
            # 使用 Groq 高速引擎
            llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                groq_api_key=effective_api_key,
                temperature=0.3
            )
        else:
            # 維持使用 Google Gemini
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash", 
                google_api_key=effective_api_key, 
                temperature=0.3
            )
        
        # Build chain using LCEL
        retriever = vector_store_service.get_retriever(effective_api_key)
        
        template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
        prompt = ChatPromptTemplate.from_template(template)
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        # Retrieve documents
        docs = retriever.invoke(query)
        context_text = format_docs(docs)
        
        # We manually invoke the components to have access to source documents easily
        prompt_val = prompt.invoke({"context": context_text, "question": query})
        response = llm.invoke(prompt_val)
        
        # Format sources
        sources = []
        for doc in docs:
            sources.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
            
        return response.content, sources

llm_service = LLMService()

