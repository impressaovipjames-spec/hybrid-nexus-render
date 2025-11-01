"""
VIPNEXUS IA - FUSED API GATEWAY
Protocolo: PNA2-HYB-FUSION/1125A

API Gateway unificado que combina:
- FastAPI (Hybrid-Nexus original)
- PHP Adapters (MiniMax compatibility)
- Database Bridge (MongoDB ↔ JSON sync)
- Automation Triggers (Cross-system sequences)
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import os
import logging
import json
import asyncio
from datetime import datetime, timezone, timedelta
import uuid
from pathlib import Path
import subprocess
import sys

# Importar componentes da fusão
sys.path.append('/workspace/hybrid-fusion/bridge')
sys.path.append('/workspace/hybrid-fusion/adapters')

from database_bridge import DatabaseBridge
from automation_triggers import AutomationTriggerEngine

# Configurações
APP_NAME = "VIPNEXUS IA - FUSED API GATEWAY"
VERSION = "1.0.0-fusion"
LOG_FILE = Path('/workspace/hybrid-fusion/logs/api_gateway.log')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('FusedAPIGateway')

# Configuração de segurança
security = HTTPBearer()

# Criar app FastAPI
app = FastAPI(
    title=APP_NAME,
    description="API Gateway unificado para fusão Hybrid-Nexus ↔ MiniMax VIPNEXUS",
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== GLOBAL COMPONENTS ====================

class FusionComponents:
    """Componentes globais da fusão"""
    
    def __init__(self):
        self.database_bridge = None
        self.automation_engine = None
        self.initialized = False
    
    async def initialize(self):
        """Inicializar todos os componentes"""
        try:
            logger.info("Inicializando componentes da fusão...")
            
            # Database Bridge
            self.database_bridge = DatabaseBridge()
            await self.database_bridge.initialize()
            
            # Automation Engine
            self.automation_engine = AutomationTriggerEngine()
            await self.automation_engine.initialize()
            
            self.initialized = True
            logger.info("Componentes da fusão inicializados com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar componentes: {e}")
            raise

# Instância global
fusion_components = FusionComponents()

# ==================== PYDANTIC MODELS ====================

class LeadCreate(BaseModel):
    """Modelo para criação de lead"""
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telefone: str = Field(..., min_length=10, max_length=20)
    source: Optional[str] = "fused_landing"

class LeadUpdate(BaseModel):
    """Modelo para atualização de lead"""
    status: Optional[str] = None
    notas: Optional[str] = None
    source: Optional[str] = None

class LeadResponse(BaseModel):
    """Modelo de resposta de lead"""
    id: str
    nome: str
    email: str
    telefone: str
    status: str
    source: str
    timestamp: datetime
    notas: Optional[str] = None
    sync_status: Dict[str, Any] = {}

class AutomationTriggerRequest(BaseModel):
    """Modelo para trigger de automação"""
    lead_id: str
    lead_email: str
    lead_name: str
    trigger_type: str
    data: Optional[Dict[str, Any]] = {}

class SyncRequest(BaseModel):
    """Modelo para solicitação de sincronização"""
    sync_type: str  # 'mongodb_to_minimax', 'minimax_to_mongodb', 'bidirectional'
    force: bool = False

class HealthResponse(BaseModel):
    """Modelo de resposta de saúde"""
    status: str
    version: str
    components: Dict[str, bool]
    timestamp: datetime

# ==================== AUTHENTICATION ====================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency para autenticação JWT"""
    # Implementação simples para demo
    # Em produção, implementar verificação JWT real
    token = credentials.credentials
    
    if token != "fused_token_demo":
        raise HTTPException(status_code=401, detail="Token inválido")
    
    return {"id": "fused_admin", "email": "admin@vipnexus.com", "role": "admin"}

# ==================== STARTUP/SHUTDOWN EVENTS ====================

@app.on_event("startup")
async def startup_event():
    """Eventos de inicialização"""
    try:
        logger.info(f"Iniciando {APP_NAME} v{VERSION}")
        await fusion_components.initialize()
        logger.info("API Gateway iniciado com sucesso")
    except Exception as e:
        logger.error(f"Erro no startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos de shutdown"""
    try:
        logger.info("Encerrando API Gateway...")
        if fusion_components.database_bridge:
            await fusion_components.database_bridge.close()
        logger.info("API Gateway encerrado com sucesso")
    except Exception as e:
        logger.error(f"Erro no shutdown: {e}")

# ==================== HEALTH & INFO ENDPOINTS ====================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Endpoint de verificação de saúde"""
    components_status = {
        'database_bridge': fusion_components.database_bridge is not None and fusion_components.database_bridge.mongo_client is not None,
        'automation_engine': fusion_components.automation_engine is not None and fusion_components.automation_engine.minimax_config is not None,
        'fusion_initialized': fusion_components.initialized
    }
    
    overall_status = "healthy" if all(components_status.values()) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        version=VERSION,
        components=components_status,
        timestamp=datetime.now(timezone.utc)
    )

@app.get("/api/info")
async def get_api_info():
    """Informações do sistema fusionado"""
    return {
        'name': APP_NAME,
        'version': VERSION,
        'protocol': 'PNA2-HYB-FUSION/1125A',
        'components': {
            'hybrid_nexus': 'FastAPI + MongoDB + React',
            'minimax_vipnexus': 'PHP + JSON + Advanced Integrations'
        },
        'fusion_status': 'active',
        'features': [
            'Unified Lead Management',
            'Cross-system Automation',
            'Real-time Data Sync',
            'Multi-platform Integration'
        ]
    }

# ==================== LEADS MANAGEMENT ====================

@app.post("/api/leads", response_model=LeadResponse, status_code=201)
async def create_lead(lead_data: LeadCreate, background_tasks: BackgroundTasks):
    """Criar novo lead (com triggers de fusão)"""
    try:
        logger.info(f"Criando lead fusionado: {lead_data.email}")
        
        # 1. Salvar no MongoDB (Hybrid-Nexus)
        lead_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        
        mongo_lead = {
            'id': lead_id,
            'nome': lead_data.nome,
            'email': lead_data.email,
            'telefone': lead_data.telefone,
            'status': 'novo',
            'fonte': lead_data.source or 'fused_landing',
            'timestamp': timestamp,
            'sync_source': 'fused_api'
        }
        
        if fusion_components.database_bridge:
            await fusion_components.database_bridge.db.leads.insert_one(mongo_lead)
        
        # 2. Trigger automações (MiniMax style)
        if fusion_components.automation_engine:
            automation_result = await fusion_components.automation_engine.trigger_lead_capture({
                'lead_id': lead_id,
                'nome': lead_data.nome,
                'email': lead_data.email,
                'telefone': lead_data.telefone,
                'source': lead_data.source
            })
        
        # 3. Sincronização automática (background)
        background_tasks.add_task(fusion_components.database_bridge.sync_leads_mongodb_to_minimax)
        
        return LeadResponse(
            id=lead_id,
            nome=lead_data.nome,
            email=lead_data.email,
            telefone=lead_data.telefone,
            status='novo',
            source=lead_data.source or 'fused_landing',
            timestamp=timestamp,
            sync_status={
                'mongodb_saved': True,
                'automation_triggered': fusion_components.automation_engine is not None,
                'minimax_sync_pending': True
            }
        )
        
    except Exception as e:
        logger.error(f"Erro ao criar lead: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/leads", response_model=List[LeadResponse])
async def get_leads(current_user: dict = Depends(get_current_user)):
    """Listar todos os leads"""
    try:
        if not fusion_components.database_bridge:
            raise HTTPException(status_code=503, detail="Database bridge não disponível")
        
        mongo_leads = await fusion_components.database_bridge.db.leads.find({}).sort("timestamp", -1).to_list(1000)
        
        leads = []
        for lead in mongo_leads:
            leads.append(LeadResponse(
                id=lead.get('id', ''),
                nome=lead.get('nome', ''),
                email=lead.get('email', ''),
                telefone=lead.get('telefone', ''),
                status=lead.get('status', 'novo'),
                source=lead.get('fonte', ''),
                timestamp=lead.get('timestamp'),
                notas=lead.get('notas'),
                sync_status=lead.get('sync_status', {})
            ))
        
        return leads
        
    except Exception as e:
        logger.error(f"Erro ao buscar leads: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: str, current_user: dict = Depends(get_current_user)):
    """Obter lead específico"""
    try:
        if not fusion_components.database_bridge:
            raise HTTPException(status_code=503, detail="Database bridge não disponível")
        
        lead = await fusion_components.database_bridge.db.leads.find_one({"id": lead_id})
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead não encontrado")
        
        return LeadResponse(
            id=lead.get('id', ''),
            nome=lead.get('nome', ''),
            email=lead.get('email', ''),
            telefone=lead.get('telefone', ''),
            status=lead.get('status', 'novo'),
            source=lead.get('fonte', ''),
            timestamp=lead.get('timestamp'),
            notas=lead.get('notas'),
            sync_status=lead.get('sync_status', {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.patch("/api/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(lead_id: str, update_data: LeadUpdate, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """Atualizar lead (com triggers de automação)"""
    try:
        if not fusion_components.database_bridge:
            raise HTTPException(status_code=503, detail="Database bridge não disponível")
        
        # Buscar lead atual
        lead = await fusion_components.database_bridge.db.leads.find_one({"id": lead_id})
        if not lead:
            raise HTTPException(status_code=404, detail="Lead não encontrado")
        
        old_status = lead.get('status', 'novo')
        
        # Preparar update
        update_dict = {}
        if update_data.status:
            update_dict['status'] = update_data.status
        if update_data.notas:
            update_dict['notas'] = update_data.notas
        if update_data.source:
            update_dict['fonte'] = update_data.source
        
        update_dict['updated_at'] = datetime.now(timezone.utc)
        
        # Executar update no MongoDB
        await fusion_components.database_bridge.db.leads.update_one(
            {"id": lead_id},
            {"$set": update_dict}
        )
        
        # Trigger automações se status mudou
        if update_data.status and update_data.status != old_status:
            if fusion_components.automation_engine:
                await fusion_components.automation_engine.trigger_status_change(
                    lead_id=lead_id,
                    old_status=old_status,
                    new_status=update_data.status,
                    lead_data={
                        'email': lead.get('email', ''),
                        'nome': lead.get('nome', ''),
                        'telefone': lead.get('telefone', '')
                    }
                )
        
        # Sincronização automática (background)
        background_tasks.add_task(fusion_components.database_bridge.sync_leads_mongodb_to_minimax)
        
        # Retornar lead atualizado
        updated_lead = await fusion_components.database_bridge.db.leads.find_one({"id": lead_id})
        
        return LeadResponse(
            id=updated_lead.get('id', ''),
            nome=updated_lead.get('nome', ''),
            email=updated_lead.get('email', ''),
            telefone=updated_lead.get('telefone', ''),
            status=updated_lead.get('status', 'novo'),
            source=updated_lead.get('fonte', ''),
            timestamp=updated_lead.get('timestamp'),
            notas=updated_lead.get('notas'),
            sync_status=updated_lead.get('sync_status', {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# ==================== AUTOMATION ENDPOINTS ====================

@app.post("/api/automation/trigger")
async def trigger_automation(trigger_data: AutomationTriggerRequest):
    """Disparar automação manual"""
    try:
        if not fusion_components.automation_engine:
            raise HTTPException(status_code=503, detail="Automation engine não disponível")
        
        # Mapear tipos de trigger
        trigger_mapping = {
            'lead_capture': fusion_components.automation_engine.trigger_lead_capture,
            'cart_abandonment': fusion_components.automation_engine.trigger_cart_abandonment,
            'purchase_completed': fusion_components.automation_engine.trigger_purchase_completed
        }
        
        if trigger_data.trigger_type not in trigger_mapping:
            raise HTTPException(status_code=400, detail=f"Tipo de trigger inválido: {trigger_data.trigger_type}")
        
        # Executar trigger
        trigger_func = trigger_mapping[trigger_data.trigger_type]
        result = await trigger_func(trigger_data.data or {})
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no trigger de automação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/automation/status")
async def get_automation_status():
    """Obter status das automações"""
    try:
        if not fusion_components.automation_engine:
            raise HTTPException(status_code=503, detail="Automation engine não disponível")
        
        status = await fusion_components.automation_engine.get_automation_status()
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status de automação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# ==================== SYNCHRONIZATION ENDPOINTS ====================

@app.post("/api/sync/trigger")
async def trigger_sync(sync_request: SyncRequest):
    """Disparar sincronização manual"""
    try:
        if not fusion_components.database_bridge:
            raise HTTPException(status_code=503, detail="Database bridge não disponível")
        
        # Mapear tipos de sync
        sync_mapping = {
            'mongodb_to_minimax': fusion_components.database_bridge.sync_leads_mongodb_to_minimax,
            'minimax_to_mongodb': fusion_components.database_bridge.sync_leads_minimax_to_mongodb,
            'bidirectional': fusion_components.database_bridge.bidirectional_sync
        }
        
        if sync_request.sync_type not in sync_mapping:
            raise HTTPException(status_code=400, detail=f"Tipo de sync inválido: {sync_request.sync_type}")
        
        # Executar sync
        sync_func = sync_mapping[sync_request.sync_type]
        result = await sync_func()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na sincronização: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/sync/status")
async def get_sync_status():
    """Obter status da sincronização"""
    try:
        if not fusion_components.database_bridge:
            raise HTTPException(status_code=503, detail="Database bridge não disponível")
        
        status = await fusion_components.database_bridge.get_sync_status()
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status de sync: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# ==================== INTEGRATION ENDPOINTS ====================

@app.post("/api/integrations/eduzz-webhook")
async def handle_eduzz_webhook(request: Request):
    """Webhook para eventos Eduzz (simulado)"""
    try:
        # Simular processamento webhook
        webhook_data = await request.json()
        
        logger.info(f"Webhook Eduzz recebido: {json.dumps(webhook_data)}")
        
        # Processar evento (em implementação real, validaria assinatura)
        event_type = webhook_data.get('event_type', 'purchase')
        customer_data = webhook_data.get('customer', {})
        
        if event_type == 'purchase_approved':
            # Trigger automação de pós-compra
            if fusion_components.automation_engine:
                await fusion_components.automation_engine.trigger_purchase_completed({
                    'transaction_id': webhook_data.get('transaction_id'),
                    'customer_email': customer_data.get('email'),
                    'customer_name': customer_data.get('name'),
                    'amount': webhook_data.get('amount')
                })
        
        return {"success": True, "message": "Webhook processado"}
        
    except Exception as e:
        logger.error(f"Erro no webhook Eduzz: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/integrations/stats")
async def get_integration_stats():
    """Estatísticas das integrações"""
    try:
        stats = {
            'total_leads': 0,
            'automations_triggered': 0,
            'sync_operations': 0,
            'last_sync': None
        }
        
        if fusion_components.database_bridge:
            # Contar leads
            stats['total_leads'] = await fusion_components.database_bridge.db.leads.count_documents({})
            
            # Último sync
            if fusion_components.database_bridge.last_sync_timestamp:
                stats['last_sync'] = fusion_components.database_bridge.last_sync_timestamp.isoformat()
        
        if fusion_components.automation_engine:
            automation_status = await fusion_components.automation_engine.get_automation_status()
            stats['automations_triggered'] = automation_status.get('completed_instances', 0)
        
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao obter stats de integração: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# ==================== ADMIN ENDPOINTS ====================

@app.post("/api/admin/login")
async def admin_login(email: str, password: str):
    """Login administrativo (simplificado)"""
    # Implementação simplificada
    if email == "admin@vipnexus.com" and password == "admin123":
        return {
            "access_token": "fused_token_demo",
            "token_type": "bearer",
            "user": {
                "id": "fused_admin",
                "email": "admin@vipnexus.com",
                "role": "admin"
            }
        }
    
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

@app.get("/api/admin/dashboard")
async def get_admin_dashboard(current_user: dict = Depends(get_current_user)):
    """Dashboard administrativo"""
    try:
        dashboard_data = {
            'leads': {'total': 0, 'new': 0, 'qualified': 0, 'sold': 0},
            'automations': {'active': 0, 'completed': 0, 'failed': 0},
            'sync': {'status': 'idle', 'last_sync': None, 'operations': 0},
            'integrations': {'active': 0, 'total': 5}
        }
        
        if fusion_components.database_bridge:
            # Stats de leads
            total_leads = await fusion_components.database_bridge.db.leads.count_documents({})
            new_leads = await fusion_components.database_bridge.db.leads.count_documents({"status": "novo"})
            qualified_leads = await fusion_components.database_bridge.db.leads.count_documents({"status": "qualificado"})
            sold_leads = await fusion_components.database_bridge.db.leads.count_documents({"status": "vendido"})
            
            dashboard_data['leads'] = {
                'total': total_leads,
                'new': new_leads,
                'qualified': qualified_leads,
                'sold': sold_leads
            }
            
            # Sync status
            sync_status = await fusion_components.database_bridge.get_sync_status()
            dashboard_data['sync'] = {
                'status': 'active' if sync_status.get('sync_needed') else 'synced',
                'last_sync': sync_status.get('last_sync'),
                'operations': 1
            }
        
        if fusion_components.automation_engine:
            automation_status = await fusion_components.automation_engine.get_automation_status()
            dashboard_data['automations'] = {
                'active': automation_status.get('running_instances', 0),
                'completed': automation_status.get('completed_instances', 0),
                'failed': 0
            }
        
        dashboard_data['integrations']['active'] = 5  # SendGrid, WhatsApp, GA4, Meta, CRM
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# ==================== ERROR HANDLERS ====================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint não encontrado",
            "detail": f"URL: {request.url}",
            "available_endpoints": [
                "/api/health",
                "/api/info", 
                "/api/leads",
                "/api/automation/trigger",
                "/api/sync/trigger",
                "/api/integrations/stats",
                "/api/admin/dashboard"
            ]
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    logger.error(f"Erro interno: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "detail": str(exc) if os.getenv('DEBUG') else "Erro interno",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

# ==================== RUN APP ====================

if __name__ == "__main__":
    import uvicorn
    
    print(f"""
    🚀 {APP_NAME}
    📡 Protocolo: {VERSION}
    🔗 Fusion: Hybrid-Nexus ↔ MiniMax VIPNEXUS
    📊 Docs: http://localhost:8000/docs
    🔧 Health: http://localhost:8000/api/health
    """)
    
    uvicorn.run(
        "fused_api_gateway:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
