"""
VIPNEXUS IA - DATABASE BRIDGE: MongoDB ↔ JSON Sync
Protocolo: PNA2-HYB-FUSION/1125A

Este módulo sincroniza dados entre:
- MongoDB (Hybrid-Nexus FastAPI)
- JSON files (MiniMax VIPNEXUS)
- Real-time updates bidirecionais
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import aiofiles
from motor.motor_asyncio import AsyncIOMotorClient
import hashlib
import uuid

# Configurações
MONGODB_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'vipnexus_funil')
MINIMAX_DATA_DIR = Path('/workspace/funil-automatico')
HYBRID_DATA_DIR = Path('/workspace/hybrid-fusion/data')
LOG_FILE = Path('/workspace/hybrid-fusion/logs/database_bridge.log')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DatabaseBridge')

class DatabaseBridge:
    """
    Bridge para sincronização de dados entre MongoDB e JSON
    """
    
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.sync_cache = {}
        self.last_sync_timestamp = None
        
    async def initialize(self):
        """Inicializar conexão MongoDB"""
        try:
            self.mongo_client = AsyncIOMotorClient(MONGODB_URL)
            self.db = self.mongo_client[DB_NAME]
            logger.info(f"Conectado ao MongoDB: {MONGODB_URL}")
            
            # Criar diretórios necessários
            HYBRID_DATA_DIR.mkdir(parents=True, exist_ok=True)
            Path('/workspace/hybrid-fusion/logs').mkdir(parents=True, exist_ok=True)
            
        except Exception as e:
            logger.error(f"Erro ao conectar MongoDB: {e}")
            raise
    
    async def close(self):
        """Fechar conexão MongoDB"""
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("Conexão MongoDB fechada")
    
    # ==================== LEADS SYNCHRONIZATION ====================
    
    async def sync_leads_mongodb_to_minimax(self) -> Dict[str, Any]:
        """
        Sincronizar leads do MongoDB (Hybrid-Nexus) → JSON MiniMax format
        """
        try:
            logger.info("Iniciando sincronização MongoDB → MiniMax")
            
            # Buscar todos os leads do MongoDB
            mongo_leads = await self.db.leads.find({}).to_list(length=1000)
            
            minimax_leads = []
            sync_stats = {
                'total_leads': len(mongo_leads),
                'new_leads': 0,
                'updated_leads': 0,
                'errors': 0
            }
            
            for mongo_lead in mongo_leads:
                try:
                    # Converter MongoDB document → MiniMax format
                    minimax_lead = self._convert_mongo_lead_to_minimax(mongo_lead)
                    minimax_leads.append(minimax_lead)
                    
                    # Determinar se é novo ou atualizado
                    lead_hash = self._calculate_lead_hash(minimax_lead)
                    if lead_hash not in self.sync_cache:
                        sync_stats['new_leads'] += 1
                    else:
                        sync_stats['updated_leads'] += 1
                    
                    self.sync_cache[lead_hash] = minimax_lead
                    
                except Exception as e:
                    logger.error(f"Erro ao converter lead {mongo_lead.get('_id')}: {e}")
                    sync_stats['errors'] += 1
            
            # Salvar no formato MiniMax
            await self._save_minimax_leads(minimax_leads)
            
            self.last_sync_timestamp = datetime.now(timezone.utc)
            
            logger.info(f"Sincronização concluída: {sync_stats}")
            return {
                'success': True,
                'stats': sync_stats,
                'timestamp': self.last_sync_timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na sincronização: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def sync_leads_minimax_to_mongodb(self, json_file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Sincronizar leads do JSON MiniMax → MongoDB (Hybrid-Nexus)
        """
        try:
            logger.info("Iniciando sincronização MiniMax → MongoDB")
            
            # Carregar dados MiniMax
            if json_file_path is None:
                json_file_path = MINIMAX_DATA_DIR / 'data' / 'leads.json'
            
            if not Path(json_file_path).exists():
                logger.warning(f"Arquivo MiniMax não encontrado: {json_file_path}")
                return {'success': True, 'message': 'Arquivo não encontrado'}
            
            async with aiofiles.open(json_file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                minimax_leads = json.loads(content)
            
            sync_stats = {
                'total_leads': len(minimax_leads),
                'inserted': 0,
                'updated': 0,
                'errors': 0
            }
            
            for minimax_lead in minimax_leads:
                try:
                    # Verificar se lead já existe no MongoDB
                    existing = await self.db.leads.find_one({
                        'email': minimax_lead.get('email'),
                        'telefone': minimax_lead.get('telefone')
                    })
                    
                    # Converter MiniMax format → MongoDB document
                    mongo_lead = self._convert_minimax_lead_to_mongo(minimax_lead)
                    
                    if existing:
                        # Atualizar lead existente
                        result = await self.db.leads.update_one(
                            {'_id': existing['_id']},
                            {'$set': mongo_lead}
                        )
                        if result.modified_count > 0:
                            sync_stats['updated'] += 1
                    else:
                        # Inserir novo lead
                        result = await self.db.leads.insert_one(mongo_lead)
                        if result.inserted_id:
                            sync_stats['inserted'] += 1
                    
                except Exception as e:
                    logger.error(f"Erro ao sincronizar lead {minimax_lead.get('email')}: {e}")
                    sync_stats['errors'] += 1
            
            self.last_sync_timestamp = datetime.now(timezone.utc)
            
            logger.info(f"Sincronização MiniMax→MongoDB concluída: {sync_stats}")
            return {
                'success': True,
                'stats': sync_stats,
                'timestamp': self.last_sync_timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na sincronização MiniMax→MongoDB: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def bidirectional_sync(self) -> Dict[str, Any]:
        """
        Sincronização bidirecional entre MongoDB e MiniMax
        """
        try:
            logger.info("Iniciando sincronização bidirecional")
            
            # Sincronizar MongoDB → MiniMax
            mongodb_to_minimax = await self.sync_leads_mongodb_to_minimax()
            
            # Sincronizar MiniMax → MongoDB
            minimax_to_mongodb = await self.sync_leads_minimax_to_mongodb()
            
            result = {
                'success': True,
                'bidirectional': True,
                'mongodb_to_minimax': mongodb_to_minimax,
                'minimax_to_mongodb': minimax_to_mongodb,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info("Sincronização bidirecional concluída com sucesso")
            return result
            
        except Exception as e:
            logger.error(f"Erro na sincronização bidirecional: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ==================== REAL-TIME SYNC ====================
    
    async def watch_mongodb_changes(self):
        """
        Monitorar mudanças em tempo real no MongoDB
        """
        try:
            logger.info("Iniciando watch de mudanças MongoDB")
            
            # Watch para mudanças na coleção leads
            change_stream = self.db.leads.watch()
            
            async for change in change_stream:
                try:
                    operation_type = change['operationType']
                    document_key = change['documentKey']
                    
                    logger.info(f"Mudança detectada: {operation_type} - {document_key}")
                    
                    if operation_type in ['insert', 'update', 'replace']:
                        # Trigger sync para MiniMax
                        await self._trigger_minimax_sync(change['fullDocument'])
                    elif operation_type == 'delete':
                        # Remover do MiniMax
                        await self._remove_from_minimax(document_key['_id'])
                    
                except Exception as e:
                    logger.error(f"Erro ao processar mudança: {e}")
            
        except Exception as e:
            logger.error(f"Erro no watch MongoDB: {e}")
    
    async def _trigger_minimax_sync(self, mongo_lead: Dict[str, Any]):
        """Trigger sincronização para MiniMax quando lead muda no MongoDB"""
        try:
            minimax_lead = self._convert_mongo_lead_to_minimax(mongo_lead)
            
            # Carregar leads MiniMax existentes
            minimax_leads = await self._load_minimax_leads()
            
            # Encontrar e atualizar
            found = False
            for i, lead in enumerate(minimax_leads):
                if (lead.get('email') == minimax_lead['email'] and 
                    lead.get('telefone') == minimax_lead['telefone']):
                    minimax_leads[i] = minimax_lead
                    found = True
                    break
            
            if not found:
                minimax_leads.append(minimax_lead)
            
            # Salvar
            await self._save_minimax_leads(minimax_leads)
            
            logger.info(f"Lead sincronizado para MiniMax: {minimax_lead['email']}")
            
        except Exception as e:
            logger.error(f"Erro ao trigger sync MiniMax: {e}")
    
    # ==================== CONVERSION METHODS ====================
    
    def _convert_mongo_lead_to_minimax(self, mongo_lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converter MongoDB lead format → MiniMax format
        """
        # Converter ObjectId para string
        lead_id = str(mongo_lead.get('_id', ''))
        
        # Converter timestamp
        timestamp = mongo_lead.get('timestamp')
        if isinstance(timestamp, datetime):
            timestamp_str = timestamp.isoformat()
        else:
            timestamp_str = timestamp or datetime.now(timezone.utc).isoformat()
        
        return {
            'lead_id': mongo_lead.get('id') or str(uuid.uuid4()),
            'timestamp': timestamp_str,
            'nome': mongo_lead.get('nome', ''),
            'email': mongo_lead.get('email', ''),
            'telefone': mongo_lead.get('telefone', ''),
            'status': mongo_lead.get('status', 'novo'),
            'source': mongo_lead.get('fonte', 'mongodb'),
            'notes': mongo_lead.get('notas', ''),
            'created_at': timestamp_str,
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'sync_source': 'mongodb_hybrid_nexus',
            'original_id': lead_id
        }
    
    def _convert_minimax_lead_to_mongo(self, minimax_lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converter MiniMax lead format → MongoDB document
        """
        # Converter timestamp string para datetime
        timestamp = minimax_lead.get('timestamp')
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        return {
            'id': minimax_lead.get('lead_id', str(uuid.uuid4())),
            'nome': minimax_lead.get('nome', ''),
            'email': minimax_lead.get('email', ''),
            'telefone': minimax_lead.get('telefone', ''),
            'status': minimax_lead.get('status', 'novo'),
            'fonte': minimax_lead.get('source', 'minimax'),
            'notas': minimax_lead.get('notes', ''),
            'timestamp': timestamp,
            'sync_source': minimax_lead.get('sync_source', 'minimax'),
            'original_id': minimax_lead.get('original_id', '')
        }
    
    # ==================== FILE OPERATIONS ====================
    
    async def _load_minimax_leads(self) -> List[Dict[str, Any]]:
        """Carregar leads do formato MiniMax"""
        try:
            file_path = HYBRID_DATA_DIR / 'leads_minimax.json'
            
            if not file_path.exists():
                return []
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
                
        except Exception as e:
            logger.error(f"Erro ao carregar leads MiniMax: {e}")
            return []
    
    async def _save_minimax_leads(self, leads: List[Dict[str, Any]]):
        """Salvar leads no formato MiniMax"""
        try:
            file_path = HYBRID_DATA_DIR / 'leads_minimax.json'
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(leads, indent=2, ensure_ascii=False))
            
            logger.info(f"Salvos {len(leads)} leads no formato MiniMax")
            
        except Exception as e:
            logger.error(f"Erro ao salvar leads MiniMax: {e}")
            raise
    
    async def _remove_from_minimax(self, mongo_id: str):
        """Remover lead do formato MiniMax"""
        try:
            minimax_leads = await self._load_minimax_leads()
            
            # Filtrar leads a manter
            filtered_leads = [
                lead for lead in minimax_leads 
                if lead.get('original_id') != mongo_id
            ]
            
            await self._save_minimax_leads(filtered_leads)
            
            logger.info(f"Lead removido do MiniMax: {mongo_id}")
            
        except Exception as e:
            logger.error(f"Erro ao remover do MiniMax: {e}")
    
    def _calculate_lead_hash(self, lead: Dict[str, Any]) -> str:
        """Calcular hash único para lead"""
        content = f"{lead.get('email', '')}{lead.get('telefone', '')}{lead.get('timestamp', '')}"
        return hashlib.md5(content.encode()).hexdigest()
    
    # ==================== UTILITY METHODS ====================
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """Obter status da sincronização"""
        try:
            # Contar leads no MongoDB
            mongo_count = await self.db.leads.count_documents({})
            
            # Contar leads no MiniMax
            minimax_leads = await self._load_minimax_leads()
            minimax_count = len(minimax_leads)
            
            # Informações do cache
            cache_size = len(self.sync_cache)
            
            return {
                'success': True,
                'mongodb_leads': mongo_count,
                'minimax_leads': minimax_count,
                'cache_size': cache_size,
                'last_sync': self.last_sync_timestamp.isoformat() if self.last_sync_timestamp else None,
                'sync_needed': mongo_count != minimax_count
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def force_full_sync(self) -> Dict[str, Any]:
        """Forçar sincronização completa"""
        logger.info("Iniciando sincronização completa forçada")
        
        # Limpar cache
        self.sync_cache.clear()
        
        # Executar sincronização bidirecional
        result = await self.bidirectional_sync()
        
        if result['success']:
            logger.info("Sincronização completa forçada concluída")
        else:
            logger.error("Falha na sincronização completa forçada")
        
        return result

# ==================== MAIN FUNCTIONS ====================

async def main():
    """Função principal para testes"""
    bridge = DatabaseBridge()
    
    try:
        await bridge.initialize()
        
        # Testar sincronização
        result = await bridge.bidirectional_sync()
        print("Resultado da sincronização:", json.dumps(result, indent=2))
        
        # Obter status
        status = await bridge.get_sync_status()
        print("Status da sincronização:", json.dumps(status, indent=2))
        
    finally:
        await bridge.close()

if __name__ == "__main__":
    asyncio.run(main())
