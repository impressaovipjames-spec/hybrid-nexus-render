# 📋 Guia de Integrações - Fase 2

Este documento contém as instruções para implementar as integrações de **WhatsApp Business Cloud API**, **SendGrid** e **Mercado Pago** no sistema VIPNEXUS IA.

## 🔌 Integrações Pendentes

### 1. WhatsApp Business Cloud API (Meta)

#### Requisitos
- Conta no Facebook Business Manager
- Número de telefone verificado
- App criado no Meta for Developers
- Token de acesso permanente

#### Passos para Obter Credenciais

1. **Criar App no Meta for Developers**
   - Acesse: https://developers.facebook.com/
   - Crie um novo app tipo "Business"
   - Adicione o produto "WhatsApp"

2. **Configurar WhatsApp Business API**
   - No painel do app, vá em WhatsApp > Getting Started
   - Adicione e verifique seu número de telefone
   - Gere um token de acesso permanente

3. **Obter Credenciais**
   - **Phone Number ID**: ID do número de telefone verificado
   - **WhatsApp Business Account ID**: ID da conta WhatsApp Business
   - **Access Token**: Token de acesso permanente
   - **Verify Token**: Token para webhooks (você cria)

#### Variáveis de Ambiente Necessárias

Adicionar ao `/app/backend/.env`:
```env
WHATSAPP_TOKEN="seu_token_de_acesso"
WHATSAPP_PHONE_ID="seu_phone_number_id"
WHATSAPP_VERIFY_TOKEN="seu_verify_token_customizado"
WHATSAPP_BUSINESS_ACCOUNT_ID="seu_business_account_id"
```

#### Funcionalidades a Implementar

1. **Envio Automático ao Capturar Lead**
   - Endpoint backend: `POST /api/whatsapp/send`
   - Disparar após criação de lead
   - Mensagem: "Olá [Nome], aqui é da equipe VIPNEXUS IA! Recebemos seu interesse. Como podemos te ajudar?"

2. **Webhook para Receber Mensagens**
   - Endpoint: `POST /api/whatsapp/webhook`
   - Validação do verify token
   - Processamento de mensagens recebidas
   - Armazenar conversas no MongoDB

3. **Follow-up Automático (48h)**
   - Criar job/scheduler (APScheduler)
   - Verificar leads sem resposta
   - Enviar mensagem de follow-up

#### Documentação Oficial
- https://developers.facebook.com/docs/whatsapp/cloud-api/

---

### 2. SendGrid (E-mail)

#### Requisitos
- Conta no SendGrid
- Domínio verificado (ou usar sandbox)
- API Key criada

#### Passos para Obter Credenciais

1. **Criar Conta SendGrid**
   - Acesse: https://sendgrid.com/
   - Crie uma conta gratuita (até 100 emails/dia)

2. **Gerar API Key**
   - Settings > API Keys
   - Criar nova API Key com permissão "Full Access"
   - Copiar e guardar a key (só aparece uma vez)

3. **Verificar Sender Identity**
   - Settings > Sender Authentication
   - Verificar um email ou domínio

#### Variáveis de Ambiente Necessárias

Adicionar ao `/app/backend/.env`:
```env
SENDGRID_API_KEY="seu_sendgrid_api_key"
SENDGRID_FROM_EMAIL="seuemail@dominio.com"
SENDGRID_FROM_NAME="VIPNEXUS IA"
```

#### Dependência Python
```bash
pip install sendgrid
```

#### Funcionalidades a Implementar

1. **E-mail de Boas-vindas**
   - Disparar após criação de lead
   - Template profissional
   - Link para página de confirmação

2. **E-mail de Carrinho Abandonado**
   - Scheduler que verifica leads na página de confirmação há 30min
   - Sem compra finalizada
   - Lembrete com oferta especial

3. **E-mail de Nutrição (Sequência)**
   - Dia 1: Boas-vindas
   - Dia 3: Estudos de caso
   - Dia 7: Oferta exclusiva

#### Documentação Oficial
- https://docs.sendgrid.com/api-reference/mail-send/mail-send

---

### 3. Mercado Pago (Checkout)

#### Requisitos
- Conta Mercado Pago (Brasil)
- Aplicação criada no painel de desenvolvedores
- Credenciais de produção ou teste

#### Passos para Obter Credenciais

1. **Criar Aplicação**
   - Acesse: https://www.mercadopago.com.br/developers/
   - Vá em "Suas aplicações"
   - Crie uma nova aplicação

2. **Obter Credenciais**
   - No painel da aplicação
   - Copie: **Public Key** e **Access Token**
   - Use credenciais de teste primeiro

3. **Configurar Webhooks**
   - No painel da aplicação
   - Configure URL de notificação: `https://seu-dominio.com/api/mercadopago/webhook`

#### Variáveis de Ambiente Necessárias

Adicionar ao `/app/backend/.env`:
```env
MERCADOPAGO_ACCESS_TOKEN="seu_access_token"
MERCADOPAGO_PUBLIC_KEY="sua_public_key"
```

Adicionar ao `/app/frontend/.env`:
```env
REACT_APP_MERCADOPAGO_PUBLIC_KEY="sua_public_key"
```

#### Dependência Python
```bash
pip install mercadopago
```

#### Funcionalidades a Implementar

1. **Integração no Checkout**
   - Instalar SDK no frontend: `npm install @mercadopago/sdk-react`
   - Criar preferência de pagamento no backend
   - Renderizar Checkout Pro ou Checkout Bricks

2. **Criação de Preferência de Pagamento**
   - Endpoint: `POST /api/checkout/create-preference`
   - Dados: produto, valor, comprador
   - Retornar `preference_id`

3. **Webhook para Confirmação**
   - Endpoint: `POST /api/mercadopago/webhook`
   - Validar assinatura do Mercado Pago
   - Atualizar status do lead para "vendido"
   - Enviar e-mail de confirmação

4. **Página de Sucesso/Falha**
   - `/checkout/success` (pagamento aprovado)
   - `/checkout/failure` (pagamento recusado)
   - `/checkout/pending` (pagamento pendente)

#### Documentação Oficial
- https://www.mercadopago.com.br/developers/pt/docs/checkout-pro/landing
- https://www.mercadopago.com.br/developers/pt/docs/sdks-library/client-side/mp-instance-react

---

## 🔄 Ordem de Implementação Sugerida

1. **SendGrid** (mais simples)
   - E-mail de boas-vindas
   - Testar com leads existentes

2. **Mercado Pago**
   - Checkout funcional
   - Validação de pagamento
   - Atualização de status

3. **WhatsApp Business Cloud API**
   - Mensagem automática
   - Webhook
   - Follow-up

---

## 📝 Checklist de Implementação

### SendGrid
- [ ] Criar conta e obter API Key
- [ ] Adicionar variáveis de ambiente
- [ ] Instalar dependência `sendgrid`
- [ ] Criar função de envio de e-mail
- [ ] Integrar com criação de lead
- [ ] Criar templates HTML de e-mails
- [ ] Testar envio

### Mercado Pago
- [ ] Criar aplicação no MP
- [ ] Obter credenciais de teste
- [ ] Adicionar variáveis de ambiente
- [ ] Instalar SDK Python e React
- [ ] Criar endpoint de preferência
- [ ] Integrar frontend com Checkout
- [ ] Implementar webhook
- [ ] Criar páginas de sucesso/falha
- [ ] Testar com cartões de teste
- [ ] Migrar para produção

### WhatsApp
- [ ] Criar app no Meta for Developers
- [ ] Verificar número de telefone
- [ ] Obter credenciais
- [ ] Adicionar variáveis de ambiente
- [ ] Criar função de envio de mensagem
- [ ] Implementar webhook
- [ ] Configurar webhook no Meta
- [ ] Testar envio e recebimento
- [ ] Implementar follow-up automático

---

## 🧪 Testes

### Cartões de Teste (Mercado Pago)
```
Cartão aprovado: 5031 4332 1540 6351
CVV: 123
Validade: 11/25
Nome: APRO

Cartão recusado: 5031 4332 1540 6351
Nome: OTHE
```

### Número de Teste (WhatsApp)
Use o número de teste fornecido pelo Meta durante o desenvolvimento.

---

## 🚨 Importante

- **NUNCA** commitar credenciais no código
- Sempre usar variáveis de ambiente
- Testar em ambiente de sandbox primeiro
- Implementar tratamento de erros robusto
- Adicionar logs para debug
- Validar webhooks com assinatura

---

## 📚 Recursos Adicionais

- **FastAPI Background Tasks**: Para envios assíncronos
- **APScheduler**: Para jobs agendados (follow-up)
- **MongoDB**: Armazenar histórico de mensagens/emails
- **Logs**: Usar logging do Python para rastreamento

---

## 🤝 Suporte

Após obter as credenciais, execute:
```bash
# Para testar SendGrid
curl -X POST "https://hybrid-nexus.preview.emergentagent.com/api/test/email" \
  -H "Content-Type: application/json" \
  -d '{"email":"seu@email.com"}'

# Para testar WhatsApp
curl -X POST "https://hybrid-nexus.preview.emergentagent.com/api/test/whatsapp" \
  -H "Content-Type: application/json" \
  -d '{"telefone":"5511999999999"}'
```

Quando estiver pronto para implementar, informe que as credenciais estão disponíveis e prosseguiremos com a integração!
