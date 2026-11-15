import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import { 
  FolderKanban, 
  Users, 
  DollarSign, 
  AlertCircle, 
  ArrowUpRight,
  TrendingUp,
  PieChart as PieIcon
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';

const STATUS_COLORS: Record<string, string> = {
  Planning: '#94a3b8',
  'In Progress': '#2563eb',
  'In Review': '#f59e0b',
  Completed: '#10b981',
  'On Hold': '#f43f5e',
};

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const data = await api.getDashboardMetrics();
        setMetrics(data);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch dashboard metrics');
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-16">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const kpis = [
    {
      label: 'Active Projects',
      value: metrics?.active_projects ?? 0,
      icon: FolderKanban,
      color: 'text-blue-600',
      action: () => navigate('/projects'),
      note: 'Delivery in progress',
    },
    {
      label: 'Total Clients',
      value: metrics?.total_clients ?? 0,
      icon: Users,
      color: 'text-slate-700',
      action: () => navigate('/clients'),
      note: 'Registered accounts',
    },
    {
      label: 'Overdue Tasks',
      value: metrics?.overdue_tasks ?? 0,
      icon: AlertCircle,
      color: metrics?.overdue_tasks > 0 ? 'text-rose-500' : 'text-emerald-500',
      action: () => navigate('/kanban'),
      note: metrics?.overdue_tasks > 0 ? 'Action required' : 'All clear',
    },
    {
      label: 'Collected Revenue',
      value: `$${(metrics?.total_revenue ?? 0).toLocaleString(undefined, { minimumFractionDigits: 0 })}`,
      icon: DollarSign,
      color: 'text-emerald-600',
      action: () => navigate('/invoices'),
      note: `+$${(metrics?.pending_revenue ?? 0).toLocaleString()} pending`,
    },
  ];

  const monthlyRevenue = metrics?.monthly_revenue || [];
  const statusData = metrics?.project_status_breakdown || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Executive Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">
          Welcome back, {user?.full_name}! Real-time operational health and revenue breakdown.
        </p>
      </div>

      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-lg">
          {error}
        </div>
      )}

      {/* Top 4 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div
              key={idx}
              onClick={kpi.action}
              className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-300 cursor-pointer transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between text-slate-500 text-xs font-semibold uppercase tracking-wider mb-2">
                  <span>{kpi.label}</span>
                  <Icon className={`w-4 h-4 ${kpi.color}`} />
                </div>
                <div className="text-2xl font-bold text-slate-900">{kpi.value}</div>
              </div>
              <p className="text-xs text-slate-400 font-medium mt-2 flex items-center gap-1">
                <ArrowUpRight className="w-3 h-3 text-slate-400" />
                {kpi.note}
              </p>
            </div>
          );
        })}
      </div>

      {/* Recharts Analytics Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue Trend Chart (2 columns) */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-blue-600" />
              <h3 className="font-bold text-sm text-slate-900">Revenue Trend (Last 6 Months)</h3>
            </div>
            <span className="text-xs text-slate-400">Total Billed Distribution</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthlyRevenue} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                <Tooltip
                  formatter={(value: any) => [`$${Number(value).toFixed(2)}`, 'Revenue']}
                  contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="revenue" fill="#2563eb" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Project Status Distribution (1 column) */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <PieIcon className="w-4 h-4 text-blue-600" />
              <h3 className="font-bold text-sm text-slate-900">Project Distribution</h3>
            </div>

            <div className="h-48 w-full flex items-center justify-center">
              {statusData.length === 0 ? (
                <div className="text-xs text-slate-400">No project data available</div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={statusData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={75}
                      paddingAngle={4}
                    >
                      {statusData.map((entry: any, index: number) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={STATUS_COLORS[entry.name] || '#3b82f6'}
                        />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          {/* Legend */}
          <div className="pt-4 border-t border-slate-100 grid grid-cols-2 gap-2 text-[11px] text-slate-500">
            {statusData.map((item: any) => (
              <div key={item.name} className="flex items-center gap-1.5">
                <div
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: STATUS_COLORS[item.name] || '#3b82f6' }}
                ></div>
                <span className="truncate">{item.name} ({item.value})</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Navigation Cards */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <h3 className="font-bold text-sm text-slate-900 mb-3">Workspace Operations</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <button
            onClick={() => navigate('/clients')}
            className="p-4 rounded-xl border border-slate-200 hover:bg-slate-50 text-left transition-colors"
          >
            <div className="font-semibold text-sm text-slate-900 flex items-center gap-2">
              <Users className="w-4 h-4 text-blue-600" />
              Clients Directory
            </div>
            <div className="text-xs text-slate-500 mt-1">Manage contact records, accounts, and billing totals</div>
          </button>
          <button
            onClick={() => navigate('/projects')}
            className="p-4 rounded-xl border border-slate-200 hover:bg-slate-50 text-left transition-colors"
          >
            <div className="font-semibold text-sm text-slate-900 flex items-center gap-2">
              <FolderKanban className="w-4 h-4 text-blue-600" />
              Projects & Budgets
            </div>
            <div className="text-xs text-slate-500 mt-1">Delivery milestones, deadlines, and financial bounds</div>
          </button>
          <button
            onClick={() => navigate('/invoices')}
            className="p-4 rounded-xl border border-slate-200 hover:bg-slate-50 text-left transition-colors"
          >
            <div className="font-semibold text-sm text-slate-900 flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-emerald-600" />
              Issue Invoices
            </div>
            <div className="text-xs text-slate-500 mt-1">Vector PDF receipts, line item math, and tax calculation</div>
          </button>
        </div>
      </div>
    </div>
  );
};
