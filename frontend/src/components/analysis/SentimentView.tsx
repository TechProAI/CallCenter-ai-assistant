import { Badge } from '../common';
import { TrendingUp, TrendingDown, Minus, Zap } from 'lucide-react';
import type { SentimentAnalysis, SentimentLabel } from '../../types';

const sentimentConfig: Record<SentimentLabel, { color: string; label: string; emoji: string }> = {
  very_positive: { color: 'green', label: 'Very Positive', emoji: '😊' },
  positive: { color: 'green', label: 'Positive', emoji: '🙂' },
  neutral: { color: 'gray', label: 'Neutral', emoji: '😐' },
  negative: { color: 'red', label: 'Negative', emoji: '😟' },
  very_negative: { color: 'red', label: 'Very Negative', emoji: '😠' },
};

const trajectoryConfig: Record<string, { icon: React.ElementType; color: string; label: string }> = {
  improved: { icon: TrendingUp, color: 'text-emerald-400', label: 'Improved' },
  declined: { icon: TrendingDown, color: 'text-rose-400', label: 'Declined' },
  stable: { icon: Minus, color: 'text-slate-400', label: 'Stable' },
  mixed: { icon: Zap, color: 'text-amber-400', label: 'Mixed' },
};

export default function SentimentView({ data }: { data: SentimentAnalysis }) {
  const overall = sentimentConfig[data.overall_sentiment] || sentimentConfig.neutral;
  const customer = sentimentConfig[data.customer_sentiment] || sentimentConfig.neutral;
  const agent = sentimentConfig[data.agent_sentiment] || sentimentConfig.neutral;
  const traj = trajectoryConfig[data.sentiment_trajectory] || trajectoryConfig.stable;
  const TrajIcon = traj.icon;

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-card p-5 text-center">
          <p className="text-xs text-slate-500 mb-2 uppercase tracking-wider">Overall</p>
          <span className="text-3xl mb-1 block">{overall.emoji}</span>
          <Badge color={overall.color}>{overall.label}</Badge>
          <p className="text-xs text-slate-500 mt-2">Confidence: {Math.round(data.overall_confidence * 100)}%</p>
        </div>
        <div className="glass-card p-5 text-center">
          <p className="text-xs text-slate-500 mb-2 uppercase tracking-wider">Customer</p>
          <span className="text-3xl mb-1 block">{customer.emoji}</span>
          <Badge color={customer.color}>{customer.label}</Badge>
        </div>
        <div className="glass-card p-5 text-center">
          <p className="text-xs text-slate-500 mb-2 uppercase tracking-wider">Agent</p>
          <span className="text-3xl mb-1 block">{agent.emoji}</span>
          <Badge color={agent.color}>{agent.label}</Badge>
        </div>
        <div className="glass-card p-5 text-center">
          <p className="text-xs text-slate-500 mb-2 uppercase tracking-wider">Trajectory</p>
          <TrajIcon className={`w-8 h-8 mx-auto mb-1 ${traj.color}`} />
          <Badge color={traj.color === 'text-emerald-400' ? 'green' : traj.color === 'text-rose-400' ? 'red' : 'gray'}>{traj.label}</Badge>
        </div>
      </div>

      {/* Phase Timeline */}
      {data.phases.length > 0 && (
        <div className="glass-card p-6">
          <h4 className="text-sm font-semibold text-slate-200 mb-4">Sentiment Timeline</h4>
          <div className="relative">
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-800" />
            <div className="space-y-6">
              {data.phases.map((phase, i) => {
                const cfg = sentimentConfig[phase.sentiment] || sentimentConfig.neutral;
                return (
                  <div key={i} className="relative pl-10">
                    <div className="absolute left-2 top-1 w-5 h-5 rounded-full bg-slate-900 border-2 border-slate-700 flex items-center justify-center">
                      <span className="text-[10px]">{cfg.emoji}</span>
                    </div>
                    <div className="glass-card p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-semibold text-white capitalize">{phase.phase.replace(/_/g, ' ')}</span>
                        <Badge color={cfg.color}>{cfg.label}</Badge>
                      </div>
                      {phase.key_phrases.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-2">
                          {phase.key_phrases.map((p, j) => (
                            <span key={j} className="text-[11px] px-2 py-0.5 bg-slate-800/80 text-slate-300 rounded-md italic">"{p}"</span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Emotional Triggers */}
      {data.emotional_triggers.length > 0 && (
        <div className="glass-card p-5">
          <h4 className="text-sm font-semibold text-amber-400 mb-3 flex items-center gap-2">
            <Zap className="w-4 h-4" /> Emotional Triggers
          </h4>
          <div className="space-y-2">
            {data.emotional_triggers.map((trigger, i) => (
              <div key={i} className="flex items-start gap-2 text-sm text-slate-300">
                <span className="text-amber-500 mt-1 text-xs">⚡</span>
                {trigger}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
