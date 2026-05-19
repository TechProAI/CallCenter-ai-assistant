import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Phone, BarChart3, CheckCircle, Activity, ArrowRight, TrendingUp } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { getDashboardStats } from '../services/api';
import { Badge, LoadingSpinner } from '../components/common';
import type { DashboardStats, CallRecord } from '../types';

const SENTIMENT_COLORS: Record<string, string> = {
  very_positive: '#10b981', positive: '#34d399', neutral: '#94a3b8',
  negative: '#f87171', very_negative: '#ef4444',
};
const CATEGORY_COLORS = ['#06b6d4', '#8b5cf6', '#f59e0b', '#ef4444', '#10b981', '#3b82f6', '#ec4899', '#f97316', '#6366f1', '#64748b'];
const URGENCY_COLORS: Record<string, string> = { low: '#10b981', medium: '#f59e0b', high: '#f97316', critical: '#ef4444' };

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => { getDashboardStats().then(setStats).catch(console.error).finally(() => setLoading(false)); }, []);

  if (loading) return <div className="flex items-center justify-center h-[60vh]"><LoadingSpinner size="lg" text="Loading dashboard..." /></div>;

  const sentimentData = Object.entries(stats?.sentiment_distribution || {}).map(([key, val]) => ({ name: key.replace(/_/g, ' '), value: val, fill: SENTIMENT_COLORS[key] || '#64748b' }));
  const categoryData = Object.entries(stats?.category_distribution || {}).map(([key, val], i) => ({ name: key.replace(/_/g, ' '), value: val, fill: CATEGORY_COLORS[i % CATEGORY_COLORS.length] }));
  const urgencyData = Object.entries(stats?.urgency_distribution || {}).map(([key, val]) => ({ name: key, value: val, fill: URGENCY_COLORS[key] || '#64748b' }));

  const renderPieChart = (data: any[], title: string) => (
    <div className="glass-card p-6">
      <h3 className="text-sm font-semibold cs-text mb-4">{title}</h3>
      {data.length > 0 ? (
        <div className="flex flex-col sm:flex-row items-center gap-6">
          <ResponsiveContainer width={160} height={160}>
            <PieChart><Pie data={data} cx="50%" cy="50%" innerRadius={45} outerRadius={70} dataKey="value" paddingAngle={3} strokeWidth={0}>
              {data.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
            </Pie><Tooltip contentStyle={{ background: 'var(--cs-card-solid)', border: '1px solid var(--cs-border)', borderRadius: '8px', fontSize: '12px', color: 'var(--cs-text)' }} /></PieChart>
          </ResponsiveContainer>
          <div className="space-y-2">
            {data.map((item, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: item.fill }} />
                <span className="cs-muted capitalize">{item.name}</span>
                <span className="cs-text font-medium ml-auto">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      ) : <p className="text-sm cs-muted text-center py-8">No data yet</p>}
    </div>
  );

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-display font-bold gradient-text">Dashboard</h1>
        <p className="cs-muted mt-1">Call center intelligence at a glance</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
        {[
          { label: 'Total Calls', value: stats?.total_calls ?? 0, icon: Phone, color: 'from-cyan-500 to-blue-600', textColor: 'text-cyan-400' },
          { label: 'Avg Quality', value: stats?.avg_quality_score ? `${stats.avg_quality_score.toFixed(1)}/10` : 'N/A', icon: BarChart3, color: 'from-violet-500 to-purple-600', textColor: 'text-violet-400' },
          { label: 'Resolution Rate', value: stats?.avg_resolution_rate ? `${stats.avg_resolution_rate}%` : 'N/A', icon: CheckCircle, color: 'from-emerald-500 to-green-600', textColor: 'text-emerald-400' },
          { label: 'Categories', value: Object.keys(stats?.category_distribution || {}).length, icon: Activity, color: 'from-amber-500 to-orange-600', textColor: 'text-amber-400' },
        ].map((stat, i) => (
          <div key={i} className="glass-card-hover p-4 sm:p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-[10px] sm:text-xs cs-muted uppercase tracking-wider font-medium">{stat.label}</span>
              <div className={`w-8 h-8 sm:w-9 sm:h-9 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center shadow-lg`}>
                <stat.icon className="w-4 h-4 text-white" />
              </div>
            </div>
            <p className={`text-xl sm:text-2xl font-display font-bold ${stat.textColor}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {renderPieChart(sentimentData, 'Sentiment Distribution')}
        {renderPieChart(categoryData, 'Category Distribution')}
      </div>

      {/* Urgency Bar Chart */}
      {urgencyData.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-sm font-semibold cs-text mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-cyan-400" /> Urgency Distribution
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={urgencyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--cs-border)" />
              <XAxis dataKey="name" tick={{ fontSize: 12, fill: 'var(--cs-muted)' }} axisLine={false} />
              <YAxis tick={{ fontSize: 12, fill: 'var(--cs-muted)' }} axisLine={false} />
              <Tooltip contentStyle={{ background: 'var(--cs-card-solid)', border: '1px solid var(--cs-border)', borderRadius: '8px', fontSize: '12px', color: 'var(--cs-text)' }} />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {urgencyData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Recent Calls */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold cs-text">Recent Calls</h3>
          <button onClick={() => navigate('/history')} className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1">
            View all <ArrowRight className="w-3 h-3" />
          </button>
        </div>
        {stats?.recent_calls && stats.recent_calls.length > 0 ? (
          <div className="space-y-2">
            {stats.recent_calls.slice(0, 5).map((call: CallRecord) => (
              <button key={call.call_id} onClick={() => navigate(`/analysis/${call.call_id}`)}
                className="w-full flex items-center justify-between p-3 rounded-xl cs-nav-hover transition-colors text-left">
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${call.status === 'completed' ? 'bg-emerald-400' : call.status === 'failed' ? 'bg-rose-400' : 'bg-amber-400 animate-pulse'}`} />
                  <div>
                    <p className="text-sm cs-text font-medium font-mono">{call.call_id}</p>
                    <p className="text-[11px] cs-muted">{new Date(call.created_at).toLocaleString()}</p>
                  </div>
                </div>
                <Badge color={call.status === 'completed' ? 'green' : call.status === 'failed' ? 'red' : 'yellow'}>{call.status}</Badge>
              </button>
            ))}
          </div>
        ) : <p className="text-sm cs-muted text-center py-8">No calls analyzed yet. Start by uploading a call.</p>}
      </div>
    </div>
  );
}
