import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, ChevronLeft, ChevronRight, Phone, Filter, X } from 'lucide-react';
import { listCalls } from '../services/api';
import { Badge, LoadingSpinner, EmptyState } from '../components/common';
import type { CallRecord } from '../types';
import { clsx } from 'clsx';

const STATUS_OPTIONS = ['all', 'completed', 'processing', 'failed'];

export default function CallHistory() {
  const [calls, setCalls] = useState<CallRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [showFilters, setShowFilters] = useState(false);
  const navigate = useNavigate();
  const pageSize = 15;

  useEffect(() => {
    setLoading(true);
    listCalls(page, pageSize)
      .then((res) => { setCalls(res.calls); setTotal(res.total_count); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [page]);

  const filtered = calls.filter((c) => {
    const matchSearch = !search ||
      c.call_id.toLowerCase().includes(search.toLowerCase()) ||
      (c.file_name && c.file_name.toLowerCase().includes(search.toLowerCase()));
    const matchStatus = statusFilter === 'all' || c.status === statusFilter;
    const matchType = typeFilter === 'all' || c.input_type === typeFilter;
    return matchSearch && matchStatus && matchType;
  });

  const totalPages = Math.ceil(total / pageSize);
  const statusColor = (s: string) => s === 'completed' ? 'green' : s === 'failed' ? 'red' : 'yellow';
  const hasFilters = statusFilter !== 'all' || typeFilter !== 'all' || search !== '';

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-display font-bold gradient-text">Call History</h1>
          <p className="cs-muted mt-1">{total} total calls analyzed</p>
        </div>
        <button onClick={() => navigate('/upload')} className="btn-primary">New Analysis</button>
      </div>

      {/* Search + Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 cs-muted" />
          <input type="text" placeholder="Search by call ID or file name..." value={search}
            onChange={(e) => setSearch(e.target.value)} className="input-field pl-11 text-sm" />
        </div>
        <button onClick={() => setShowFilters(!showFilters)}
          className={clsx('btn-secondary flex items-center gap-2 text-sm', hasFilters && 'border-cyan-500/40 text-cyan-400')}>
          <Filter className="w-4 h-4" /> Filters {hasFilters && `(active)`}
        </button>
        {hasFilters && (
          <button onClick={() => { setSearch(''); setStatusFilter('all'); setTypeFilter('all'); }}
            className="text-xs cs-muted hover:text-rose-400 flex items-center gap-1">
            <X className="w-3 h-3" /> Clear
          </button>
        )}
      </div>

      {/* Filter Options */}
      {showFilters && (
        <div className="glass-card p-4 flex flex-wrap gap-4 animate-fade-in">
          <div>
            <label className="text-xs cs-muted mb-1 block">Status</label>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="input-field text-sm py-2">
              {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s === 'all' ? 'All Statuses' : s}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs cs-muted mb-1 block">Input Type</label>
            <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)} className="input-field text-sm py-2">
              <option value="all">All Types</option>
              <option value="audio">Audio</option>
              <option value="transcript">Transcript</option>
            </select>
          </div>
        </div>
      )}

      {/* Table */}
      {loading ? (
        <div className="flex items-center justify-center h-[40vh]"><LoadingSpinner text="Loading calls..." /></div>
      ) : filtered.length === 0 ? (
        <EmptyState icon={<Phone className="w-12 h-12" />} title="No calls found"
          description={hasFilters ? "Try adjusting your filters." : "Start by uploading an audio file or pasting a transcript."} />
      ) : (
        <div className="glass-card overflow-hidden">
          {/* Desktop table */}
          <div className="hidden md:block overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b" style={{ borderColor: 'var(--cs-border)' }}>
                  {['Call ID', 'Status', 'Type', 'File', 'Duration', 'Created', ''].map((h) => (
                    <th key={h} className="text-left px-5 py-3.5 text-[11px] font-semibold cs-muted uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map((call) => (
                  <tr key={call.call_id} onClick={() => navigate(`/analysis/${call.call_id}`)}
                    className="border-b cursor-pointer transition-colors cs-nav-hover" style={{ borderColor: 'var(--cs-border)' }}>
                    <td className="px-5 py-4"><span className="text-sm font-mono text-cyan-400">{call.call_id}</span></td>
                    <td className="px-5 py-4"><Badge color={statusColor(call.status)}>{call.status}</Badge></td>
                    <td className="px-5 py-4"><span className="text-xs cs-muted capitalize">{call.input_type}</span></td>
                    <td className="px-5 py-4"><span className="text-xs cs-muted truncate max-w-[150px] block">{call.file_name || '—'}</span></td>
                    <td className="px-5 py-4"><span className="text-xs cs-muted">{call.duration_seconds ? `${Math.round(call.duration_seconds)}s` : '—'}</span></td>
                    <td className="px-5 py-4"><span className="text-xs cs-muted">{new Date(call.created_at).toLocaleDateString()}</span></td>
                    <td className="px-5 py-4"><ChevronRight className="w-4 h-4 cs-muted" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile cards */}
          <div className="md:hidden divide-y" style={{ borderColor: 'var(--cs-border)' }}>
            {filtered.map((call) => (
              <button key={call.call_id} onClick={() => navigate(`/analysis/${call.call_id}`)}
                className="w-full p-4 text-left cs-nav-hover transition-colors">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-mono text-cyan-400">{call.call_id}</span>
                  <Badge color={statusColor(call.status)}>{call.status}</Badge>
                </div>
                <div className="flex items-center gap-3 text-xs cs-muted">
                  <span className="capitalize">{call.input_type}</span>
                  <span>{new Date(call.created_at).toLocaleDateString()}</span>
                  {call.duration_seconds && <span>{Math.round(call.duration_seconds)}s</span>}
                </div>
              </button>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-between px-5 py-4 border-t" style={{ borderColor: 'var(--cs-border)' }}>
              <span className="text-xs cs-muted">Page {page} of {totalPages}</span>
              <div className="flex gap-2">
                <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1}
                  className="p-1.5 rounded-lg cs-nav-hover disabled:opacity-30 disabled:cursor-not-allowed"><ChevronLeft className="w-4 h-4 cs-muted" /></button>
                <button onClick={() => setPage(Math.min(totalPages, page + 1))} disabled={page === totalPages}
                  className="p-1.5 rounded-lg cs-nav-hover disabled:opacity-30 disabled:cursor-not-allowed"><ChevronRight className="w-4 h-4 cs-muted" /></button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
