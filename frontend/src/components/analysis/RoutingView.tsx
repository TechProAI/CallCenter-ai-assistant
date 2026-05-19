import { Badge } from '../common';
import { ArrowUpRight, AlertTriangle, Tag, Building2 } from 'lucide-react';
import type { RoutingDecision } from '../../types';

const urgencyColors = { low: 'green', medium: 'yellow', high: 'orange', critical: 'red' };
const resolutionColors = { resolved: 'green', partially_resolved: 'yellow', unresolved: 'red', follow_up_required: 'orange', escalated: 'purple' };

export default function RoutingView({ data }: { data: RoutingDecision }) {
  return (
    <div className="space-y-6">
      {/* Top Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card p-5">
          <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">Category</p>
          <Badge color="blue">{data.category.replace(/_/g, ' ')}</Badge>
        </div>
        <div className="glass-card p-5">
          <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">Urgency</p>
          <Badge color={urgencyColors[data.urgency] || 'gray'}>{data.urgency}</Badge>
        </div>
        <div className="glass-card p-5">
          <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">Resolution</p>
          <Badge color={resolutionColors[data.resolution_status] || 'gray'}>{data.resolution_status.replace(/_/g, ' ')}</Badge>
        </div>
      </div>

      {/* Priority */}
      <div className="glass-card p-5 flex items-center justify-between">
        <span className="text-sm text-slate-400">Priority Score</span>
        <div className="flex items-center gap-2">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className={`w-3 h-6 rounded-sm ${i < data.priority_score ? (data.priority_score >= 8 ? 'bg-rose-500' : data.priority_score >= 5 ? 'bg-amber-500' : 'bg-emerald-500') : 'bg-slate-800'}`} />
          ))}
          <span className="text-sm font-bold text-white ml-2">{data.priority_score}/10</span>
        </div>
      </div>

      {/* Escalation */}
      {data.requires_escalation && (
        <div className="bg-rose-500/10 border border-rose-500/20 rounded-xl p-5 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-rose-300 mb-1">Escalation Required</p>
            <p className="text-sm text-rose-200/80">{data.escalation_reason}</p>
          </div>
        </div>
      )}

      {/* Department */}
      {data.recommended_department && (
        <div className="glass-card p-5 flex items-center gap-3">
          <Building2 className="w-5 h-5 text-violet-400" />
          <div>
            <p className="text-xs text-slate-500">Recommended Department</p>
            <p className="text-sm font-semibold text-violet-300">{data.recommended_department}</p>
          </div>
        </div>
      )}

      {/* Tags */}
      {data.tags.length > 0 && (
        <div className="glass-card p-5">
          <p className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
            <Tag className="w-4 h-4 text-slate-400" /> Tags
          </p>
          <div className="flex flex-wrap gap-2">
            {data.tags.map((tag, i) => (
              <span key={i} className="px-3 py-1 bg-slate-800 text-slate-300 rounded-lg text-xs border border-slate-700/60">{tag}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
