import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Users, FolderKanban, DollarSign, ArrowUpRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Executive Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">
          Welcome back, {user?.full_name}! Here is your current business overview.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div 
          onClick={() => navigate('/projects')}
          className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-300 cursor-pointer transition-all"
        >
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>Active Projects</span>
            <FolderKanban className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">4</div>
          <p className="text-xs text-emerald-600 font-medium mt-1 flex items-center gap-0.5">
            <ArrowUpRight className="w-3.5 h-3.5" /> 2 on track this week
          </p>
        </div>

        <div 
          onClick={() => navigate('/clients')}
          className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-300 cursor-pointer transition-all"
        >
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>Total Clients</span>
            <Users className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">3</div>
          <p className="text-xs text-slate-400 font-medium mt-1">1 enterprise account</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>Overdue Tasks</span>
            <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
          </div>
          <div className="text-2xl font-bold text-slate-900">0</div>
          <p className="text-xs text-emerald-600 font-medium mt-1">All deadlines clear</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>Pipeline Revenue</span>
            <DollarSign className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">$57,500</div>
          <p className="text-xs text-slate-400 font-medium mt-1">Across 4 contracts</p>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <h2 className="text-base font-bold text-slate-900 mb-3">Quick Navigation</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <button
            onClick={() => navigate('/clients')}
            className="p-4 rounded-xl border border-slate-200 hover:bg-slate-50 text-left transition-colors"
          >
            <div className="font-semibold text-sm text-slate-900">Manage Clients</div>
            <div className="text-xs text-slate-500 mt-0.5">Directory, billing totals, contact info</div>
          </button>
          <button
            onClick={() => navigate('/projects')}
            className="p-4 rounded-xl border border-slate-200 hover:bg-slate-50 text-left transition-colors"
          >
            <div className="font-semibold text-sm text-slate-900">Projects & Deadlines</div>
            <div className="text-xs text-slate-500 mt-0.5">Planning, active delivery, budget tracking</div>
          </button>
          <button
            onClick={() => navigate('/projects')}
            className="p-4 rounded-xl border border-slate-200 hover:bg-slate-50 text-left transition-colors"
          >
            <div className="font-semibold text-sm text-slate-900">Task Boards</div>
            <div className="text-xs text-slate-500 mt-0.5">Interactive drag-and-drop Kanban execution</div>
          </button>
        </div>
      </div>
    </div>
  );
};
