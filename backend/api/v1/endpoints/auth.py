from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from core.config import settings

router = APIRouter()

class VerifyRequest(BaseModel):
    api_key: str = ""
    password: str = ""

@router.post("/verify")
async def verify_credentials(request: VerifyRequest):
    """
    驗證提供的是否為有效的 API Key 或正確的 Demo Password。
    此端點僅用於 UI 反饋。
    """
    if request.api_key and request.api_key.strip():
        # 這裡僅做基本格式檢查 (例如 Google API Key 通常以 AIza 開頭)
        if request.api_key.startswith("AIza"):
            return {"status": "success", "message": "API Key 格式正確"}
        else:
            raise HTTPException(status_code=400, detail="無效的 API Key 格式")

    if request.password:
        if request.password == settings.DEMO_PASSWORD:
            return {"status": "success", "message": "Demo 密碼驗證成功"}
        else:
            raise HTTPException(status_code=401, detail="Demo 密碼錯誤")

    raise HTTPException(status_code=400, detail="請提供憑證進行驗證")
