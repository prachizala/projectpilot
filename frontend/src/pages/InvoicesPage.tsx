import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { Invoice, Client, InvoiceItem } from '../types';
import { 
  Receipt, 
  Plus, 
  Trash2, 
  Download, 
  AlertCircle, 
  X 
} from 'lucide-react';

const STATUS_BADGES: Record<string, string> = {
  draft: 'bg-slate-100 text-slate-700 border-slate-200',
  sent: 'bg-blue-50 text-blue-700 border-blue-200',
  paid: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  overdue: 'bg-rose-50 text-rose-700 border-rose-200',
};

export const InvoicesPage: React.FC = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [clientId, setClientId] = useState<number | ''>('');
  const [issueDate, setIssueDate] = useState(new Date().toISOString().split('T')[0]);
  const [dueDate, setDueDate] = useState(
    new Date(Date.now() + 15 * 86400000).toISOString().split('T')[0]
  );
  const [taxRatePct, setTaxRatePct] = useState(18.0);
  const [notes, setNotes] = useState('');
  const [items, setItems] = useState<InvoiceItem[]>([
    { description: 'Consulting & Software Development', quantity: 1, unit_price: 1500, total: 1500 }
  ]);
  const [submitting, setSubmitting] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [invData, clientData] = await Promise.all([
        api.getInvoices(),
        api.getClients(),
      ]);
      setInvoices(invData);
      setClients(clientData);
    } catch (err: any) {
      setError(err.message || 'Failed to load invoices');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleItemChange = (index: number, field: keyof InvoiceItem, value: any) => {
    const updated = [...items];
    (updated[index] as any)[field] = value;
    if (field === 'quantity' || field === 'unit_price') {
      const q = Number(updated[index].quantity) || 0;
      const p = Number(updated[index].unit_price) || 0;
      updated[index].total = roundTwo(q * p);
    }
    setItems(updated);
  };

  const addItemRow = () => {
    setItems([...items, { description: '', quantity: 1, unit_price: 0, total: 0 }]);
  };

  const removeItemRow = (index: number) => {
    if (items.length <= 1) return;
    setItems(items.filter((_, i) => i !== index));
  };

  const roundTwo = (num: number) => Math.round((num + Number.EPSILON) * 100) / 100;

  const subtotal = roundTwo(items.reduce((sum, item) => sum + (Number(item.total) || 0), 0));
  const taxAmount = roundTwo(subtotal * (taxRatePct / 100));
  const totalAmount = roundTwo(subtotal + taxAmount);

  const handleCreateInvoice = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!clientId) {
      setError('Please select a client.');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await api.createInvoice({
        client_id: Number(clientId),
        issue_date: issueDate,
        due_date: dueDate,
        tax_rate_pct: taxRatePct,
        notes: notes || null,
        items: items.map((it) => ({
          description: it.description,
          quantity: Number(it.quantity),
          unit_price: Number(it.unit_price),
        })),
      });

      setShowModal(false);
      setClientId('');
      setItems([{ description: '', quantity: 1, unit_price: 0, total: 0 }]);
      fetchData();
    } catch (err: any) {
      setError(err.message || 'Failed to create invoice');
    } finally {
      setSubmitting(false);
    }
  };

  const handleStatusChange = async (id: number, newStatus: string) => {
    try {
      await api.updateInvoiceStatus(id, newStatus);
      fetchData();
    } catch (err: any) {
      alert(err.message || 'Failed to update status');
    }
  };

  const handleDownloadPdf = async (inv: Invoice) => {
    try {
      await api.downloadInvoicePdf(inv.id, inv.invoice_number);
    } catch (err: any) {
      alert(err.message || 'PDF download failed');
    }
  };

  const handleDeleteInvoice = async (id: number) => {
    if (!window.confirm('Delete this invoice?')) return;
    try {
      await api.deleteInvoice(id);
      fetchData();
    } catch (err: any) {
      alert(err.message || 'Failed to delete invoice');
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Invoices & Billing</h1>
          <p className="text-sm text-slate-500 mt-1">
            Automated line item calculations, taxes, vector PDF generation, and payment tracking
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-medium shadow-sm transition-colors"
        >
          <Plus className="w-4 h-4" />
          Create Invoice
        </button>
      </div>

      {/* Invoices List */}
      {loading ? (
        <div className="flex items-center justify-center p-12">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : invoices.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center max-w-lg mx-auto">
          <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <Receipt className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-slate-900">No invoices generated</h3>
          <p className="text-sm text-slate-500 mt-1">
            Create your first invoice to bill clients with itemized breakdowns and instant vector PDF downloads.
          </p>
          <button
            onClick={() => setShowModal(true)}
            className="mt-5 inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
          >
            <Plus className="w-4 h-4" />
            Create First Invoice
          </button>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200 text-xs uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-6">Invoice #</th>
                  <th className="py-3.5 px-6">Client</th>
                  <th className="py-3.5 px-6">Status</th>
                  <th className="py-3.5 px-6">Dates</th>
                  <th className="py-3.5 px-6 text-right">Total Due</th>
                  <th className="py-3.5 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {invoices.map((inv) => (
                  <tr key={inv.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-4 px-6 font-bold text-slate-900">
                      {inv.invoice_number}
                    </td>
                    <td className="py-4 px-6">
                      <div className="font-semibold text-slate-900">{inv.client_name || 'Client'}</div>
                      <div className="text-xs text-slate-400">{(inv.items || []).length} line item(s)</div>
                    </td>
                    <td className="py-4 px-6">
                      <select
                        value={inv.status}
                        onChange={(e) => handleStatusChange(inv.id, e.target.value)}
                        className={`text-xs font-semibold px-2.5 py-1 rounded-full border focus:outline-none cursor-pointer ${
                          STATUS_BADGES[inv.status] || STATUS_BADGES.draft
                        }`}
                      >
                        <option value="draft">Draft</option>
                        <option value="sent">Sent</option>
                        <option value="paid">Paid</option>
                        <option value="overdue">Overdue</option>
                      </select>
                    </td>
                    <td className="py-4 px-6 text-xs text-slate-500 space-y-0.5">
                      <div>Issued: {inv.issue_date}</div>
                      <div>Due: {inv.due_date}</div>
                    </td>
                    <td className="py-4 px-6 text-right font-bold text-slate-900">
                      ${inv.total_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-4 px-6 text-right space-x-2">
                      <button
                        onClick={() => handleDownloadPdf(inv)}
                        title="Download Vector PDF"
                        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-blue-600 hover:text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
                      >
                        <Download className="w-3.5 h-3.5" />
                        PDF
                      </button>
                      <button
                        onClick={() => handleDeleteInvoice(inv.id)}
                        title="Delete Invoice"
                        className="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create Invoice Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl border border-slate-100 overflow-hidden my-8">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <h3 className="font-bold text-slate-900 text-lg">Create New Tax Invoice</h3>
              <button onClick={() => setShowModal(false)} className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateInvoice} className="p-6 space-y-5">
              {error && (
                <div className="flex items-center gap-2 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-lg">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="sm:col-span-1">
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Client *</label>
                  <select
                    required
                    value={clientId}
                    onChange={(e) => setClientId(Number(e.target.value))}
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
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Issue Date</label>
                  <input
                    type="date"
                    required
                    value={issueDate}
                    onChange={(e) => setIssueDate(e.target.value)}
                    className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Due Date</label>
                  <input
                    type="date"
                    required
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>
              </div>

              {/* Line Items Section */}
              <div className="border border-slate-200 rounded-xl p-4 bg-slate-50/50 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">Line Items</span>
                  <button
                    type="button"
                    onClick={addItemRow}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700"
                  >
                    <Plus className="w-3.5 h-3.5" /> Add Row
                  </button>
                </div>

                {items.map((item, index) => (
                  <div key={index} className="grid grid-cols-12 gap-2 items-center bg-white p-2 rounded-lg border border-slate-200">
                    <div className="col-span-6">
                      <input
                        type="text"
                        required
                        placeholder="Description of deliverable..."
                        value={item.description}
                        onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                        className="w-full px-2 py-1 text-xs bg-transparent border-0 focus:outline-none focus:ring-0 text-slate-900"
                      />
                    </div>
                    <div className="col-span-2">
                      <input
                        type="number"
                        min="0.1"
                        step="0.5"
                        required
                        placeholder="Qty"
                        value={item.quantity}
                        onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                        className="w-full px-2 py-1 text-xs bg-slate-50 border border-slate-200 rounded text-center focus:outline-none"
                      />
                    </div>
                    <div className="col-span-2">
                      <input
                        type="number"
                        min="0"
                        step="10"
                        required
                        placeholder="Price"
                        value={item.unit_price}
                        onChange={(e) => handleItemChange(index, 'unit_price', e.target.value)}
                        className="w-full px-2 py-1 text-xs bg-slate-50 border border-slate-200 rounded text-right focus:outline-none"
                      />
                    </div>
                    <div className="col-span-1 text-right text-xs font-semibold text-slate-900">
                      ${item.total.toFixed(0)}
                    </div>
                    <div className="col-span-1 text-right">
                      {items.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeItemRow(index)}
                          className="text-slate-300 hover:text-rose-500"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  </div>
                ))}

                {/* Subtotal & Tax Controls */}
                <div className="pt-2 flex flex-col items-end gap-1.5 text-xs text-slate-600">
                  <div className="flex items-center gap-4">
                    <span>Subtotal:</span>
                    <span className="font-semibold text-slate-900">${subtotal.toFixed(2)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span>Tax Rate (%):</span>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={taxRatePct}
                      onChange={(e) => setTaxRatePct(Number(e.target.value))}
                      className="w-14 px-1.5 py-0.5 bg-white border border-slate-300 rounded text-center"
                    />
                    <span className="font-semibold text-slate-900">${taxAmount.toFixed(2)}</span>
                  </div>
                  <div className="flex items-center gap-4 text-sm font-bold text-slate-900 pt-1 border-t border-slate-200">
                    <span>Total Amount:</span>
                    <span className="text-blue-600">${totalAmount.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Notes & Payment Instructions</label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Wire transfer instructions, bank account details..."
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-600 resize-none"
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
                  disabled={submitting}
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm rounded-lg shadow-sm transition-colors disabled:opacity-50"
                >
                  {submitting ? 'Generating...' : 'Issue Invoice'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
