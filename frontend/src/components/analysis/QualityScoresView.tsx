import { ScoreCircle, ProgressBar, Badge } from '../common';
import { ThumbsUp, AlertCircle, ChevronDown } from 'lucide-react';
import { useState } from 'react';
import type { QualityScores, ScoreBreakdown } from '../../types';
import { clsx } from 'clsx';

function ScoreCard({ label, data }: { label: string; data: ScoreBreakdown }) {
  const [open, setOpen] = useState(false);
  const color = data.score >= 8 ? 'emerald' : data.score >= 6 ? 'cyan' : data.score >= 4 ? 'amber' : 'rose';

  return (
    <div className="glass-card p-4">
      <button onClick={() => setOpen(!open)} className="w-full text-left">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-semibold text-slate-200">{label}</span>
          <div className="flex items-center gap-2">
            <span className={`text-lg font-bold font-display text-${color}-400`}>{data.score.toFixed(1)}</span>
            <ChevronDown className={clsx('w-4 h-4 text-slate-500 transition-transform', open && 'rotate-180')} />
          </div>
        </div>
        <ProgressBar value={data.score} />
      </button>

      {open && (
        <div className="mt-4 space-y-3 animate-fade-in">
          <p className="text-xs text-slate-400 leading-relaxed">{data.justification}</p>
          {data.highlights.length > 0 && (
            <div>
              <p className="text-[10px] uppercase tracking-wider text-emerald-400 font-semibold mb-1.5 flex items-center gap-1">
                <ThumbsUp className="w-3 h-3" /> Highlights
              </p>
              {data.highlights.map((h, i) => (
                <p key={i} className="text-xs text-slate-300 ml-4 mb-1">• {h}</p>
              ))}
            </div>
          )}
          {data.improvements.length > 0 && (
            <div>
              <p className="text-[10px] uppercase tracking-wider text-amber-400 font-semibold mb-1.5 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" /> Improve
              </p>
              {data.improvements.map((im, i) => (
                <p key={i} className="text-xs text-slate-300 ml-4 mb-1">• {im}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function QualityScoresView({ data }: { data: QualityScores }) {
  const gradeColor = data.grade === 'A' ? 'emerald' : data.grade === 'B' ? 'cyan' : data.grade === 'C' ? 'amber' : 'rose';

  const scoreItems: { label: string; key: keyof QualityScores }[] = [
    { label: 'Empathy', key: 'empathy_score' },
    { label: 'Professionalism', key: 'professionalism_score' },
    { label: 'Resolution', key: 'resolution_score' },
    { label: 'Communication', key: 'communication_score' },
    { label: 'Compliance', key: 'compliance_score' },
    { label: 'Active Listening', key: 'active_listening_score' },
  ];

  return (
    <div className="space-y-6">
      {/* Overall Score Header */}
      <div className="glass-card p-6 flex items-center gap-8">
        <ScoreCircle score={data.overall_score} size={100} grade={data.grade} />
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-xl font-display font-bold text-white">Overall Quality</h3>
            <Badge color={gradeColor}>Grade {data.grade}</Badge>
          </div>
          <p className="text-sm text-slate-300 leading-relaxed">{data.overall_feedback}</p>
        </div>
      </div>

      {/* Individual Scores Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {scoreItems.map(({ label, key }) => (
          <ScoreCard key={key} label={label} data={data[key] as ScoreBreakdown} />
        ))}
      </div>
    </div>
  );
}
