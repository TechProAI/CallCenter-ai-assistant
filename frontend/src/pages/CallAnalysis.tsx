import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Clock, FileAudio, Trash2, Download } from 'lucide-react';
import { getCallAnalysis, deleteCall, getExportPdfUrl } from '../services/api';
import { usePolling } from '../hooks/usePolling';
import { useToast } from '../contexts/ToastContext';
import { Badge, LoadingSpinner } from '../components/common';
import ProgressTracker from '../components/analysis/ProgressTracker';
import TranscriptView from '../components/analysis/TranscriptView';
import SummaryView from '../components/analysis/SummaryView';
import QualityScoresView from '../components/analysis/QualityScoresView';
import SentimentView from '../components/analysis/SentimentView';
import RoutingView from '../components/analysis/RoutingView';
import CoachingView from '../components/analysis/CoachingView';
import type { FullAnalysis } from '../types';
import { clsx } from 'clsx';

const tabs = [
  { key: 'summary', label: 'Summary' },
  { key: 'transcript', label: 'Transcript' },
  { key: 'quality', label: 'Quality Scores' },
  { key: 'sentiment', label: 'Sentiment' },
  { key: 'routing', label: 'Routing' },
  { key: 'coaching', label: 'Coaching' },
];

export default function CallAnalysis() {
  const { callId } = useParams<{ callId: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  const [analysis, setAnalysis] = useState<FullAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('summary');
  const [deleting, setDeleting] = useState(false);

  const isProcessing = analysis?.call?.status !== 'completed' && analysis?.call?.status !== 'failed';
  const { status: pollStatus } = usePolling(isProcessing ? callId! : null);

  const fetchData = () => {
    if (!callId) return;
    getCallAnalysis(callId).then(setAnalysis).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, [callId]);

  useEffect(() => {
    if (pollStatus?.status === 'completed') { fetchData(); toast.success('Analysis complete!'); }
    if (pollStatus?.status === 'failed') toast.error('Analysis failed.');
  }, [pollStatus?.status]);

  const handleDelete = async () => {
    if (!callId || !confirm('Delete this call and all analysis data?')) return;
    setDeleting(true);
    try { await deleteCall(callId); toast.success('Call deleted.'); navigate('/history'); }
    catch { setDeleting(false); toast.error('Failed to delete.'); }
  };

  const handleExportPdf = () => {
    if (!callId) return;
    window.open(getExportPdfUrl(callId), '_blank');
    toast.info('Downloading PDF report...');
  };

  if (loading) return <div className="flex items-center justify-center h-[60vh]"><LoadingSpinner size="lg" text="Loading analysis..." /></div>;
  if (!analysis?.call) return <div className="text-center py-20 cs-muted">Call not found.</div>;

  const call = analysis.call;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate(-1)} className="p-2 rounded-lg cs-nav-hover transition-colors">
            <ArrowLeft className="w-5 h-5 cs-muted" />
          </button>
          <div>
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-xl sm:text-2xl font-display font-bold cs-heading font-mono">{call.call_id}</h1>
              <Badge color={call.status === 'completed' ? 'green' : call.status === 'failed' ? 'red' : 'yellow'}>{call.status}</Badge>
            </div>
            <div className="flex items-center gap-4 mt-1 text-xs cs-muted flex-wrap">
              <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{new Date(call.created_at).toLocaleString()}</span>
              {call.input_type === 'audio' && call.file_name && <span className="flex items-center gap-1"><FileAudio className="w-3 h-3" />{call.file_name}</span>}
              {call.processing_time_seconds && <span>{call.processing_time_seconds}s processing</span>}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {call.status === 'completed' && (
            <button onClick={handleExportPdf} className="btn-secondary flex items-center gap-2 text-sm">
              <Download className="w-4 h-4" /> Export PDF
            </button>
          )}
          <button onClick={handleDelete} disabled={deleting} className="p-2 rounded-lg hover:bg-rose-500/10 cs-muted hover:text-rose-400 transition-colors">
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {isProcessing && pollStatus && <ProgressTracker status={pollStatus.status} progress={pollStatus.progress_percent} />}

      {call.status === 'completed' && (
        <>
          <div className="flex gap-1 border-b overflow-x-auto" style={{ borderColor: 'var(--cs-border)' }}>
            {tabs.map((t) => (
              <button key={t.key} onClick={() => setActiveTab(t.key)}
                className={clsx('px-4 sm:px-5 py-3 text-sm font-medium whitespace-nowrap transition-all', activeTab === t.key ? 'tab-active' : 'tab-inactive')}>
                {t.label}
              </button>
            ))}
          </div>

          <div className="min-h-[400px]">
            {activeTab === 'summary' && analysis.summary && <SummaryView data={analysis.summary} />}
            {activeTab === 'transcript' && analysis.transcript && <TranscriptView data={analysis.transcript} />}
            {activeTab === 'quality' && analysis.quality_scores && <QualityScoresView data={analysis.quality_scores} />}
            {activeTab === 'sentiment' && analysis.sentiment && <SentimentView data={analysis.sentiment} />}
            {activeTab === 'routing' && analysis.routing && <RoutingView data={analysis.routing} />}
            {activeTab === 'coaching' && analysis.coaching && <CoachingView data={analysis.coaching} />}
            {!analysis[activeTab === 'quality' ? 'quality_scores' : activeTab as keyof FullAnalysis] &&
              <p className="cs-muted py-8 text-center">{tabs.find(t => t.key === activeTab)?.label} not available.</p>}
          </div>
        </>
      )}

      {call.status === 'failed' && (
        <div className="glass-card p-8 text-center">
          <p className="text-rose-400 text-lg font-semibold mb-2">Analysis Failed</p>
          <p className="text-sm cs-muted">{call.error || 'An unexpected error occurred.'}</p>
          <button onClick={() => navigate('/upload')} className="btn-primary mt-6">Try Again</button>
        </div>
      )}
    </div>
  );
}
