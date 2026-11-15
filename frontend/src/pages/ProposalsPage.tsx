import React from 'react';
import { Lightbulb } from 'lucide-react';

export const ProposalsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">AI Proposal Generator</h1>
        <p className="text-sm text-slate-500 mt-1">
          Scaffold project scopes, milestones, and task lists directly from client requirement briefs (Scheduled for Day 6).
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center max-w-md mx-auto">
        <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4">
          <Lightbulb className="w-6 h-6" />
        </div>
        <h3 className="text-base font-bold text-slate-900">Proposal Scaffolding Pipeline</h3>
        <p className="text-xs text-slate-500 mt-1">
          Converts unstructured client requirements into active project and task structures with one click.
        </p>
      </div>
    </div>
  );
};
