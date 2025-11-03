from login_fix import app
from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import jwt
from passlib.context import CryptContext

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'vipnexus-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app
app = FastAPI(title="VIPNEXUS IA - Funil de Vendas")
api_router = APIRouter(prefix="/api")

# ==================== MODELS ====================

class Lead(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    email: EmailStr
    telefone: str
    status: str = "novo"  # novo, contatado, qualificado, vendido, perdido
    fonte: str = "landing_page"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notas: Optional[str] = None

class LeadCreate(BaseModel):
    nome: str
    email: EmailStr
    telefone: str

class LeadUpdate(BaseModel):
    status: Optional[str] = None
    notas: Optional[str] = None

class AdminUser(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password_hash: str
    nome: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class Stats(BaseModel):
    total_leads: int
    leads_novos: int
    leads_qualificados: int
    leads_vendidos: int
    taxa_conversao: float

# ==================== AUTH FUNCTIONS ====================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user = await db.admin_users.find_one({"id": user_id}, {"_id": 0})
        if user is None:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

# ==================== ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "VIPNEXUS IA - Sistema de Funil de Vendas", "version": "1.0"}

# ========== LEADS ROUTES ==========

@api_router.post("/leads", response_model=Lead, status_code=201)
async def create_lead(lead_data: LeadCreate):
    """Criar novo lead (público - usado pela landing page)"""
    lead = Lead(**lead_data.model_dump())
    doc = lead.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    await db.leads.insert_one(doc)
    return lead

@api_router.get("/leads", response_model=List[Lead])
async def get_leads(current_user: dict = Depends(get_current_user)):
    """Listar todos os leads (admin)"""
    leads = await db.leads.find({}, {"_id": 0}).sort("timestamp", -1).to_list(1000)
    for lead in leads:
        if isinstance(lead['timestamp'], str):
            lead['timestamp'] = datetime.fromisoformat(lead['timestamp'])
    return leads

@api_router.get("/leads/{lead_id}", response_model=Lead)
async def get_lead(lead_id: str, current_user: dict = Depends(get_current_user)):
    """Obter detalhes de um lead específico (admin)"""
    lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    if isinstance(lead['timestamp'], str):
        lead['timestamp'] = datetime.fromisoformat(lead['timestamp'])
    return lead

@api_router.patch("/leads/{lead_id}", response_model=Lead)
async def update_lead(lead_id: str, update_data: LeadUpdate, current_user: dict = Depends(get_current_user)):
    """Atualizar status/notas de um lead (admin)"""
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")
    
    result = await db.leads.update_one({"id": lead_id}, {"$set": update_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    
    updated_lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
    if isinstance(updated_lead['timestamp'], str):
        updated_lead['timestamp'] = datetime.fromisoformat(updated_lead['timestamp'])
    return updated_lead

# ========== AUTH ROUTES ==========

@api_router.post("/auth/register", response_model=dict)
async def register_admin(admin_data: AdminLogin, nome: str = "Admin"):
    """Registrar novo admin (usar apenas para setup inicial)"""
    # Verificar se já existe
    existing = await db.admin_users.find_one({"email": admin_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    admin = AdminUser(
        email=admin_data.email,
        password_hash=hash_password(admin_data.password),
        nome=nome
    )
    doc = admin.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.admin_users.insert_one(doc)
    return {"message": "Admin criado com sucesso", "email": admin.email}

@api_router.post("/auth/login", response_model=TokenResponse)
async def login_admin(credentials: AdminLogin):
    """Login de admin"""
    user = await db.admin_users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    
    token = create_access_token({"sub": user['id'], "email": user['email']})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user['id'], "email": user['email'], "nome": user['nome']}
    }

@api_router.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Obter informações do usuário atual"""
    return {"id": current_user['id'], "email": current_user['email'], "nome": current_user['nome']}

# ========== STATS ROUTES ==========

@api_router.get("/stats", response_model=Stats)
async def get_stats(current_user: dict = Depends(get_current_user)):
    """Obter estatísticas do funil (admin)"""
    total_leads = await db.leads.count_documents({})
    leads_novos = await db.leads.count_documents({"status": "novo"})
    leads_qualificados = await db.leads.count_documents({"status": "qualificado"})
    leads_vendidos = await db.leads.count_documents({"status": "vendido"})
    
    taxa_conversao = (leads_vendidos / total_leads * 100) if total_leads > 0 else 0
    
    return {
        "total_leads": total_leads,
        "leads_novos": leads_novos,
        "leads_qualificados": leads_qualificados,
        "leads_vendidos": leads_vendidos,
        "taxa_conversao": round(taxa_conversao, 2)
    }

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()