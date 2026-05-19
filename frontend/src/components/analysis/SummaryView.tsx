import { FileText, Target, AlertTriangle, CheckSquare, ArrowRightCircle } from 'lucide-react';
import { Badge } from '../common';
import type { Summary } from '../../types';

export default function SummaryView({ data }: { data: Summary }) {
  return (
    <div className="space-y-6">
      {/* Brief Summary */}
      <div className="glass-card p-5">
        <h4 className="text-sm font-semibold text-cyan-400 mb-2 flex items-center gap-2">
          <FileText className="w-4 h-4" /> Overview
        </h4>
        <p className="text-slate-200 leading-relaxed">{data.brief_summary}</p>
      </div>

      {/* Customer Intent */}
      <div className="glass-card p-5">
        <h4 className="text-sm font-semibold text-violet-400 mb-2 flex items-center gap-2">
          <Target className="w-4 h-4" /> Customer Intent
        </h4>
        <p className="text-slate-200">{data.customer_intent}</p>
      </div>

      {/* Grid: Key Points + Issues */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Key Points */}
        <div className="glass-card p-5">
          <h4 className="text-sm font-semibold text-emerald-400 mb-3 flex items-center gap-2">
            <CheckSquare className="w-4 h-4" /> Key Points
          </h4>
          <ul className="space-y-2">
            {data.key_points.map((point, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                <span className="text-emerald-500 mt-1 text-xs">●</span>
                {point}
              </li>
            ))}
          </ul>
        </div>

        {/* Issues Raised */}
        <div className="glass-card p-5">
          <h4 className="text-sm font-semibold text-amber-400 mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" /> Issues Raised
          </h4>
          <ul className="space-y-2">
            {data.issues_raised.length > 0 ? data.issues_raised.map((issue, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                <span className="text-amber-500 mt-1 text-xs">●</span>
                {issue}
              </li>
            )) : (
              <li className="text-sm text-slate-500 italic">No issues raised</li>
            )}
          </ul>
        </div>
      </div>

      {/* Resolution */}
      <div className="glass-card p-5">
        <h4 className="text-sm font-semibold text-blue-400 mb-2">Resolution Provided</h4>
        <p className="text-slate-200 text-sm leading-relaxed">{data.resolution_provided}</p>
      </div>

      {/* Action Items */}
      {data.action_items.length > 0 && (
        <div className="glass-card p-5">
          <h4 className="text-sm font-semibold text-orange-400 mb-3 flex items-center gap-2">
            <ArrowRightCircle className="w-4 h-4" /> Action Items
          </h4>
          <div className="space-y-2">
            {data.action_items.map((item, i) => (
              <div key={i} className="flex items-start gap-3 bg-slate-800/50 rounded-lg p-3">
                <span className="w-5 h-5 rounded-full bg-orange-500/20 text-orange-400 flex items-center justify-center text-[10px] font-bold flex-shrink-0 mt-0.5">{i + 1}</span>
                <span className="text-sm text-slate-200">{item}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Follow-up */}
      {data.follow_up_needed && (
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 flex items-start gap-3">
          <Badge color="yellow">Follow-up Required</Badge>
          <p className="text-sm text-amber-200">{data.follow_up_details || 'Follow-up action needed.'}</p>
        </div>
      )}

      {/* Detailed Summary */}
      <details className="glass-card">
        <summary className="px-5 py-4 cursor-pointer text-sm font-semibold text-slate-300 hover:text-white transition-colors">
          View Detailed Summary
        </summary>
        <div className="px-5 pb-5">
          <p className="text-sm text-slate-300 leading-relaxed">{data.detailed_summary}</p>
        </div>
      </details>
    </div>
  );
}
