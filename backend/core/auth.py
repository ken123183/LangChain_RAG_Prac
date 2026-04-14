from core.config import settings

def get_effective_api_key(api_key: str = "", password: str = "") -> str:
    """
    獲取有效的 API Key。
    1. 如果有提供 api_key，直接使用。
    2. 如果沒提供 api_key，但提供正確的 demo password，則使用系統設定的 GOOGLE_API_KEY。
    """
    if api_key and api_key.strip():
        return api_key.strip()
    
    if password and password == settings.DEMO_PASSWORD:
        if settings.GOOGLE_API_KEY:
            return settings.GOOGLE_API_KEY
        else:
            raise ValueError("系統尚未設定預設 API Key (GOOGLE_API_KEY)。")
            
    if not api_key and not password:
        raise ValueError("請提供 Google API Key 或 Demo 存取密碼。")
    
    if password and password != settings.DEMO_PASSWORD:
        raise ValueError("Demo 存取密碼錯誤。")
        
    raise ValueError("無法驗證身份，請提供有效憑證。")
