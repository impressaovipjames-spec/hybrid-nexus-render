import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { 
  LogOut, 
  Users, 
  TrendingUp, 
  DollarSign, 
  Target,
  Search,
  Download,
  Sparkles
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState(null);
  const [leads, setLeads] = useState([]);
  const [filteredLeads, setFilteredLeads] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('todos');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const userData = localStorage.getItem('vipnexus_user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
    fetchData();
  }, []);

  useEffect(() => {
    filterLeads();
  }, [searchTerm, statusFilter, leads]);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('vipnexus_token');
    return { headers: { Authorization: `Bearer ${token}` } };
  };

  const fetchData = async () => {
    try {
      const [statsRes, leadsRes] = await Promise.all([
        axios.get(`${API}/stats`, getAuthHeaders()),
        axios.get(`${API}/leads`, getAuthHeaders())
      ]);
      setStats(statsRes.data);
      setLeads(leadsRes.data);
      setFilteredLeads(leadsRes.data);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      if (error.response?.status === 401) {
        toast.error('Sessão expirada');
        handleLogout();
      }
    } finally {
      setLoading(false);
    }
  };

  const filterLeads = () => {
    let filtered = leads;
    
    if (statusFilter !== 'todos') {
      filtered = filtered.filter(lead => lead.status === statusFilter);
    }
    
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(lead => 
        lead.nome.toLowerCase().includes(term) ||
        lead.email.toLowerCase().includes(term) ||
        lead.telefone.includes(term)
      );
    }
    
    setFilteredLeads(filtered);
  };

  const handleLogout = () => {
    localStorage.removeItem('vipnexus_token');
    localStorage.removeItem('vipnexus_user');
    navigate('/admin/login');
  };

  const handleStatusChange = async (leadId, newStatus) => {
    try {
      await axios.patch(`${API}/leads/${leadId}`, { status: newStatus }, getAuthHeaders());
      toast.success('Status atualizado!');
      fetchData();
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      toast.error('Erro ao atualizar status');
    }
  };

  const exportCSV = () => {
    const headers = ['Nome', 'Email', 'Telefone', 'Status', 'Data'];
    const rows = filteredLeads.map(lead => [
      lead.nome,
      lead.email,
      lead.telefone,
      lead.status,
      new Date(lead.timestamp).toLocaleDateString('pt-BR')
    ]);
    
    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `leads-vipnexus-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    toast.success('CSV exportado com sucesso!');
  };

  const getStatusBadge = (status) => {
    const variants = {
      novo: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
      contatado: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
      qualificado: 'bg-purple-500/20 text-purple-400 border-purple-500/50',
      vendido: 'bg-green-500/20 text-green-400 border-green-500/50',
      perdido: 'bg-red-500/20 text-red-400 border-red-500/50',
    };
    return variants[status] || variants.novo;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Carregando...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-slate-800/50 bg-slate-950/70 backdrop-blur-md sticky top-0 z-50">
        <nav className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-8 h-8 text-amber-400" />
            <span className="text-2xl font-bold bg-gradient-to-r from-amber-400 to-amber-200 bg-clip-text text-transparent">
              VIPNEXUS IA
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-400">Olá, {user?.nome}</span>
            <Button
              data-testid="btn-logout"
              onClick={handleLogout}
              variant="ghost"
              className="text-slate-400 hover:text-red-400"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sair
            </Button>
          </div>
        </nav>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[
            { icon: Users, label: 'Total de Leads', value: stats?.total_leads || 0, color: 'text-blue-400' },
            { icon: Target, label: 'Novos Leads', value: stats?.leads_novos || 0, color: 'text-yellow-400' },
            { icon: TrendingUp, label: 'Qualificados', value: stats?.leads_qualificados || 0, color: 'text-purple-400' },
            { icon: DollarSign, label: 'Taxa Conversão', value: `${stats?.taxa_conversao || 0}%`, color: 'text-green-400' },
          ].map((stat, idx) => (
            <div key={idx} className="p-6 rounded-2xl bg-slate-900/50 backdrop-blur-sm border border-slate-800/50">
              <div className="flex items-center justify-between mb-2">
                <stat.icon className={`w-8 h-8 ${stat.color}`} />
                <span className={`text-3xl font-bold ${stat.color}`}>{stat.value}</span>
              </div>
              <p className="text-slate-400 text-sm">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* Filters and Actions */}
        <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800/50 rounded-2xl p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="flex flex-col md:flex-row gap-4 w-full md:w-auto">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-500" />
                <Input
                  data-testid="search-leads"
                  type="text"
                  placeholder="Buscar leads..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-slate-950/50 border-slate-700 text-white min-w-[250px]"
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger data-testid="filter-status" className="bg-slate-950/50 border-slate-700 text-white min-w-[150px]">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos</SelectItem>
                  <SelectItem value="novo">Novos</SelectItem>
                  <SelectItem value="contatado">Contatados</SelectItem>
                  <SelectItem value="qualificado">Qualificados</SelectItem>
                  <SelectItem value="vendido">Vendidos</SelectItem>
                  <SelectItem value="perdido">Perdidos</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button
              data-testid="btn-export-csv"
              onClick={exportCSV}
              className="bg-amber-500 hover:bg-amber-600 text-slate-950 font-semibold"
            >
              <Download className="w-4 h-4 mr-2" />
              Exportar CSV
            </Button>
          </div>
        </div>

        {/* Leads Table */}
        <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800/50 rounded-2xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-950/50">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Nome</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Email</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">WhatsApp</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Status</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Data</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {filteredLeads.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-8 text-center text-slate-500">
                      Nenhum lead encontrado
                    </td>
                  </tr>
                ) : (
                  filteredLeads.map((lead) => (
                    <tr key={lead.id} data-testid={`lead-row-${lead.id}`} className="hover:bg-slate-800/20">
                      <td className="px-6 py-4 text-sm">{lead.nome}</td>
                      <td className="px-6 py-4 text-sm text-slate-400">{lead.email}</td>
                      <td className="px-6 py-4 text-sm text-slate-400">{lead.telefone}</td>
                      <td className="px-6 py-4">
                        <Badge className={`${getStatusBadge(lead.status)} border`}>
                          {lead.status}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-400">
                        {new Date(lead.timestamp).toLocaleDateString('pt-BR')}
                      </td>
                      <td className="px-6 py-4">
                        <Select 
                          value={lead.status} 
                          onValueChange={(value) => handleStatusChange(lead.id, value)}
                        >
                          <SelectTrigger className="bg-slate-950/50 border-slate-700 text-white text-xs h-8 w-32">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="novo">Novo</SelectItem>
                            <SelectItem value="contatado">Contatado</SelectItem>
                            <SelectItem value="qualificado">Qualificado</SelectItem>
                            <SelectItem value="vendido">Vendido</SelectItem>
                            <SelectItem value="perdido">Perdido</SelectItem>
                          </SelectContent>
                        </Select>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}