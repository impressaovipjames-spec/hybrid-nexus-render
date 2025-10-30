import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { CheckCircle2, Gift, Shield, Zap, Star } from 'lucide-react';

export default function ConfirmacaoPage() {
  const navigate = useNavigate();
  const nome = localStorage.getItem('vipnexus_lead_nome') || 'Visitante';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 text-white">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-slate-950/70 border-b border-slate-800/50">
        <nav className="container mx-auto px-6 py-4">
          <span className="text-2xl font-bold bg-gradient-to-r from-amber-400 to-amber-200 bg-clip-text text-transparent">
            VIPNEXUS IA
          </span>
        </nav>
      </header>

      <div className="pt-32 pb-20 px-6">
        <div className="container mx-auto max-w-4xl">
          {/* Success Message */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-green-500/20 mb-6">
              <CheckCircle2 className="w-12 h-12 text-green-400" />
            </div>
            <h1 className="text-4xl font-bold mb-4">
              Parabéns, {nome}! 🎉
            </h1>
            <p className="text-xl text-slate-300">
              Você acaba de dar o primeiro passo rumo à transformação digital do seu negócio!
            </p>
          </div>

          {/* Offer Card */}
          <div className="relative mb-12">
            <div className="absolute inset-0 bg-gradient-to-br from-amber-400/20 to-blue-500/20 rounded-3xl blur-3xl"></div>
            <div className="relative p-8 rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-slate-800/50">
              <div className="text-center mb-6">
                <span className="inline-block px-4 py-2 rounded-full bg-amber-400/10 text-amber-400 border border-amber-400/20 text-sm font-medium mb-4">
                  OFERTA EXCLUSIVA
                </span>
                <h2 className="text-3xl font-bold mb-2">Acesso Completo VIPNEXUS PRO</h2>
                <p className="text-slate-400">Tudo que você precisa para automatizar suas vendas</p>
              </div>

              {/* Features Grid */}
              <div className="grid md:grid-cols-2 gap-4 mb-8">
                {[
                  { icon: Zap, text: 'Funil de vendas automatizado' },
                  { icon: Gift, text: 'Integração WhatsApp Business' },
                  { icon: Shield, text: 'Sistema de pagamento seguro' },
                  { icon: Star, text: 'Dashboard analytics completo' },
                ].map((feature, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-4 rounded-lg bg-slate-950/50">
                    <feature.icon className="w-6 h-6 text-amber-400 flex-shrink-0" />
                    <span className="text-slate-300">{feature.text}</span>
                  </div>
                ))}
              </div>

              {/* Pricing */}
              <div className="text-center mb-6">
                <div className="mb-2">
                  <span className="text-slate-500 line-through text-2xl">R$ 497,00</span>
                </div>
                <div className="text-5xl font-bold text-amber-400 mb-2">
                  R$ 297,00
                </div>
                <p className="text-slate-400">ou 12x de R$ 29,70</p>
              </div>

              {/* Bonuses */}
              <div className="bg-slate-950/50 rounded-xl p-6 mb-6">
                <h3 className="font-semibold mb-3 text-amber-400">Bônus Exclusivos:</h3>
                <ul className="space-y-2 text-sm text-slate-300">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-400" />
                    Templates de mensagens prontas (R$ 97)
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-400" />
                    Curso completo de automação (R$ 197)
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-400" />
                    Suporte prioritário por 30 dias (R$ 147)
                  </li>
                </ul>
              </div>

              <Button
                data-testid="btn-ir-checkout"
                onClick={() => navigate('/checkout')}
                className="w-full bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-600 hover:to-amber-500 text-slate-950 font-semibold py-6 text-lg transition-all duration-300"
              >
                Quero Entrar Agora! →
              </Button>

              <p className="text-xs text-slate-500 text-center mt-4">
                Garantia de 7 dias. Se não gostar, devolvemos 100% do seu dinheiro.
              </p>
            </div>
          </div>

          {/* Testimonials */}
          <div className="grid md:grid-cols-2 gap-6">
            {[
              { nome: 'Carlos Silva', texto: 'Tripliquei minhas vendas em 2 meses!' },
              { nome: 'Marina Santos', texto: 'Automatizei 90% do meu atendimento' },
            ].map((depoimento, idx) => (
              <div key={idx} className="p-6 rounded-xl bg-slate-900/50 backdrop-blur-sm border border-slate-800/50">
                <div className="flex gap-1 mb-3">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-amber-400 text-amber-400" />
                  ))}
                </div>
                <p className="text-slate-300 mb-3">"{depoimento.texto}"</p>
                <p className="font-medium text-amber-400">{depoimento.nome}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}