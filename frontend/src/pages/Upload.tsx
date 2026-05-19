import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload as UploadIcon, FileAudio, FileText, X, Mic, Globe } from 'lucide-react';
import { uploadAudio, analyzeTranscript } from '../services/api';
import { usePolling } from '../hooks/usePolling';
import { useToast } from '../contexts/ToastContext';
import ProgressTracker from '../components/analysis/ProgressTracker';
import AudioPlayer from '../components/analysis/AudioPlayer';
import { clsx } from 'clsx';

type Tab = 'audio' | 'transcript';

const LANGUAGES = [
  { code: 'auto', label: 'Auto Detect' },
  { code: 'en', label: 'English' },
  { code: 'es', label: 'Spanish' },
  { code: 'fr', label: 'French' },
  { code: 'de', label: 'German' },
  { code: 'hi', label: 'Hindi' },
  { code: 'ja', label: 'Japanese' },
  { code: 'zh', label: 'Chinese' },
  { code: 'ar', label: 'Arabic' },
  { code: 'pt', label: 'Portuguese' },
  { code: 'ko', label: 'Korean' },
];

export default function UploadPage() {
  const [tab, setTab] = useState<Tab>('audio');
  const [file, setFile] = useState<File | null>(null);
  const [transcript, setTranscript] = useState('');
  const [callerName, setCallerName] = useState('');
  const [agentName, setAgentName] = useState('');
  const [language, setLanguage] = useState('auto');
  const [dragOver, setDragOver] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [callId, setCallId] = useState<string | null>(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const toast = useToast();

  const { status: pollStatus } = usePolling(callId);

  if (pollStatus?.status === 'completed' && callId) {
    toast.success('Analysis complete!');
    setTimeout(() => navigate(`/analysis/${callId}`), 500);
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setFile(e.target.files[0]);
  };

  const handleSubmit = async () => {
    setError('');
    setSubmitting(true);
    try {
      let result;
      if (tab === 'audio' && file) {
        result = await uploadAudio(file, language);
        toast.info('Audio uploaded. Analysis starting...');
      } else if (tab === 'transcript' && transcript.trim().length >= 50) {
        result = await analyzeTranscript(transcript, callerName || undefined, agentName || undefined, undefined, language);
        toast.info('Transcript submitted. Analysis starting...');
      } else {
        setError(tab === 'audio' ? 'Please select an audio file.' : 'Transcript must be at least 50 characters.');
        setSubmitting(false);
        return;
      }
      setCallId(result.call_id);
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Something went wrong.';
      setError(msg);
      toast.error(msg);
      setSubmitting(false);
    }
  };

  if (callId && pollStatus) {
    return (
      <div className="max-w-3xl mx-auto space-y-8 animate-fade-in">
        <div>
          <h1 className="text-3xl font-display font-bold gradient-text">Analyzing Call</h1>
          <p className="cs-muted mt-1 font-mono text-sm">{callId}</p>
        </div>
        <ProgressTracker status={pollStatus.status} progress={pollStatus.progress_percent} />
        <p className="text-center text-sm cs-muted">{pollStatus.message}</p>
        {pollStatus.status === 'failed' && (
          <div className="text-center">
            <button onClick={() => { setCallId(null); setSubmitting(false); }} className="btn-secondary">Try Again</button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-display font-bold gradient-text">Analyze a Call</h1>
        <p className="cs-muted mt-1">Upload an audio recording or paste a transcript for AI analysis</p>
      </div>

      {/* Tab Selector */}
      <div className="flex gap-1 cs-card-bg p-1 rounded-xl border w-fit" style={{ borderColor: 'var(--cs-border)' }}>
        {[
          { key: 'audio' as Tab, label: 'Audio Upload', icon: Mic },
          { key: 'transcript' as Tab, label: 'Paste Transcript', icon: FileText },
        ].map((t) => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={clsx('flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all',
              tab === t.key ? 'bg-gradient-to-r from-cyan-500/10 to-blue-500/10 text-cyan-400' : 'cs-muted hover:cs-text'
            )}>
            <t.icon className="w-4 h-4" />{t.label}
          </button>
        ))}
      </div>

      {/* Language Selector */}
      <div className="flex items-center gap-3">
        <Globe className="w-4 h-4 cs-muted" />
        <select value={language} onChange={(e) => setLanguage(e.target.value)} className="input-field text-sm max-w-xs">
          {LANGUAGES.map((l) => <option key={l.code} value={l.code}>{l.label}</option>)}
        </select>
      </div>

      {/* Audio Upload */}
      {tab === 'audio' && (
        <div className="space-y-5">
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            className={clsx('border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 cursor-pointer',
              dragOver ? 'border-cyan-400 bg-cyan-500/5' : 'hover:bg-opacity-40',
              file ? 'border-emerald-500/40 bg-emerald-500/5' : ''
            )}
            style={{ borderColor: !dragOver && !file ? 'var(--cs-border)' : undefined }}
            onClick={() => document.getElementById('audio-input')?.click()}
          >
            <input id="audio-input" type="file" accept=".wav,.mp3,.m4a,.webm,.ogg,.flac" onChange={handleFileSelect} className="hidden" />
            {file ? (
              <div className="flex flex-col items-center gap-3">
                <FileAudio className="w-12 h-12 text-emerald-400" />
                <div><p className="text-sm font-semibold text-emerald-300">{file.name}</p>
                  <p className="text-xs cs-muted">{(file.size / (1024 * 1024)).toFixed(2)} MB</p></div>
                <button onClick={(e) => { e.stopPropagation(); setFile(null); }} className="text-xs cs-muted hover:text-rose-400 flex items-center gap-1">
                  <X className="w-3 h-3" /> Remove</button>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3">
                <UploadIcon className="w-12 h-12 cs-muted" />
                <p className="text-sm cs-text">Drag & drop an audio file here, or click to browse</p>
                <p className="text-xs cs-muted">Supports WAV, MP3, M4A, WebM, OGG, FLAC (max 50MB)</p>
              </div>
            )}
          </div>
          {file && <AudioPlayer file={file} />}
        </div>
      )}

      {/* Transcript Input */}
      {tab === 'transcript' && (
        <div className="space-y-4">
          <textarea value={transcript} onChange={(e) => setTranscript(e.target.value)}
            placeholder="Paste your call transcript here..." rows={12} className="input-field font-mono text-sm resize-none" />
          <p className="text-xs cs-muted">{transcript.length} characters (minimum 50)</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div><label className="text-xs cs-muted mb-1 block">Caller Name (optional)</label>
              <input value={callerName} onChange={(e) => setCallerName(e.target.value)} className="input-field text-sm" placeholder="e.g. John Smith" /></div>
            <div><label className="text-xs cs-muted mb-1 block">Agent Name (optional)</label>
              <input value={agentName} onChange={(e) => setAgentName(e.target.value)} className="input-field text-sm" placeholder="e.g. Sarah Johnson" /></div>
          </div>
        </div>
      )}

      {error && <div className="bg-rose-500/10 border border-rose-500/20 rounded-xl p-4 text-sm text-rose-300">{error}</div>}

      <button onClick={handleSubmit} disabled={submitting || (tab === 'audio' ? !file : transcript.length < 50)} className="btn-primary w-full py-3.5 text-base font-semibold">
        {submitting ? 'Starting Analysis...' : 'Analyze Call'}
      </button>
    </div>
  );
}
