import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { toast } from 'sonner';
import { Lock, Loader2, Sparkles } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AdminLogin() {
  const navigate = useNavigate();
  const [credentials, setCredentials] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/login`, credentials);
      localStorage.setItem('vipnexus_token', response.data.access_token);
      localStorage.setItem('vipnexus_user', JSON.stringify(response.data.user));
      toast.success('Login realizado com sucesso!');
      navigate('/admin/dashboard');
    } catch (error) {
      console.error('Erro no login:', error);
      toast.error('Email ou senha inválidos');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setCredentials({ ...credentials, [e.target.name]: e.target.value });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 text-white flex items-center justify-center px-6">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-4">
            <Sparkles className="w-10 h-10 text-amber-400" />
            <span className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-amber-200 bg-clip-text text-transparent">
              VIPNEXUS IA
            </span>
          </div>
          <p className="text-slate-400">Painel Administrativo</p>
        </div>

        {/* Login Card */}
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-br from-amber-400/20 to-blue-500/20 rounded-3xl blur-3xl"></div>
          <div className="relative p-8 rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-slate-800/50">
            <div className="flex items-center gap-2 mb-6">
              <Lock className="w-5 h-5 text-amber-400" />
              <h2 className="text-2xl font-bold">Login</h2>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="email" className="text-slate-300">Email</Label>
                <Input
                  id="email"
                  name="email"
                  data-testid="admin-input-email"
                  type="email"
                  required
                  value={credentials.email}
                  onChange={handleChange}
                  className="mt-1 bg-slate-950/50 border-slate-700 text-white focus:border-amber-400"
                  placeholder="admin@vipnexus.com"
                />
              </div>

              <div>
                <Label htmlFor="password" className="text-slate-300">Senha</Label>
                <Input
                  id="password"
                  name="password"
                  data-testid="admin-input-password"
                  type="password"
                  required
                  value={credentials.password}
                  onChange={handleChange}
                  className="mt-1 bg-slate-950/50 border-slate-700 text-white focus:border-amber-400"
                  placeholder="••••••••"
                />
              </div>

              <Button
                type="submit"
                data-testid="btn-admin-login"
                disabled={loading}
                className="w-full bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-600 hover:to-amber-500 text-slate-950 font-semibold py-6 text-lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Entrando...
                  </>
                ) : (
                  'Entrar'
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-slate-500">
                Use as credenciais fornecidas pelo sistema
              </p>
            </div>
          </div>
        </div>

        {/* Back to site */}
        <div className="text-center mt-6">
          <Button
            variant="ghost"
            onClick={() => navigate('/')}
            className="text-slate-400 hover:text-amber-400"
          >
            ← Voltar ao site
          </Button>
        </div>
      </div>
    </div>
  );
}