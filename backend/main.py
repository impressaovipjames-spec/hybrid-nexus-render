from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/auth/login")
def login(req: LoginRequest):
    if req.email == "admin@vipnexus.com" and req.password == "nova123":
        return {"token": "vipnexus_token_demo"}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

@app.get("/api/health")
def health():
    return {"status": "ok"}
