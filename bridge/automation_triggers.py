"""
VIPNEXUS IA - AUTOMATION TRIGGERS: MiniMax ↔ Hybrid-Nexus
Protocolo: PNA2-HYB-FUSION/1125A

Este módulo gerencia os triggers de automação que conectam:
- Sequências MiniMax (7-day nurture, WhatsApp, Email)
- Eventos Hybrid-Nexus (lead capture, status changes)
- Integrações externas (SendGrid, Zenvia, GA4, Meta Pixel)
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import aiofiles
import aiohttp
import hashlib
from dataclasses import dataclass, asdict
import yaml

# Configurações
MINIMAX_CONFIG_PATH = Path('/workspace/funil-automatico/js/config.js')
HYBRID_DATA_DIR = Path('/workspace/hybrid-fusion/data')
AUTOMATION_LOG = Path('/workspace/hybrid-fusion/logs/automation.log')
ACTIVE_SEQUENCES_FILE = HYBRID_DATA_DIR / 'active_sequences.json'

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(AUTOMATION_LOG),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AutomationTriggers')

@dataclass
class AutomationEvent:
    """Estrutura para eventos de automação"""
    event_id: str
    event_type: str
    lead_id: str
    lead_email: str
    lead_name: str
    timestamp: datetime
    data: Dict[str, Any]
    sequence_id: Optional[str] = None
    status: str = 'pending'

@dataclass
class AutomationSequence:
    """Estrutura para sequências de automação"""
    sequence_id: str
    name: str
    trigger_event: str
    steps: List[Dict[str, Any]]
    active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class AutomationTriggerEngine:
    """
    Engine principal de triggers de automação
    """
    
    def __init__(self):
        self.active_sequences = {}
        self.event_queue = asyncio.Queue()
        self.minimax_config = None
        self.sequence_scheduler = {}
        
    async def initialize(self):
        """Inicializar engine de automação"""
        try:
            # Carregar configuração MiniMax
            self.minimax_config = await self._load_minimax_config()
            
            # Criar diretórios necessários
            HYBRID_DATA_DIR.mkdir(parents=True, exist_ok=True)
            
            # Carregar sequências ativas
            await self._load_active_sequences()
            
            # Inicializar sequências padrão
            await self._initialize_default_sequences()
            
            logger.info("Engine de automação inicializado")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar engine: {e}")
            raise
    
    async def trigger_lead_capture(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger: Captura de novo lead
        Dispara sequência de boas-vindas e nutrição
        """
        try:
            event = AutomationEvent(
                event_id=f"lead_capture_{datetime.now().timestamp()}",
                event_type="lead_capture",
                lead_id=lead_data.get('lead_id', ''),
                lead_email=lead_data.get('email', ''),
                lead_name=lead_data.get('nome', ''),
                timestamp=datetime.now(timezone.utc),
                data=lead_data
            )
            
            logger.info(f"Trigger: Captura de lead - {event.lead_email}")
            
            # Adicionar à fila de eventos
            await self.event_queue.put(event)
            
            # Processar imediatamente
            await self._process_event(event)
            
            return {
                'success': True,
                'event_id': event.event_id,
                'triggers_fired': ['welcome_sequence', '7_day_nurture', 'whatsapp_welcome']
            }
            
        except Exception as e:
            logger.error(f"Erro no trigger lead_capture: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def trigger_status_change(self, lead_id: str, old_status: str, new_status: str, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger: Mudança de status do lead
        Dispara automações baseadas no novo status
        """
        try:
            event = AutomationEvent(
                event_id=f"status_change_{datetime.now().timestamp()}",
                event_type="status_change",
                lead_id=lead_id,
                lead_email=lead_data.get('email', ''),
                lead_name=lead_data.get('nome', ''),
                timestamp=datetime.now(timezone.utc),
                data={
                    'old_status': old_status,
                    'new_status': new_status,
                    'lead_data': lead_data
                }
            )
            
            logger.info(f"Trigger: Status change - {lead_data.get('email')} - {old_status} → {new_status}")
            
            await self.event_queue.put(event)
            await self._process_event(event)
            
            # Determinar automações baseadas no status
            triggers = self._get_triggers_for_status(new_status)
            
            return {
                'success': True,
                'event_id': event.event_id,
                'status_change': f"{old_status} → {new_status}",
                'triggers_fired': triggers
            }
            
        except Exception as e:
            logger.error(f"Erro no trigger status_change: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def trigger_cart_abandonment(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger: Carrinho abandonado
        Dispara sequência de recuperação
        """
        try:
            event = AutomationEvent(
                event_id=f"cart_abandonment_{datetime.now().timestamp()}",
                event_type="cart_abandonment",
                lead_id=lead_data.get('lead_id', ''),
                lead_email=lead_data.get('email', ''),
                lead_name=lead_data.get('nome', ''),
                timestamp=datetime.now(timezone.utc),
                data=lead_data
            )
            
            logger.info(f"Trigger: Carrinho abandonado - {event.lead_email}")
            
            await self.event_queue.put(event)
            await self._process_event(event)
            
            return {
                'success': True,
                'event_id': event.event_id,
                'triggers_fired': ['cart_recovery_email', 'cart_recovery_whatsapp']
            }
            
        except Exception as e:
            logger.error(f"Erro no trigger cart_abandonment: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def trigger_purchase_completed(self, purchase_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger: Compra finalizada
        Dispara sequência de onboarding e agradecimento
        """
        try:
            event = AutomationEvent(
                event_id=f"purchase_completed_{datetime.now().timestamp()}",
                event_type="purchase_completed",
                lead_id=purchase_data.get('lead_id', ''),
                lead_email=purchase_data.get('customer_email', ''),
                lead_name=purchase_data.get('customer_name', ''),
                timestamp=datetime.now(timezone.utc),
                data=purchase_data
            )
            
            logger.info(f"Trigger: Compra finalizada - {event.lead_email}")
            
            await self.event_queue.put(event)
            await self._process_event(event)
            
            return {
                'success': True,
                'event_id': event.event_id,
                'triggers_fired': ['thank_you_email', 'onboarding_sequence', 'upsell_sequence']
            }
            
        except Exception as e:
            logger.error(f"Erro no trigger purchase_completed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _process_event(self, event: AutomationEvent):
        """Processar evento e executar automações"""
        try:
            # Buscar sequências ativas para este tipo de evento
            matching_sequences = [
                seq for seq in self.active_sequences.values()
                if seq.trigger_event == event.event_type and seq.active
            ]
            
            for sequence in matching_sequences:
                await self._execute_sequence(sequence, event)
                
        except Exception as e:
            logger.error(f"Erro ao processar evento {event.event_id}: {e}")
    
    async def _execute_sequence(self, sequence: AutomationSequence, event: AutomationEvent):
        """Executar sequência de automação"""
        try:
            logger.info(f"Executando sequência: {sequence.name} para {event.lead_email}")
            
            # Criar instance da sequência para este evento
            sequence_instance = {
                'sequence_id': sequence.sequence_id,
                'instance_id': f"{sequence.sequence_id}_{event.event_id}",
                'event_id': event.event_id,
                'lead_email': event.lead_email,
                'lead_name': event.lead_name,
                'steps_completed': 0,
                'steps_total': len(sequence.steps),
                'started_at': datetime.now(timezone.utc),
                'status': 'running'
            }
            
            # Salvar instance
            await self._save_sequence_instance(sequence_instance)
            
            # Executar steps sequencialmente
            for step in sequence.steps:
                await self._execute_step(step, sequence_instance, event)
                sequence_instance['steps_completed'] += 1
                
                # Pausar entre steps se necessário
                delay = step.get('delay_minutes', 0)
                if delay > 0:
                    logger.info(f"Aguardando {delay} minutos para próximo step")
                    await asyncio.sleep(delay * 60)
            
            # Marcar como concluído
            sequence_instance['status'] = 'completed'
            sequence_instance['completed_at'] = datetime.now(timezone.utc)
            await self._save_sequence_instance(sequence_instance)
            
            logger.info(f"Sequência concluída: {sequence.name}")
            
        except Exception as e:
            logger.error(f"Erro ao executar sequência {sequence.sequence_id}: {e}")
            
            # Marcar como erro
            if 'sequence_instance' in locals():
                sequence_instance['status'] = 'error'
                sequence_instance['error'] = str(e)
                await self._save_sequence_instance(sequence_instance)
    
    async def _execute_step(self, step: Dict[str, Any], sequence_instance: Dict[str, Any], event: AutomationEvent):
        """Executar step individual da sequência"""
        try:
            step_type = step.get('type', '')
            step_config = step.get('config', {})
            
            logger.info(f"Executando step: {step_type} para {event.lead_email}")
            
            if step_type == 'send_email':
                await self._send_email(step_config, event, sequence_instance)
            elif step_type == 'send_whatsapp':
                await self._send_whatsapp(step_config, event, sequence_instance)
            elif step_type == 'track_analytics':
                await self._track_analytics(step_config, event, sequence_instance)
            elif step_type == 'update_crm':
                await self._update_crm(step_config, event, sequence_instance)
            elif step_type == 'delay':
                await self._execute_delay(step_config, event, sequence_instance)
            else:
                logger.warning(f"Tipo de step não reconhecido: {step_type}")
                
        except Exception as e:
            logger.error(f"Erro ao executar step: {e}")
            raise
    
    async def _send_email(self, config: Dict[str, Any], event: AutomationEvent, sequence_instance: Dict[str, Any]):
        """Enviar email via SendGrid"""
        try:
            if not self.minimax_config:
                logger.warning("Configuração MiniMax não disponível para envio de email")
                return
            
            # Simular envio SendGrid
            email_data = {
                'to': event.lead_email,
                'template': config.get('template', 'default'),
                'subject': config.get('subject', 'Mensagem VIPNEXUS IA'),
                'variables': {
                    'nome': event.lead_name,
                    'data': event.data,
                    'sequence_name': sequence_instance.get('sequence_id', '')
                }
            }
            
            # Em implementação real, chamaria API SendGrid
            logger.info(f"Email enviado (simulado): {event.lead_email} - Template: {config.get('template')}")
            
            # Log da automação
            await self._log_automation_action('email_sent', event, config)
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            raise
    
    async def _send_whatsapp(self, config: Dict[str, Any], event: AutomationEvent, sequence_instance: Dict[str, Any]):
        """Enviar WhatsApp via Zenvia"""
        try:
            if not self.minimax_config:
                logger.warning("Configuração MiniMax não disponível para envio WhatsApp")
                return
            
            # Simular envio WhatsApp
            whatsapp_data = {
                'to': event.data.get('telefone', ''),
                'message': config.get('message', 'Olá! Tudo bem?'),
                'template': config.get('template', 'default'),
                'variables': {
                    'nome': event.lead_name
                }
            }
            
            # Em implementação real, chamaria API Zenvia
            logger.info(f"WhatsApp enviado (simulado): {event.data.get('telefone')} - Template: {config.get('template')}")
            
            # Log da automação
            await self._log_automation_action('whatsapp_sent', event, config)
            
        except Exception as e:
            logger.error(f"Erro ao enviar WhatsApp: {e}")
            raise
    
    async def _track_analytics(self, config: Dict[str, Any], event: AutomationEvent, sequence_instance: Dict[str, Any]):
        """Tracking de analytics (GA4, Meta Pixel)"""
        try:
            tracking_config = config.get('tracking', {})
            
            # Simular tracking GA4
            if tracking_config.get('ga4'):
                ga4_event = {
                    'event_name': tracking_config.get('event_name', 'automation_trigger'),
                    'event_params': {
                        'lead_email': event.lead_email,
                        'sequence_id': sequence_instance.get('sequence_id', ''),
                        'step_type': config.get('type', '')
                    }
                }
                logger.info(f"GA4 tracking (simulado): {json.dumps(ga4_event)}")
            
            # Simular tracking Meta Pixel
            if tracking_config.get('meta_pixel'):
                pixel_event = {
                    'event_name': tracking_config.get('event_name', 'AutomationTrigger'),
                    'event_params': {
                        'email': event.lead_email,
                        'sequence': sequence_instance.get('sequence_id', '')
                    }
                }
                logger.info(f"Meta Pixel tracking (simulado): {json.dumps(pixel_event)}")
            
            # Log da automação
            await self._log_automation_action('analytics_tracked', event, config)
            
        except Exception as e:
            logger.error(f"Erro no tracking analytics: {e}")
            raise
    
    async def _update_crm(self, config: Dict[str, Any], event: AutomationEvent, sequence_instance: Dict[str, Any]):
        """Atualizar CRM (Pipedrive)"""
        try:
            if not self.minimax_config:
                logger.warning("Configuração MiniMax não disponível para CRM")
                return
            
            # Simular atualização CRM
            crm_data = {
                'lead_email': event.lead_email,
                'action': config.get('action', 'note_added'),
                'note': f"Automação executada: {config.get('description', 'Sequência executada')}",
                'sequence_id': sequence_instance.get('sequence_id', ''),
                'step_type': config.get('type', '')
            }
            
            # Em implementação real, chamaria API Pipedrive
            logger.info(f"CRM atualizado (simulado): {event.lead_email} - {config.get('description')}")
            
            # Log da automação
            await self._log_automation_action('crm_updated', event, config)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar CRM: {e}")
            raise
    
    async def _execute_delay(self, config: Dict[str, Any], event: AutomationEvent, sequence_instance: Dict[str, Any]):
        """Aguardar tempo específico"""
        try:
            delay_minutes = config.get('minutes', 0)
            delay_hours = config.get('hours', 0)
            delay_days = config.get('days', 0)
            
            total_delay = (delay_minutes * 60) + (delay_hours * 3600) + (delay_days * 86400)
            
            if total_delay > 0:
                logger.info(f"Aguardando {total_delay} segundos antes do próximo step")
                await asyncio.sleep(total_delay)
            
            # Log da automação
            await self._log_automation_action('delay_executed', event, config)
            
        except Exception as e:
            logger.error(f"Erro no delay: {e}")
            raise
    
    # ==================== DEFAULT SEQUENCES ====================
    
    async def _initialize_default_sequences(self):
        """Inicializar sequências padrão"""
        try:
            # Sequência 1: Bem-vindos (7 dias)
            welcome_sequence = AutomationSequence(
                sequence_id="welcome_7_day",
                name="Sequência de Boas-vindas (7 dias)",
                trigger_event="lead_capture",
                steps=[
                    {
                        'type': 'send_email',
                        'config': {
                            'template': 'welcome_day_0',
                            'subject': 'Bem-vindo ao VIPNEXUS IA!',
                            'delay_minutes': 0
                        }
                    },
                    {
                        'type': 'send_whatsapp',
                        'config': {
                            'template': 'welcome_whatsapp',
                            'message': 'Olá {{nome}}! 👋 Obrigado por se interessar pelo VIPNEXUS IA. Em breve você receberá conteúdo exclusivo!',
                            'delay_minutes': 5
                        }
                    },
                    {
                        'type': 'track_analytics',
                        'config': {
                            'tracking': {'ga4': True, 'meta_pixel': True},
                            'event_name': 'WelcomeSequenceStarted'
                        }
                    }
                ],
                active=True,
                created_at=datetime.now(timezone.utc)
            )
            
            # Sequência 2: Carrinho Abandonado
            cart_recovery_sequence = AutomationSequence(
                sequence_id="cart_recovery",
                name="Recuperação de Carrinho",
                trigger_event="cart_abandonment",
                steps=[
                    {
                        'type': 'send_email',
                        'config': {
                            'template': 'cart_recovery_1h',
                            'subject': 'Esqueceu alguma coisa? 🤔',
                            'delay_minutes': 60
                        }
                    },
                    {
                        'type': 'send_whatsapp',
                        'config': {
                            'template': 'cart_recovery_whatsapp',
                            'message': 'Oi {{nome}}! Vi que você quase fechou sua compra. Tem alguma dúvida? Posso ajudar! 😊',
                            'delay_minutes': 120
                        }
                    },
                    {
                        'type': 'send_email',
                        'config': {
                            'template': 'cart_recovery_24h',
                            'subject': 'Última chance: Oferta especial expira em breve! ⏰',
                            'delay_minutes': 1440
                        }
                    }
                ],
                active=True,
                created_at=datetime.now(timezone.utc)
            )
            
            # Sequência 3: Pós-compra
            onboarding_sequence = AutomationSequence(
                sequence_id="onboarding",
                name="Onboarding Pós-compra",
                trigger_event="purchase_completed",
                steps=[
                    {
                        'type': 'send_email',
                        'config': {
                            'template': 'thank_you',
                            'subject': 'Sua compra foi confirmada! 🎉',
                            'delay_minutes': 0
                        }
                    },
                    {
                        'type': 'send_email',
                        'config': {
                            'template': 'onboarding_guide',
                            'subject': 'Como começar com VIPNEXUS IA - Guia passo a passo',
                            'delay_minutes': 1440
                        }
                    }
                ],
                active=True,
                created_at=datetime.now(timezone.utc)
            )
            
            # Adicionar sequências ao engine
            sequences = [welcome_sequence, cart_recovery_sequence, onboarding_sequence]
            
            for seq in sequences:
                if seq.sequence_id not in self.active_sequences:
                    self.active_sequences[seq.sequence_id] = seq
                    logger.info(f"Sequência carregada: {seq.name}")
            
            # Salvar sequências ativas
            await self._save_active_sequences()
            
        except Exception as e:
            logger.error(f"Erro ao inicializar sequências padrão: {e}")
            raise
    
    def _get_triggers_for_status(self, status: str) -> List[str]:
        """Obter triggers baseados no status do lead"""
        status_triggers = {
            'novo': ['welcome_sequence'],
            'contatado': ['follow_up_24h'],
            'qualificado': ['sales_sequence'],
            'vendido': ['onboarding_sequence'],
            'perdido': ['winback_sequence']
        }
        
        return status_triggers.get(status, [])
    
    # ==================== FILE OPERATIONS ====================
    
    async def _load_minimax_config(self) -> Optional[Dict[str, Any]]:
        """Carregar configuração MiniMax"""
        try:
            if not MINIMAX_CONFIG_PATH.exists():
                logger.warning(f"Configuração MiniMax não encontrada: {MINIMAX_CONFIG_PATH}")
                return None
            
            async with aiofiles.open(MINIMAX_CONFIG_PATH, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Extrair configuração JavaScript
            import re
            config_match = re.search(r'const FUNIL_CONFIG = ({.*?});', content, re.DOTALL)
            
            if config_match:
                config_str = config_match.group(1)
                # Limpar formato JavaScript para JSON
                config_str = re.sub(r'(\w+):', r'"\1":', config_str)
                config_str = config_str.replace("'", '"')
                return json.loads(config_str)
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao carregar configuração MiniMax: {e}")
            return None
    
    async def _load_active_sequences(self):
        """Carregar sequências ativas do arquivo"""
        try:
            if ACTIVE_SEQUENCES_FILE.exists():
                async with aiofiles.open(ACTIVE_SEQUENCES_FILE, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    sequences_data = json.loads(content)
                
                for seq_data in sequences_data:
                    sequence = AutomationSequence(**seq_data)
                    self.active_sequences[sequence.sequence_id] = sequence
                
                logger.info(f"Carregadas {len(sequences_data)} sequências ativas")
            
        except Exception as e:
            logger.error(f"Erro ao carregar sequências ativas: {e}")
    
    async def _save_active_sequences(self):
        """Salvar sequências ativas no arquivo"""
        try:
            sequences_data = [asdict(seq) for seq in self.active_sequences.values()]
            
            async with aiofiles.open(ACTIVE_SEQUENCES_FILE, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(sequences_data, indent=2, default=str, ensure_ascii=False))
            
            logger.info(f"Salvas {len(sequences_data)} sequências ativas")
            
        except Exception as e:
            logger.error(f"Erro ao salvar sequências ativas: {e}")
    
    async def _save_sequence_instance(self, instance: Dict[str, Any]):
        """Salvar instance de sequência"""
        try:
            instances_file = HYBRID_DATA_DIR / 'sequence_instances.json'
            
            # Carregar instances existentes
            if instances_file.exists():
                async with aiofiles.open(instances_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    instances = json.loads(content)
            else:
                instances = {}
            
            # Atualizar instance
            instances[instance['instance_id']] = instance
            
            # Salvar
            async with aiofiles.open(instances_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(instances, indent=2, default=str, ensure_ascii=False))
                
        except Exception as e:
            logger.error(f"Erro ao salvar instance de sequência: {e}")
    
    async def _log_automation_action(self, action: str, event: AutomationEvent, config: Dict[str, Any]):
        """Log da ação de automação"""
        try:
            log_entry = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'action': action,
                'event_id': event.event_id,
                'lead_email': event.lead_email,
                'sequence_id': event.sequence_id,
                'config': config
            }
            
            # Salvar em arquivo de log de automações
            log_file = HYBRID_DATA_DIR / 'automation_log.json'
            
            if log_file.exists():
                async with aiofiles.open(log_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    logs = json.loads(content)
            else:
                logs = []
            
            logs.append(log_entry)
            
            # Manter apenas últimos 1000 logs
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            async with aiofiles.open(log_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(logs, indent=2, ensure_ascii=False))
                
        except Exception as e:
            logger.error(f"Erro ao loggar ação de automação: {e}")
    
    async def get_automation_status(self) -> Dict[str, Any]:
        """Obter status das automações"""
        try:
            # Contar sequências ativas
            active_sequences = len([seq for seq in self.active_sequences.values() if seq.active])
            
            # Carregar instances de sequências
            instances_file = HYBRID_DATA_DIR / 'sequence_instances.json'
            if instances_file.exists():
                async with aiofiles.open(instances_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    instances = json.loads(content)
                
                running_instances = len([inst for inst in instances.values() if inst.get('status') == 'running'])
                completed_instances = len([inst for inst in instances.values() if inst.get('status') == 'completed'])
            else:
                instances = {}
                running_instances = 0
                completed_instances = 0
            
            # Contar eventos na fila
            queue_size = self.event_queue.qsize()
            
            return {
                'success': True,
                'active_sequences': active_sequences,
                'total_sequences': len(self.active_sequences),
                'running_instances': running_instances,
                'completed_instances': completed_instances,
                'event_queue_size': queue_size,
                'minimax_config_loaded': self.minimax_config is not None
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status das automações: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# ==================== MAIN FUNCTIONS ====================

async def main():
    """Função principal para testes"""
    engine = AutomationTriggerEngine()
    
    try:
        await engine.initialize()
        
        # Testar trigger de captura de lead
        test_lead = {
            'lead_id': 'test_lead_001',
            'nome': 'João Silva',
            'email': 'joao@teste.com',
            'telefone': '11999999999'
        }
        
        result = await engine.trigger_lead_capture(test_lead)
        print("Resultado trigger lead_capture:", json.dumps(result, indent=2))
        
        # Obter status
        status = await engine.get_automation_status()
        print("Status automações:", json.dumps(status, indent=2))
        
    except Exception as e:
        logger.error(f"Erro no main: {e}")

if __name__ == "__main__":
    asyncio.run(main())
