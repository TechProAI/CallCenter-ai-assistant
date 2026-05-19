import { Star, Target, BookOpen, MessageCircle } from 'lucide-react';
import type { CoachingRecommendation } from '../../types';

export default function CoachingView({ data }: { data: CoachingRecommendation }) {
  return (
    <div className="space-y-6">
      {/* Overall */}
      <div className="glass-card p-6 border-l-4 border-cyan-500">
        <p className="text-sm text-slate-200 leading-relaxed">{data.overall_recommendation}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Strengths */}
        <div className="glass-card p-5">
          <h4 className="text-sm font-semibold text-emerald-400 mb-4 flex items-center gap-2">
            <Star className="w-4 h-4" /> Strengths
          </h4>
          <div className="space-y-2.5">
            {data.strengths.map((s, i) => (
              <div key={i} className="flex items-start gap-2.5 bg-emerald-500/5 rounded-lg p-3 border border-emerald-500/10">
                <span className="text-emerald-400 text-xs mt-0.5">✓</span>
                <span className="text-sm text-slate-200">{s}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Areas for Improvement */}
        <div className="glass-card p-5">
          <h4 className="text-sm font-semibold text-amber-400 mb-4 flex items-center gap-2">
            <Target className="w-4 h-4" /> Areas for Improvement
          </h4>
          <div className="space-y-2.5">
            {data.areas_for_improvement.map((a, i) => (
              <div key={i} className="flex items-start gap-2.5 bg-amber-500/5 rounded-lg p-3 border border-amber-500/10">
                <span className="text-amber-400 text-xs mt-0.5">→</span>
                <span className="text-sm text-slate-200">{a}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Training Suggestions */}
      {data.training_suggestions.length > 0 && (
        <div className="glass-card p-5">
          <h4 className="text-sm font-semibold text-violet-400 mb-4 flex items-center gap-2">
            <BookOpen className="w-4 h-4" /> Training Suggestions
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {data.training_suggestions.map((t, i) => (
              <div key={i} className="flex items-center gap-3 bg-violet-500/5 rounded-lg p-3 border border-violet-500/10">
                <span className="w-6 h-6 rounded-full bg-violet-500/20 text-violet-400 flex items-center justify-center text-[10px] font-bold flex-shrink-0">{i + 1}</span>
                <span className="text-sm text-slate-200">{t}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Example Responses */}
      {data.example_responses.length > 0 && (
        <div className="glass-card p-5">
          <h4 className="text-sm font-semibold text-cyan-400 mb-4 flex items-center gap-2">
            <MessageCircle className="w-4 h-4" /> Better Response Examples
          </h4>
          <div className="space-y-3">
            {data.example_responses.map((r, i) => (
              <div key={i} className="bg-cyan-500/5 border border-cyan-500/10 rounded-lg p-4">
                <p className="text-sm text-slate-200 italic leading-relaxed">"{r}"</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
