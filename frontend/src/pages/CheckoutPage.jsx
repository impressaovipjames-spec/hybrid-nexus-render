import React, { useState } from 'react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { toast } from 'sonner';
import { Lock, CreditCard, ShieldCheck } from 'lucide-react';

export default function CheckoutPage() {
  const [formData, setFormData] = useState({
    nome: '',
    cpf: '',
    email: '',
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    toast.info('Integração com Mercado Pago será implementada na próxima fase!');
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 text-white">
      <header className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-slate-950/70 border-b border-slate-800/50">
        <nav className="container mx-auto px-6 py-4">
          <span className="text-2xl font-bold bg-gradient-to-r from-amber-400 to-amber-200 bg-clip-text text-transparent">
            VIPNEXUS IA
          </span>
        </nav>
      </header>

      <div className="pt-32 pb-20 px-6">
        <div className="container mx-auto max-w-5xl">
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Left - Order Summary */}
            <div>
              <h1 className="text-3xl font-bold mb-6">Resumo do Pedido</h1>
              
              <div className="p-6 rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-slate-800/50 mb-6">
                <h3 className="font-semibold text-xl mb-4">VIPNEXUS PRO - Acesso Completo</h3>
                <ul className="space-y-3 text-slate-300 mb-6">
                  <li className="flex justify-between">
                    <span>Plataforma completa</span>
                    <span>R$ 297,00</span>
                  </li>
                  <li className="flex justify-between text-green-400">
                    <span>Bônus inclusos</span>
                    <span>R$ 441,00</span>
                  </li>
                </ul>
                <div className="border-t border-slate-700 pt-4">
                  <div className="flex justify-between text-xl font-bold">
                    <span>Total</span>
                    <span className="text-amber-400">R$ 297,00</span>
                  </div>
                  <p className="text-sm text-slate-500 mt-2">ou 12x de R$ 29,70</p>
                </div>
              </div>

              <div className="flex items-center gap-3 text-sm text-slate-400">
                <ShieldCheck className="w-5 h-5 text-green-400" />
                <span>Pagamento 100% seguro via Mercado Pago</span>
              </div>
            </div>

            {/* Right - Payment Form */}
            <div>
              <div className="p-8 rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-slate-800/50">
                <div className="flex items-center gap-2 mb-6">
                  <Lock className="w-5 h-5 text-amber-400" />
                  <h2 className="text-2xl font-bold">Finalizar Pagamento</h2>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <Label htmlFor="nome" className="text-slate-300">Nome Completo</Label>
                    <Input
                      id="nome"
                      name="nome"
                      data-testid="checkout-input-nome"
                      type="text"
                      required
                      value={formData.nome}
                      onChange={handleChange}
                      className="mt-1 bg-slate-950/50 border-slate-700 text-white"
                    />
                  </div>

                  <div>
                    <Label htmlFor="cpf" className="text-slate-300">CPF</Label>
                    <Input
                      id="cpf"
                      name="cpf"
                      data-testid="checkout-input-cpf"
                      type="text"
                      required
                      value={formData.cpf}
                      onChange={handleChange}
                      className="mt-1 bg-slate-950/50 border-slate-700 text-white"
                      placeholder="000.000.000-00"
                    />
                  </div>

                  <div>
                    <Label htmlFor="email" className="text-slate-300">Email</Label>
                    <Input
                      id="email"
                      name="email"
                      data-testid="checkout-input-email"
                      type="email"
                      required
                      value={formData.email}
                      onChange={handleChange}
                      className="mt-1 bg-slate-950/50 border-slate-700 text-white"
                    />
                  </div>

                  <div className="pt-4">
                    <div className="flex items-center gap-2 mb-4 text-slate-400">
                      <CreditCard className="w-5 h-5" />
                      <span className="text-sm">Integração Mercado Pago (Em breve)</span>
                    </div>
                    
                    <Button
                      type="submit"
                      data-testid="btn-finalizar-pagamento"
                      className="w-full bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-600 hover:to-amber-500 text-slate-950 font-semibold py-6 text-lg"
                    >
                      Finalizar Pagamento →
                    </Button>
                  </div>
                </form>

                <div className="mt-6 pt-6 border-t border-slate-700">
                  <div className="flex items-center gap-4 text-xs text-slate-500">
                    <img src="https://logodownload.org/wp-content/uploads/2019/11/mercado-pago-logo-1.png" alt="Mercado Pago" className="h-6" />
                    <span>Pagamento processado com segurança</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}