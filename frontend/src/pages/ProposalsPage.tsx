import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { Proposal, Client } from '../types';
import { 
  Lightbulb, 
  Trash2, 
  CheckCircle2, 
  AlertCircle, 
  X,
  Layers,
  Sparkles
} from 'lucide-react';

export const ProposalsPage: React.FC = () => {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [title, setTitle] = useState('');
  const [clientId, setClientId] = useState<number | ''>('');
  const [targetBudget, setTargetBudget] = useState<number | ''>(8500);
  const [rawRequirements, setRawRequirements] = useState('');
  const [generating, setGenerating] = useState(false);

  const navigate = useNavigate();

  const fetchData = async () => {
    try {
      setLoading(true);
      const [propData, clientData] = await Promise.all([
        api.getProposals(),
        api.getClients(),
      ]);
      setProposals(propData);
      setClients(clientData);
    } catch (err: any) {
      setError(err.message || 'Failed to load proposals');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleGenerateProposal = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    setError(null);

    try {
      await api.generateProposal({
        title,
        client_id: clientId ? Number(clientId) : null,
        target_budget: targetBudget ? Number(targetBudget) : 7500,
        raw_requirements: rawRequirements,
      });

      setShowModal(false);
      setTitle('');
      setClientId('');
      setRawRequirements('');
      fetchData();
    } catch (err: any) {
      setError(err.message || 'Failed to generate proposal');
    } finally {
      setGenerating(false);
    }
  };

  const handleConvertToProject = async (id: number) => {
    if (!window.confirm('Convert this proposal into an active Project? This will automatically scaffold initial project tasks.')) {
      return;
    }

    try {
      const project = await api.convertProposal(id);
      navigate(`/projects/${project.id}/kanban`);
    } catch (err: any) {
      alert(err.message || 'Conversion failed');
    }
  };

  const handleDeleteProposal = async (id: number) => {
    if (!window.confirm('Delete this proposal draft?')) return;
    try {
      await api.deleteProposal(id);
      fetchData();
    } catch (err: any) {
      alert(err.message || 'Failed to delete proposal');
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">AI Proposal Generator</h1>
          <p className="text-sm text-slate-500 mt-1">
            Transform unstructured client briefs into structured deliverables, phased milestones, and active Kanban projects
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-medium shadow-sm transition-colors"
        >
          <Sparkles className="w-4 h-4" />
          Generate Proposal
        </button>
      </div>

      {/* Proposals Grid */}
      {loading ? (
        <div className="flex items-center justify-center p-12">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : proposals.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center max-w-lg mx-auto">
          <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <Lightbulb className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-slate-900">No proposals drafted yet</h3>
          <p className="text-sm text-slate-500 mt-1">
            Paste meeting notes or client specifications to generate scope estimates, milestones, and deliverables.
          </p>
          <button
            onClick={() => setShowModal(true)}
            className="mt-5 inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
          >
            <Sparkles className="w-4 h-4" />
            Generate First Proposal
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {proposals.map((prop) => {
            let milestones: any[] = [];
            try {
              milestones = JSON.parse(prop.milestones_json);
            } catch {
              milestones = [];
            }

            return (
              <div
                key={prop.id}
                className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow transition-shadow flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <span
                      className={`inline-block px-2.5 py-1 rounded-full text-xs font-semibold border ${
                        prop.status === 'converted'
                          ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                          : 'bg-blue-50 text-blue-700 border-blue-200'
                      }`}
                    >
                      {prop.status.toUpperCase()}
                    </span>

                    <button
                      onClick={() => handleDeleteProposal(prop.id)}
                      title="Delete Proposal"
                      className="text-slate-400 hover:text-rose-600 transition-colors p-1"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <h3 className="text-lg font-bold text-slate-900 tracking-tight">{prop.title}</h3>
                  <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
                    <span>Client: <strong className="text-slate-700">{prop.client_name || 'Unassigned'}</strong></span>
                    <span>•</span>
                    <span>Estimated Budget: <strong className="text-emerald-600">${prop.estimated_budget.toLocaleString()}</strong></span>
                  </div>

                  <p className="text-xs text-slate-600 mt-3 p-3 bg-slate-50 rounded-xl leading-relaxed border border-slate-100">
                    {prop.scope_summary}
                  </p>

                  {/* Phased Milestones Accordion / Preview */}
                  <div className="mt-4 space-y-2">
                    <div className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-blue-600" />
                      Phased Deliverables ({milestones.length})
                    </div>
                    {milestones.map((m: any, idx: number) => (
                      <div key={idx} className="p-2.5 bg-slate-50/70 rounded-lg border border-slate-200 text-xs">
                        <div className="flex items-center justify-between font-semibold text-slate-800">
                          <span>{m.title}</span>
                          <span className="text-emerald-600">${m.budget?.toLocaleString()}</span>
                        </div>
                        <div className="text-[11px] text-slate-400 mt-0.5">Est: {m.estimated_days} days • {m.tasks?.length || 0} tasks</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-[11px] text-slate-400">Created: {new Date(prop.created_at).toLocaleDateString()}</span>
                  {prop.status !== 'converted' ? (
                    <button
                      onClick={() => handleConvertToProject(prop.id)}
                      className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-colors"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      Convert to Active Project
                    </button>
                  ) : (
                    <span className="text-xs font-semibold text-emerald-600 flex items-center gap-1">
                      <CheckCircle2 className="w-4 h-4" /> Converted to Project
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Generate Proposal Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg border border-slate-100 overflow-hidden my-8">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-blue-600" />
                <h3 className="font-bold text-slate-900 text-lg">Generate Project Proposal</h3>
              </div>
              <button onClick={() => setShowModal(false)} className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleGenerateProposal} className="p-6 space-y-4">
              {error && (
                <div className="flex items-center gap-2 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-lg">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Project Proposal Title *</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Mobile E-Commerce App & API Engine"
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Client (Optional)</label>
                  <select
                    value={clientId}
                    onChange={(e) => setClientId(e.target.value ? Number(e.target.value) : '')}
                    className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-600"
                  >
                    <option value="">Select client...</option>
                    {clients.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name} {c.company ? `(${c.company})` : ''}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Target Budget ($)</label>
                  <input
                    type="number"
                    min="500"
                    step="500"
                    value={targetBudget}
                    onChange={(e) => setTargetBudget(e.target.value === '' ? '' : Number(e.target.value))}
                    className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Client Requirement Brief / Notes *
                </label>
                <textarea
                  rows={5}
                  required
                  value={rawRequirements}
                  onChange={(e) => setRawRequirements(e.target.value)}
                  placeholder="Paste client email, meeting bullet points, or deliverables (e.g. 'Build a React dashboard with user auth, PostgreSQL migrations, Stripe billing, and push notifications')..."
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-600 resize-none text-slate-900"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={generating}
                  className="inline-flex items-center gap-2 px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm rounded-lg shadow-sm transition-colors disabled:opacity-50"
                >
                  {generating ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Scaffolding...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      Generate Proposal
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
