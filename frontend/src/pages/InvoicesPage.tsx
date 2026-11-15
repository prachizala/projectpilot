import React from 'react';
import { Receipt } from 'lucide-react';

export const InvoicesPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Invoices & Billing</h1>
        <p className="text-sm text-slate-500 mt-1">
          Automated line item totals, tax calculations, and vector PDF downloads (Scheduled for Day 5).
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center max-w-md mx-auto">
        <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4">
          <Receipt className="w-6 h-6" />
        </div>
        <h3 className="text-base font-bold text-slate-900">Invoicing Engine Queued</h3>
        <p className="text-xs text-slate-500 mt-1">
          Complete with print-ready PyMuPDF vector generation and payment status tracking.
        </p>
      </div>
    </div>
  );
};
