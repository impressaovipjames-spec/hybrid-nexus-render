from fastapi import HTTPException
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

def login(request: LoginRequest):
    if request.email == "admin123@admin.com.br" and request.password == "novasenha123":
        return {
            "access_token": "test_token",
            "token_type": "bearer",
            "user": {"email": request.email}
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")