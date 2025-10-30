# 🚀 VIPNEXUS IA - Sistema de Funil Híbrido de Vendas

## 📋 Sobre o Projeto

Sistema completo de **funil de vendas automatizado** desenvolvido sob o protocolo **PNA 2.0 (ARGOS)**, com foco em:
- Captação de leads qualificados
- Nutrição automática via e-mail e WhatsApp
- Integração com checkout de pagamento
- Painel administrativo completo

## 🛠️ Stack Tecnológica

### Backend
- **FastAPI** (Python 3.11+)
- **MongoDB** (Banco de dados NoSQL)
- **JWT** (Autenticação)
- **Pydantic** (Validação de dados)

### Frontend
- **React** 19.0
- **Tailwind CSS** (Estilização)
- **Shadcn/UI** (Componentes)
- **React Router** (Navegação)
- **Axios** (Requisições HTTP)
- **Sonner** (Notificações toast)

## 📦 Estrutura do Projeto

```
/app/
├── backend/
│   ├── server.py          # API FastAPI principal
│   ├── .env               # Variáveis de ambiente
│   └── requirements.txt   # Dependências Python
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx       # Página de captura de leads
│   │   │   ├── ConfirmacaoPage.jsx   # Página de pré-venda
│   │   │   ├── CheckoutPage.jsx      # Checkout (preparado para Mercado Pago)
│   │   │   ├── AdminLogin.jsx        # Login do admin
│   │   │   └── AdminDashboard.jsx    # Dashboard administrativo
│   │   ├── components/ui/            # Componentes Shadcn
│   │   ├── App.js
│   │   └── App.css
│   ├── .env               # Variáveis de ambiente
│   └── package.json       # Dependências Node
│
└── README.md
```

## 🚀 URLs e Acessos

### URLs Públicas
- **Landing Page**: https://hybrid-nexus.preview.emergentagent.com/
- **Página de Confirmação**: https://hybrid-nexus.preview.emergentagent.com/confirmacao
- **Checkout**: https://hybrid-nexus.preview.emergentagent.com/checkout

### Área Administrativa
- **Login Admin**: https://hybrid-nexus.preview.emergentagent.com/admin/login
- **Dashboard**: https://hybrid-nexus.preview.emergentagent.com/admin/dashboard

### Credenciais de Acesso (Admin)
```
Email: admin@vipnexus.com
Senha: admin123
```

## 🔌 API Endpoints

### Públicos
- `POST /api/leads` - Criar novo lead

### Autenticados (Admin)
- `POST /api/auth/login` - Login de administrador
- `GET /api/auth/me` - Informações do usuário logado
- `GET /api/leads` - Listar todos os leads
- `GET /api/leads/:id` - Obter lead específico
- `PATCH /api/leads/:id` - Atualizar status do lead
- `GET /api/stats` - Estatísticas do funil

## ✨ Funcionalidades Implementadas (MVP Core)

### ✅ Landing Page
- Design moderno com gradiente azul-escuro e detalhes dourados
- Formulário de captura com validação
- Seções: Hero, Vídeo demonstrativo, Prova social
- Responsivo (mobile-first)
- Toast notifications para feedback

### ✅ Fluxo de Leads
- Captura automática de leads via formulário
- Armazenamento no MongoDB
- Redirecionamento para página de confirmação

### ✅ Página de Confirmação/Pré-venda
- Apresentação da oferta exclusiva
- Grid de benefícios
- Precificação clara (com desconto)
- Lista de bônus inclusos
- CTA para checkout

### ✅ Checkout (Estrutura preparada)
- Formulário de dados do comprador
- Resumo do pedido
- Preparado para integração com Mercado Pago

### ✅ Painel Administrativo
- Autenticação JWT segura
- Dashboard com KPIs:
  - Total de leads
  - Leads novos
  - Leads qualificados
  - Taxa de conversão
- Tabela de leads com:
  - Busca por nome/email/telefone
  - Filtro por status
  - Alteração de status em tempo real
  - Exportação para CSV
- Design com glass-morphism e backdrop blur

## 🔮 Próximas Integrações (Fase 2)

### WhatsApp Business Cloud API
- Envio automático de mensagem de boas-vindas
- Webhooks para recebimento de respostas
- Follow-up automático em 48h

### SendGrid (E-mail)
- E-mail de boas-vindas
- Sequência de nutrição
- Carrinho abandonado (30min)

### Mercado Pago (Checkout)
- Integração completa de pagamento
- Validação automática de transações
- Webhooks para confirmação

## 🔧 Variáveis de Ambiente

### Backend (.env)
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="vipnexus_funil"
CORS_ORIGINS="*"
JWT_SECRET="vipnexus-jwt-secret-change-in-production-2025"
```

### Frontend (.env)
```env
REACT_APP_BACKEND_URL=https://hybrid-nexus.preview.emergentagent.com
```

## 📊 Status dos Leads

O sistema suporta os seguintes status de leads:
- **novo**: Lead acabou de se cadastrar
- **contatado**: Primeiro contato realizado
- **qualificado**: Lead demonstrou interesse
- **vendido**: Compra finalizada
- **perdido**: Lead não converteu

## 🎨 Design System

### Cores Principais
- **Primary**: Azul escuro (#1e3a8a)
- **Accent**: Dourado (#d4af37)
- **Background**: Gradiente de azul-escuro

### Tipografia
- **Headings**: Space Grotesk (700)
- **Body**: Inter (300-700)

### Componentes
- Shadcn/UI components
- Glass-morphism effects
- Backdrop blur
- Smooth transitions

## 🧪 Testando a Aplicação

### 1. Testar Captura de Lead
```bash
curl -X POST "https://hybrid-nexus.preview.emergentagent.com/api/leads" \
-H "Content-Type: application/json" \
-d '{"nome":"Teste","email":"teste@email.com","telefone":"11999999999"}'
```

### 2. Login Admin
```bash
curl -X POST "https://hybrid-nexus.preview.emergentagent.com/api/auth/login" \
-H "Content-Type: application/json" \
-d '{"email":"admin@vipnexus.com","password":"admin123"}'
```

### 3. Obter Estatísticas (com token)
```bash
curl -X GET "https://hybrid-nexus.preview.emergentagent.com/api/stats" \
-H "Authorization: Bearer {SEU_TOKEN}"
```

## 📈 KPIs Monitorados

- Total de leads capturados
- Novos leads (últimas 24h)
- Leads qualificados
- Taxa de conversão (%)
- Leads vendidos

## 🔒 Segurança

- JWT para autenticação
- Senhas criptografadas com bcrypt
- CORS configurado
- Validação de dados com Pydantic
- HTTPOnly tokens

## 📱 Responsividade

Todas as páginas são completamente responsivas:
- Mobile (< 768px)
- Tablet (768px - 1024px)
- Desktop (> 1024px)

## 🚀 Deploy

O sistema está configurado para rodar em ambiente Kubernetes com:
- Backend na porta 8001
- Frontend na porta 3000
- MongoDB local
- Supervisor para gerenciamento de processos

## 📝 Licença

Sistema desenvolvido sob **protocolo PNA 2.0** (ARGOS – Base de Comando / VIPNEXUS IA).

## 🤝 Suporte

Para dúvidas ou suporte:
- Email: admin@vipnexus.com
- Dashboard Admin: /admin/dashboard

---

**© 2025 VIPNEXUS IA - Todos os direitos reservados.**
