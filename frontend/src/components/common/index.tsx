import { clsx } from 'clsx';

// ── Badge ──

const badgeColors: Record<string, string> = {
  green: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/20',
  red: 'bg-rose-500/15 text-rose-400 border-rose-500/20',
  yellow: 'bg-amber-500/15 text-amber-400 border-amber-500/20',
  blue: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/20',
  purple: 'bg-violet-500/15 text-violet-400 border-violet-500/20',
  gray: 'bg-slate-500/15 text-slate-400 border-slate-500/20',
  orange: 'bg-orange-500/15 text-orange-400 border-orange-500/20',
};

export function Badge({ children, color = 'gray', className }: { children: React.ReactNode; color?: string; className?: string }) {
  return (
    <span className={clsx('inline-flex items-center px-2.5 py-0.5 rounded-lg text-xs font-medium border', badgeColors[color] || badgeColors.gray, className)}>
      {children}
    </span>
  );
}

// ── Score Circle ──

export function ScoreCircle({ score, size = 80, label, grade }: { score: number; size?: number; label?: string; grade?: string }) {
  const radius = (size - 8) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 10) * circumference;
  const color = score >= 8 ? '#10b981' : score >= 6 ? '#06b6d4' : score >= 4 ? '#f59e0b' : '#ef4444';

  return (
    <div className="flex flex-col items-center gap-1.5">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="rgba(51,65,85,0.5)" strokeWidth="4" />
          <circle
            cx={size / 2} cy={size / 2} r={radius} fill="none" stroke={color} strokeWidth="4"
            strokeDasharray={circumference} strokeDashoffset={circumference - progress}
            strokeLinecap="round" className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-lg font-bold font-display" style={{ color }}>{score.toFixed(1)}</span>
          {grade && <span className="text-[10px] text-slate-400 font-medium">{grade}</span>}
        </div>
      </div>
      {label && <span className="text-xs text-slate-400 text-center">{label}</span>}
    </div>
  );
}

// ── Loading Spinner ──

export function LoadingSpinner({ size = 'md', text }: { size?: 'sm' | 'md' | 'lg'; text?: string }) {
  const sizeClasses = { sm: 'w-5 h-5', md: 'w-8 h-8', lg: 'w-12 h-12' };
  return (
    <div className="flex flex-col items-center gap-3">
      <div className={clsx('border-2 border-slate-700 border-t-cyan-400 rounded-full animate-spin', sizeClasses[size])} />
      {text && <p className="text-sm text-slate-400 animate-pulse">{text}</p>}
    </div>
  );
}

// ── Progress Bar ──

export function ProgressBar({ value, max = 10, color }: { value: number; max?: number; color?: string }) {
  const pct = Math.min((value / max) * 100, 100);
  const barColor = color || (pct >= 80 ? 'bg-emerald-500' : pct >= 60 ? 'bg-cyan-500' : pct >= 40 ? 'bg-amber-500' : 'bg-rose-500');

  return (
    <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
      <div className={clsx('h-full rounded-full transition-all duration-700 ease-out', barColor)} style={{ width: `${pct}%` }} />
    </div>
  );
}

// ── Empty State ──

export function EmptyState({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="text-slate-600 mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-slate-300 mb-2">{title}</h3>
      <p className="text-sm text-slate-500 text-center max-w-sm">{description}</p>
    </div>
  );
}
