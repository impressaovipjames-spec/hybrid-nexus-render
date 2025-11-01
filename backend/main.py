from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/auth/login")
def login(req: LoginRequest):
    if req.email == "admin@vipnexus.com" and req.password == "admin123":
        return {"token": "vipnexus_token_demo"}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

@app.get("/api/health")
def health():
    return {"status": "ok"}
import requests, os
from fastapi import Body

@app.post("/api/send-email")
def send_email(to: str = Body(...), name: str = Body(...)):
    url = "https://api.sendgrid.com/v3/mail/send"
    payload = {
        "from": {"email": "vipnexusia@gmail.com", "name": "VIPNEXUS IA"},
        "personalizations": [{
            "to": [{"email": to}],
            "dynamic_template_data": {"nome": name}
        }],
        "template_id": os.getenv("SENDGRID_TEMPLATE_ID")
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('SENDGRID_API_KEY')}",
        "Content-Type": "application/json"
    }
    r = requests.post(url, json=payload, headers=headers)
    return {"status": r.status_code, "response": r.text}
