import React from 'react';
import { Trello } from 'lucide-react';

export const KanbanPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Interactive Kanban Board</h1>
          <p className="text-sm text-slate-500 mt-1">
            Drag-and-drop task execution with persistent database rank ordering (Scheduled for Day 4).
          </p>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center max-w-md mx-auto">
        <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4">
          <Trello className="w-6 h-6" />
        </div>
        <h3 className="text-base font-bold text-slate-900">Kanban Board Ready for Day 4</h3>
        <p className="text-xs text-slate-500 mt-1">
          Select any active project from the Projects page to view its task progression columns.
        </p>
      </div>
    </div>
  );
};
