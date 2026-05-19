import { CheckCircle2, Circle, Loader2, XCircle } from 'lucide-react';
import { clsx } from 'clsx';
import type { CallStatus } from '../../types';

const steps = [
  { key: 'processing', label: 'Intake' },
  { key: 'transcribing', label: 'Transcribing' },
  { key: 'summarizing', label: 'Summarizing' },
  { key: 'scoring', label: 'Quality Scoring' },
  { key: 'analyzing', label: 'Sentiment & Routing' },
  { key: 'completed', label: 'Complete' },
];

const statusOrder = ['pending', 'processing', 'transcribing', 'summarizing', 'scoring', 'analyzing', 'completed'];

export default function ProgressTracker({ status, progress }: { status: CallStatus; progress: number | null }) {
  const currentIdx = statusOrder.indexOf(status);
  const isFailed = status === 'failed';

  return (
    <div className="glass-card p-8">
      <div className="flex items-center justify-between mb-8">
        <h3 className="text-lg font-display font-semibold text-white">Analysis Progress</h3>
        <span className="text-sm font-mono text-cyan-400">{progress ?? 0}%</span>
      </div>

      <div className="flex items-center justify-between">
        {steps.map((step, i) => {
          const stepIdx = statusOrder.indexOf(step.key);
          const isCompleted = currentIdx > stepIdx;
          const isCurrent = currentIdx === stepIdx;
          const isPending = currentIdx < stepIdx;

          return (
            <div key={step.key} className="flex items-center flex-1 last:flex-none">
              <div className="flex flex-col items-center gap-2">
                <div className={clsx(
                  'w-10 h-10 rounded-full flex items-center justify-center transition-all duration-500',
                  isCompleted && 'bg-emerald-500/20 border-2 border-emerald-500',
                  isCurrent && !isFailed && 'bg-cyan-500/20 border-2 border-cyan-400',
                  isCurrent && isFailed && 'bg-rose-500/20 border-2 border-rose-500',
                  isPending && 'bg-slate-800 border-2 border-slate-700',
                )}>
                  {isCompleted && <CheckCircle2 className="w-5 h-5 text-emerald-400" />}
                  {isCurrent && !isFailed && <Loader2 className="w-5 h-5 text-cyan-400 animate-spin" />}
                  {isCurrent && isFailed && <XCircle className="w-5 h-5 text-rose-400" />}
                  {isPending && <Circle className="w-4 h-4 text-slate-600" />}
                </div>
                <span className={clsx(
                  'text-[11px] font-medium whitespace-nowrap',
                  isCompleted && 'text-emerald-400',
                  isCurrent && 'text-cyan-400',
                  isPending && 'text-slate-600',
                )}>{step.label}</span>
              </div>
              {i < steps.length - 1 && (
                <div className={clsx(
                  'flex-1 h-0.5 mx-2 rounded-full transition-all duration-500',
                  isCompleted ? 'bg-emerald-500/50' : 'bg-slate-800',
                )} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
