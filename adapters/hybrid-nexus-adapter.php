<?php
/**
 * VIPNEXUS IA - ADAPTER BRIDGE: FastAPI → PHP
 * Protocolo: PNA2-HYB-FUSION/1125A
 * 
 * Este adapter converte endpoints FastAPI do Hybrid-Nexus 
 * para formato compatível com automações MiniMax VIPNEXUS
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

// Configurações
define('MINIMAX_CONFIG_PATH', '../funil-automatico/js/config.js');
define('EDDUZ_WEBHOOK_URL', 'https://checkout.edduz.com.br/vipnexus-ia-v1-2');
define('LEADS_STORAGE_FILE', '../hybrid-fusion/data/leads_minimax.json');
define('AUTOMATION_LOG_FILE', '../hybrid-fusion/logs/automation.log');

// Função de logging
function logMessage($message, $level = 'INFO') {
    $timestamp = date('Y-m-d H:i:s');
    $logEntry = "[$timestamp] [$level] $message" . PHP_EOL;
    file_put_contents(AUTOMATION_LOG_FILE, $logEntry, FILE_APPEND | LOCK_EX);
}

// Carregar configuração MiniMax
function loadMinimaxConfig() {
    if (!file_exists(MINIMAX_CONFIG_PATH)) {
        logMessage("Configuração MiniMax não encontrada", 'ERROR');
        return null;
    }
    
    $configContent = file_get_contents(MINIMAX_CONFIG_PATH);
    // Extrair configuração JavaScript como JSON
    preg_match('/const FUNIL_CONFIG = ({.*?});/s', $configContent, $matches);
    
    if (isset($matches[1])) {
        $jsonConfig = preg_replace('/(\w+):/i', '"$1":', $matches[1]);
        $jsonConfig = preg_replace('/"/i', '"', $jsonConfig);
        $jsonConfig = preg_replace('/\'/i', '"', $jsonConfig);
        
        return json_decode($jsonConfig, true);
    }
    
    return null;
}

// Classe principal do Adapter
class HybridNexusAdapter {
    
    private $minimaxConfig;
    
    public function __construct() {
        $this->minimaxConfig = loadMinimaxConfig();
        logMessage("Adapter Hybrid-Nexus inicializado");
    }
    
    /**
     * Endpoint 1: Capturar Lead (Hybrid-Nexus → MiniMax)
     * Converte POST /api/leads para webhook Eduzz format
     */
    public function handleLeadCapture($leadData) {
        try {
            logMessage("Processando captura de lead: " . json_encode($leadData));
            
            // Converter formato FastAPI → MiniMax
            $minimaxLead = [
                'timestamp' => date('Y-m-d H:i:s'),
                'nome' => $leadData['nome'] ?? '',
                'email' => $leadData['email'] ?? '',
                'telefone' => $leadData['telefone'] ?? '',
                'status' => 'novo',
                'source' => 'hybrid_nexus_landing',
                'session_id' => session_id(),
                'ip_address' => $_SERVER['REMOTE_ADDR'] ?? '',
                'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? '',
                'referrer' => $_SERVER['HTTP_REFERER'] ?? '',
                'utm_source' => $_GET['utm_source'] ?? '',
                'utm_medium' => $_GET['utm_medium'] ?? '',
                'utm_campaign' => $_GET['utm_campaign'] ?? ''
            ];
            
            // Salvar no storage MiniMax
            $this->saveLeadToMinimaxFormat($minimaxLead);
            
            // Disparar automações
            $automationResult = $this->triggerMinimaxAutomations($minimaxLead);
            
            // Simular webhook Eduzz
            $webhookResult = $this->simulateEduzzWebhook($minimaxLead);
            
            return [
                'success' => true,
                'lead_id' => uniqid('lead_'),
                'minimax_processed' => $automationResult['success'],
                'edduz_webhook_sent' => $webhookResult['success'],
                'message' => 'Lead processado com sucesso no sistema híbrido'
            ];
            
        } catch (Exception $e) {
            logMessage("Erro ao processar lead: " . $e->getMessage(), 'ERROR');
            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }
    
    /**
     * Endpoint 2: Atualizar Status do Lead
     * Converte PATCH /api/leads/{id} para automação MiniMax
     */
    public function handleLeadStatusUpdate($leadId, $updateData) {
        try {
            logMessage("Atualizando status do lead $leadId: " . json_encode($updateData));
            
            // Carregar leads existentes
            $leads = $this->loadMinimaxLeads();
            
            // Encontrar e atualizar o lead
            $leadUpdated = false;
            foreach ($leads as &$lead) {
                if ($lead['lead_id'] === $leadId) {
                    $lead['status'] = $updateData['status'] ?? $lead['status'];
                    $lead['notas'] = $updateData['notas'] ?? $lead['notas'];
                    $lead['updated_at'] = date('Y-m-d H:i:s');
                    $leadUpdated = true;
                    break;
                }
            }
            
            if ($leadUpdated) {
                $this->saveMinimaxLeads($leads);
                
                // Disparar automação baseada no novo status
                if (isset($updateData['status'])) {
                    $this->triggerStatusBasedAutomation($leadId, $updateData['status']);
                }
                
                return [
                    'success' => true,
                    'message' => 'Status atualizado com sucesso'
                ];
            } else {
                return [
                    'success' => false,
                    'error' => 'Lead não encontrado'
                ];
            }
            
        } catch (Exception $e) {
            logMessage("Erro ao atualizar status: " . $e->getMessage(), 'ERROR');
            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }
    
    /**
     * Endpoint 3: Disparar Automação Manual
     * Endpoint customizado para triggers manuais
     */
    public function triggerAutomation($automationType, $leadData) {
        try {
            logMessage("Disparando automação manual: $automationType");
            
            switch ($automationType) {
                case 'welcome_sequence':
                    return $this->sendWelcomeSequence($leadData);
                    
                case 'follow_up_24h':
                    return $this->sendFollowUp24h($leadData);
                    
                case 'cart_abandonment':
                    return $this->sendCartAbandonment($leadData);
                    
                case '7_day_nurture':
                    return $this->start7DayNurture($leadData);
                    
                default:
                    return [
                        'success' => false,
                        'error' => 'Tipo de automação não reconhecido'
                    ];
            }
            
        } catch (Exception $e) {
            logMessage("Erro na automação $automationType: " . $e->getMessage(), 'ERROR');
            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }
    
    /**
     * Endpoint 4: Simular Webhook Eduzz
     * Converte eventos MiniMax para formato webhook Eduzz
     */
    public function handleEduzzWebhook($webhookData) {
        try {
            logMessage("Processando webhook Eduzz: " . json_encode($webhookData));
            
            // Converter formato Eduzz → MiniMax
            $minimaxEvent = [
                'event_type' => $webhookData['event_type'] ?? 'purchase',
                'transaction_id' => $webhookData['transaction_id'] ?? uniqid('txn_'),
                'customer_email' => $webhookData['customer_email'] ?? '',
                'customer_name' => $webhookData['customer_name'] ?? '',
                'product_id' => $webhookData['product_id'] ?? '',
                'product_name' => $webhookData['product_name'] ?? '',
                'amount' => $webhookData['amount'] ?? 0,
                'status' => $webhookData['status'] ?? 'approved',
                'timestamp' => date('Y-m-d H:i:s'),
                'source' => 'edduz_webhook'
            ];
            
            // Processar evento
            $result = $this->processEduzzEvent($minimaxEvent);
            
            return [
                'success' => true,
                'event_processed' => $result['success'],
                'message' => 'Webhook processado com sucesso'
            ];
            
        } catch (Exception $e) {
            logMessage("Erro ao processar webhook: " . $e->getMessage(), 'ERROR');
            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }
    
    // ==================== MÉTODOS PRIVADOS ====================
    
    private function saveLeadToMinimaxFormat($leadData) {
        // Criar diretório se não existir
        $dir = dirname(LEADS_STORAGE_FILE);
        if (!is_dir($dir)) {
            mkdir($dir, 0755, true);
        }
        
        // Carregar leads existentes
        $leads = $this->loadMinimaxLeads();
        
        // Adicionar novo lead
        $leadData['lead_id'] = uniqid('lead_');
        $leads[] = $leadData;
        
        // Salvar
        file_put_contents(LEADS_STORAGE_FILE, json_encode($leads, JSON_PRETTY_PRINT));
        
        logMessage("Lead salvo no formato MiniMax: " . $leadData['lead_id']);
    }
    
    private function loadMinimaxLeads() {
        if (!file_exists(LEADS_STORAGE_FILE)) {
            return [];
        }
        
        $content = file_get_contents(LEADS_STORAGE_FILE);
        return json_decode($content, true) ?: [];
    }
    
    private function saveMinimaxLeads($leads) {
        file_put_contents(LEADS_STORAGE_FILE, json_encode($leads, JSON_PRETTY_PRINT));
    }
    
    private function triggerMinimaxAutomations($leadData) {
        logMessage("Disparando automações MiniMax para: " . $leadData['email']);
        
        // Simular automações baseadas na configuração MiniMax
        $result = [
            'email_sent' => $this->sendWelcomeEmail($leadData),
            'whatsapp_sent' => $this->sendWelcomeWhatsApp($leadData),
            'analytics_tracked' => $this->trackGA4Event($leadData),
            'meta_pixel_tracked' => $this->trackMetaPixel($leadData),
            'crm_updated' => $this->updateCRM($leadData)
        ];
        
        return [
            'success' => true,
            'automations' => $result
        ];
    }
    
    private function simulateEduzzWebhook($leadData) {
        // Simular envio para webhook Eduzz
        $webhookPayload = [
            'event' => 'lead_captured',
            'data' => [
                'nome' => $leadData['nome'],
                'email' => $leadData['email'],
                'telefone' => $leadData['telefone'],
                'timestamp' => $leadData['timestamp'],
                'source' => 'hybrid_nexus'
            ]
        ];
        
        logMessage("Webhook simulado enviado para Eduzz: " . json_encode($webhookPayload));
        
        return ['success' => true];
    }
    
    private function sendWelcomeEmail($leadData) {
        if (!$this->minimaxConfig) return false;
        
        // Simular envio SendGrid
        logMessage("Enviando email de boas-vindas para: " . $leadData['email']);
        return true;
    }
    
    private function sendWelcomeWhatsApp($leadData) {
        if (!$this->minimaxConfig) return false;
        
        // Simular envio WhatsApp via Zenvia
        logMessage("Enviando WhatsApp de boas-vindas para: " . $leadData['telefone']);
        return true;
    }
    
    private function trackGA4Event($leadData) {
        // Simular tracking GA4
        logMessage("Tracking GA4 para: " . $leadData['email']);
        return true;
    }
    
    private function trackMetaPixel($leadData) {
        // Simular tracking Meta Pixel
        logMessage("Tracking Meta Pixel para: " . $leadData['email']);
        return true;
    }
    
    private function updateCRM($leadData) {
        // Simular atualização CRM Pipedrive
        logMessage("Atualizando CRM para: " . $leadData['email']);
        return true;
    }
    
    private function processEduzzEvent($eventData) {
        // Processar evento Eduzz e atualizar lead status
        logMessage("Processando evento Eduzz: " . $eventData['event_type']);
        return ['success' => true];
    }
    
    private function triggerStatusBasedAutomation($leadId, $newStatus) {
        logMessage("Automação baseada em status: $leadId -> $newStatus");
        // Implementar automações específicas por status
    }
    
    private function sendWelcomeSequence($leadData) {
        logMessage("Iniciando sequência de boas-vindas para: " . $leadData['email']);
        return ['success' => true];
    }
    
    private function sendFollowUp24h($leadData) {
        logMessage("Enviando follow-up 24h para: " . $leadData['email']);
        return ['success' => true];
    }
    
    private function sendCartAbandonment($leadData) {
        logMessage("Enviando email carrinho abandonado para: " . $leadData['email']);
        return ['success' => true];
    }
    
    private function start7DayNurture($leadData) {
        logMessage("Iniciando sequência 7 dias para: " . $leadData['email']);
        return ['success' => true];
    }
}

// ==================== ROTEAMENTO ====================

$adapter = new HybridNexusAdapter();
$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$path = str_replace('/hybrid-adapter/', '', $path);

try {
    switch ($path) {
        case 'lead/capture':
            if ($method === 'POST') {
                $input = json_decode(file_get_contents('php://input'), true);
                $result = $adapter->handleLeadCapture($input);
                echo json_encode($result);
            } else {
                http_response_code(405);
                echo json_encode(['error' => 'Method not allowed']);
            }
            break;
            
        case 'lead/update':
            if ($method === 'POST') {
                $input = json_decode(file_get_contents('php://input'), true);
                $leadId = $input['lead_id'] ?? '';
                $updateData = $input['update_data'] ?? [];
                $result = $adapter->handleLeadStatusUpdate($leadId, $updateData);
                echo json_encode($result);
            } else {
                http_response_code(405);
                echo json_encode(['error' => 'Method not allowed']);
            }
            break;
            
        case 'automation/trigger':
            if ($method === 'POST') {
                $input = json_decode(file_get_contents('php://input'), true);
                $automationType = $input['type'] ?? '';
                $leadData = $input['lead_data'] ?? [];
                $result = $adapter->triggerAutomation($automationType, $leadData);
                echo json_encode($result);
            } else {
                http_response_code(405);
                echo json_encode(['error' => 'Method not allowed']);
            }
            break;
            
        case 'webhook/edduz':
            if ($method === 'POST') {
                $input = json_decode(file_get_contents('php://input'), true);
                $result = $adapter->handleEduzzWebhook($input);
                echo json_encode($result);
            } else {
                http_response_code(405);
                echo json_encode(['error' => 'Method not allowed']);
            }
            break;
            
        case 'health':
            echo json_encode([
                'status' => 'ok',
                'adapter' => 'hybrid_nexus_minimax',
                'version' => '1.0.0',
                'timestamp' => date('Y-m-d H:i:s')
            ]);
            break;
            
        default:
            http_response_code(404);
            echo json_encode(['error' => 'Endpoint not found']);
            break;
    }
    
} catch (Exception $e) {
    logMessage("Erro no adapter: " . $e->getMessage(), 'ERROR');
    http_response_code(500);
    echo json_encode(['error' => 'Internal server error']);
}

?>