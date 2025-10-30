import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { toast } from 'sonner';
import { Loader2, Sparkles, TrendingUp, Users, Zap } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function LandingPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ nome: '', email: '', telefone: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await axios.post(`${API}/leads`, formData);
      toast.success('Cadastro realizado com sucesso!');
      localStorage.setItem('vipnexus_lead_nome', formData.nome);
      setTimeout(() => {
        navigate('/confirmacao');
      }, 1000);
    } catch (error) {
      console.error('Erro ao criar lead:', error);
      toast.error('Erro ao processar cadastro. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 text-white">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-slate-950/70 border-b border-slate-800/50">
        <nav className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-8 h-8 text-amber-400" />
            <span className="text-2xl font-bold bg-gradient-to-r from-amber-400 to-amber-200 bg-clip-text text-transparent">
              VIPNEXUS IA
            </span>
          </div>
          <Button 
            variant="ghost" 
            className="text-slate-300 hover:text-amber-400"
            onClick={() => navigate('/admin/login')}
          >
            Área Admin
          </Button>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="container mx-auto max-w-6xl">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="space-y-8">
              <div className="inline-block">
                <span className="text-sm font-medium px-4 py-2 rounded-full bg-amber-400/10 text-amber-400 border border-amber-400/20">
                  🚀 Protocolo PNA 2.0 - ARGOS
                </span>
              </div>
              
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight">
                Transforme Seu Negócio com{' '}
                <span className="bg-gradient-to-r from-amber-400 via-amber-300 to-amber-200 bg-clip-text text-transparent">
                  Inteligência Artificial
                </span>
              </h1>
              
              <p className="text-lg text-slate-300">
                Sistema completo de automação de vendas. Capture, nutra e converta leads automaticamente com o poder da IA. Aumente seus resultados em até 300%.
              </p>

              {/* Features Cards */}
              <div className="grid sm:grid-cols-3 gap-4 pt-4">
                <div className="p-4 rounded-xl bg-slate-900/50 backdrop-blur-sm border border-slate-800/50">
                  <Users className="w-8 h-8 text-amber-400 mb-2" />
                  <p className="text-sm font-medium">Captação Automática</p>
                </div>
                <div className="p-4 rounded-xl bg-slate-900/50 backdrop-blur-sm border border-slate-800/50">
                  <TrendingUp className="w-8 h-8 text-amber-400 mb-2" />
                  <p className="text-sm font-medium">Nutrição Inteligente</p>
                </div>
                <div className="p-4 rounded-xl bg-slate-900/50 backdrop-blur-sm border border-slate-800/50">
                  <Zap className="w-8 h-8 text-amber-400 mb-2" />
                  <p className="text-sm font-medium">Vendas 24/7</p>
                </div>
              </div>
            </div>

            {/* Right - Form */}
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-amber-400/20 to-blue-500/20 rounded-3xl blur-3xl"></div>
              <div className="relative p-8 rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-slate-800/50 shadow-2xl">
                <div className="text-center mb-6">
                  <h2 className="text-2xl font-bold mb-2">Comece Agora Gratuitamente</h2>
                  <p className="text-slate-400">Preencha os dados abaixo e descubra o poder da automação</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <Label htmlFor="nome" className="text-slate-300">Nome Completo</Label>
                    <Input
                      id="nome"
                      name="nome"
                      data-testid="input-nome"
                      type="text"
                      required
                      value={formData.nome}
                      onChange={handleChange}
                      className="mt-1 bg-slate-950/50 border-slate-700 text-white focus:border-amber-400"
                      placeholder="Seu nome"
                    />
                  </div>

                  <div>
                    <Label htmlFor="email" className="text-slate-300">Email</Label>
                    <Input
                      id="email"
                      name="email"
                      data-testid="input-email"
                      type="email"
                      required
                      value={formData.email}
                      onChange={handleChange}
                      className="mt-1 bg-slate-950/50 border-slate-700 text-white focus:border-amber-400"
                      placeholder="seu@email.com"
                    />
                  </div>

                  <div>
                    <Label htmlFor="telefone" className="text-slate-300">WhatsApp</Label>
                    <Input
                      id="telefone"
                      name="telefone"
                      data-testid="input-telefone"
                      type="tel"
                      required
                      value={formData.telefone}
                      onChange={handleChange}
                      className="mt-1 bg-slate-950/50 border-slate-700 text-white focus:border-amber-400"
                      placeholder="(11) 99999-9999"
                    />
                  </div>

                  <Button
                    type="submit"
                    data-testid="btn-submit-lead"
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-600 hover:to-amber-500 text-slate-950 font-semibold py-6 text-lg transition-all duration-300"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                        Processando...
                      </>
                    ) : (
                      'Quero Saber Mais →'
                    )}
                  </Button>
                </form>

                <p className="text-xs text-slate-500 text-center mt-4">
                  Seus dados estão seguros. Não compartilhamos suas informações.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Video Section */}
      <section className="py-20 px-6 bg-slate-950/50">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="text-3xl font-bold mb-4">Veja Como Funciona</h2>
          <p className="text-slate-400 mb-8">Conheça o sistema que está revolucionando vendas online</p>
          <div className="aspect-video rounded-2xl overflow-hidden border border-slate-800 shadow-2xl">
            <iframe
              width="100%"
              height="100%"
              src="https://www.youtube.com/embed/dQw4w9WgXcQ"
              title="VIPNEXUS IA Demo"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            ></iframe>
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="py-20 px-6">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Resultados Comprovados</h2>
            <p className="text-slate-400">Empresas que já transformaram seus resultados</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { numero: '300%', texto: 'Aumento em conversões' },
              { numero: '5.000+', texto: 'Leads capturados/mês' },
              { numero: '24/7', texto: 'Atendimento automatizado' },
            ].map((stat, idx) => (
              <div key={idx} className="text-center p-8 rounded-2xl bg-slate-900/50 backdrop-blur-sm border border-slate-800/50">
                <div className="text-4xl font-bold text-amber-400 mb-2">{stat.numero}</div>
                <p className="text-slate-300">{stat.texto}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-slate-800">
        <div className="container mx-auto text-center text-slate-500 text-sm">
          <p>© 2025 VIPNEXUS IA - Protocolo PNA 2.0 (ARGOS). Todos os direitos reservados.</p>
        </div>
      </footer>
    </div>
  );
}