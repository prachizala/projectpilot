import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { Project, Task, TaskStatus, TaskPriority } from '../types';
import { 
  Trello, 
  Plus, 
  Trash2, 
  Calendar, 
  AlertCircle, 
  X, 
  GripVertical
} from 'lucide-react';

interface ColumnConfig {
  id: TaskStatus;
  title: string;
  accent: string;
  badge: string;
}

const COLUMNS: ColumnConfig[] = [
  { id: 'todo', title: 'To Do', accent: 'border-slate-300', badge: 'bg-slate-100 text-slate-700' },
  { id: 'in_progress', title: 'In Progress', accent: 'border-blue-400', badge: 'bg-blue-50 text-blue-700' },
  { id: 'review', title: 'In Review', accent: 'border-amber-400', badge: 'bg-amber-50 text-amber-700' },
  { id: 'done', title: 'Done', accent: 'border-emerald-400', badge: 'bg-emerald-50 text-emerald-700' },
];

const PRIORITY_BADGES: Record<TaskPriority, string> = {
  high: 'bg-rose-50 text-rose-600 border-rose-200',
  medium: 'bg-amber-50 text-amber-600 border-amber-200',
  low: 'bg-slate-50 text-slate-500 border-slate-200',
};

export const KanbanPage: React.FC = () => {
  const { id: paramProjectId } = useParams<{ id?: string }>();
  const navigate = useNavigate();

  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(
    paramProjectId ? parseInt(paramProjectId, 10) : null
  );
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Drag and Drop State
  const [draggedTaskId, setDraggedTaskId] = useState<number | null>(null);

  // Add Task Modal State
  const [showModal, setShowModal] = useState(false);
  const [targetColumn, setTargetColumn] = useState<TaskStatus>('todo');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<TaskPriority>('medium');
  const [dueDate, setDueDate] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // 1. Fetch available projects
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const data = await api.getProjects();
        setProjects(data);
        if (!selectedProjectId && data.length > 0) {
          setSelectedProjectId(data[0].id);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to fetch projects');
      }
    };
    fetchProjects();
  }, []);

  // 2. Fetch tasks for selected project
  const fetchTasks = async (projId: number) => {
    try {
      setLoading(true);
      const data = await api.getProjectTasks(projId);
      setTasks(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load project tasks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedProjectId) {
      fetchTasks(selectedProjectId);
    }
  }, [selectedProjectId]);

  const handleProjectSelect = (projId: number) => {
    setSelectedProjectId(projId);
    navigate(`/projects/${projId}/kanban`);
  };

  // Drag Handlers
  const handleDragStart = (e: React.DragEvent, taskId: number) => {
    setDraggedTaskId(taskId);
    e.dataTransfer.setData('text/plain', taskId.toString());
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = async (e: React.DragEvent, targetStatus: TaskStatus) => {
    e.preventDefault();
    if (!draggedTaskId) return;

    const taskToMove = tasks.find((t) => t.id === draggedTaskId);
    if (!taskToMove || taskToMove.status === targetStatus) {
      setDraggedTaskId(null);
      return;
    }

    // Determine new position: append to bottom of target column
    const targetColumnTasks = tasks.filter((t) => t.status === targetStatus);
    const newPosition = targetColumnTasks.length;

    // Optimistic UI Update
    const previousTasks = [...tasks];
    setTasks((current) =>
      current.map((t) =>
        t.id === draggedTaskId ? { ...t, status: targetStatus, position: newPosition } : t
      )
    );

    try {
      await api.updateTaskPosition(draggedTaskId, {
        status: targetStatus,
        position: newPosition,
      });
      if (selectedProjectId) {
        fetchTasks(selectedProjectId);
      }
    } catch {
      // Rollback on network failure
      setTasks(previousTasks);
      alert('Could not update task position. Network rollback applied.');
    } finally {
      setDraggedTaskId(null);
    }
  };

  // Create Task Handler
  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProjectId) return;

    setSubmitting(true);
    setError(null);

    try {
      await api.createTask(selectedProjectId, {
        title,
        description,
        status: targetColumn,
        priority,
        due_date: dueDate || null,
      });

      setShowModal(false);
      setTitle('');
      setDescription('');
      setPriority('medium');
      setDueDate('');
      fetchTasks(selectedProjectId);
    } catch (err: any) {
      setError(err.message || 'Failed to create task');
    } finally {
      setSubmitting(false);
    }
  };

  // Delete Task Handler
  const handleDeleteTask = async (taskId: number) => {
    if (!window.confirm('Delete this task?')) return;
    try {
      await api.deleteTask(taskId);
      if (selectedProjectId) fetchTasks(selectedProjectId);
    } catch (err: any) {
      alert(err.message || 'Failed to delete task');
    }
  };

  const activeProject = projects.find((p) => p.id === selectedProjectId);

  return (
    <div className="space-y-6">
      {/* Header and Project Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Kanban Task Board</h1>
            {activeProject && (
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                {activeProject.client_name}
              </span>
            )}
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Drag and drop tasks between workflow stages with instant position synchronization
          </p>
        </div>

        {/* Project Selector & Add Task */}
        <div className="flex items-center gap-3">
          <select
            value={selectedProjectId || ''}
            onChange={(e) => handleProjectSelect(Number(e.target.value))}
            className="px-3.5 py-2 bg-white border border-slate-200 rounded-xl text-sm font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600 shadow-sm"
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                📁 {p.title}
              </option>
            ))}
          </select>

          <button
            onClick={() => {
              setTargetColumn('todo');
              setShowModal(true);
            }}
            disabled={!selectedProjectId}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-medium shadow-sm transition-colors disabled:opacity-50"
          >
            <Plus className="w-4 h-4" />
            Add Task
          </button>
        </div>
      </div>

      {/* Kanban Columns Canvas */}
      {loading ? (
        <div className="flex items-center justify-center p-16">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : !selectedProjectId ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center max-w-md mx-auto">
          <Trello className="w-8 h-8 text-blue-600 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-900">No project selected</h3>
          <p className="text-xs text-slate-500 mt-1">Create or select a project to open its Kanban board.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 items-start">
          {COLUMNS.map((col) => {
            const columnTasks = tasks
              .filter((t) => t.status === col.id)
              .sort((a, b) => a.position - b.position);

            return (
              <div
                key={col.id}
                onDragOver={handleDragOver}
                onDrop={(e) => handleDrop(e, col.id)}
                className={`bg-slate-100/70 border-t-4 ${col.accent} rounded-2xl p-4 flex flex-col min-h-[550px] shadow-sm`}
              >
                {/* Column Header */}
                <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-200">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-slate-900">{col.title}</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${col.badge}`}>
                      {columnTasks.length}
                    </span>
                  </div>
                  <button
                    onClick={() => {
                      setTargetColumn(col.id);
                      setShowModal(true);
                    }}
                    title={`Add task to ${col.title}`}
                    className="p-1 text-slate-400 hover:text-blue-600 hover:bg-slate-200/60 rounded-md transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>

                {/* Cards Container */}
                <div className="space-y-3 flex-1">
                  {columnTasks.length === 0 ? (
                    <div className="h-32 border-2 border-dashed border-slate-200 rounded-xl flex items-center justify-center text-xs text-slate-400">
                      Drop tasks here
                    </div>
                  ) : (
                    columnTasks.map((task) => (
                      <div
                        key={task.id}
                        draggable
                        onDragStart={(e) => handleDragStart(e, task.id)}
                        className={`bg-white border border-slate-200 rounded-xl p-3.5 shadow-sm hover:shadow transition-all cursor-grab active:cursor-grabbing ${
                          draggedTaskId === task.id ? 'opacity-40 ring-2 ring-blue-500' : ''
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-center gap-1.5">
                            <GripVertical className="w-3.5 h-3.5 text-slate-300" />
                            <span
                              className={`text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded border ${
                                PRIORITY_BADGES[task.priority]
                              }`}
                            >
                              {task.priority}
                            </span>
                          </div>
                          <button
                            onClick={() => handleDeleteTask(task.id)}
                            title="Delete Task"
                            className="text-slate-300 hover:text-rose-500 transition-colors"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>

                        <h4 className="text-sm font-semibold text-slate-900 mt-2 leading-snug">
                          {task.title}
                        </h4>

                        {task.description && (
                          <p className="text-xs text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                            {task.description}
                          </p>
                        )}

                        {task.due_date && (
                          <div className="flex items-center gap-1 text-[11px] text-slate-400 mt-3 pt-2 border-t border-slate-100">
                            <Calendar className="w-3 h-3" />
                            <span>Due: {task.due_date}</span>
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Add Task Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md border border-slate-100 overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <h3 className="font-bold text-slate-900 text-lg">Add New Task</h3>
              <button onClick={() => setShowModal(false)} className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateTask} className="p-6 space-y-4">
              {error && (
                <div className="flex items-center gap-2 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-lg">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Task Title *</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Design Landing Page Wireframes"
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Target Column</label>
                  <select
                    value={targetColumn}
                    onChange={(e) => setTargetColumn(e.target.value as TaskStatus)}
                    className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-600"
                  >
                    <option value="todo">To Do</option>
                    <option value="in_progress">In Progress</option>
                    <option value="review">In Review</option>
                    <option value="done">Done</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Priority</label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value as TaskPriority)}
                    className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-600"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Due Date</label>
                <input
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Description</label>
                <textarea
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Acceptance criteria, asset links, technical specs..."
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
                  {submitting ? 'Creating...' : 'Create Task'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
