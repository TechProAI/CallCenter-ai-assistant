import { MessageSquare, User, Headphones } from 'lucide-react';
import type { Transcript } from '../../types';

export default function TranscriptView({ data }: { data: Transcript }) {
  const hasSegments = data.segments.length > 1 || (data.segments.length === 1 && data.segments[0].speaker !== 'Unknown');

  return (
    <div className="space-y-6">
      {/* Meta */}
      <div className="flex items-center gap-4 text-sm text-slate-400">
        {data.language && <span>Language: <strong className="text-slate-200 uppercase">{data.language}</strong></span>}
        {data.duration_seconds && <span>Duration: <strong className="text-slate-200">{Math.round(data.duration_seconds)}s</strong></span>}
        <span>Length: <strong className="text-slate-200">{data.full_text.length.toLocaleString()} chars</strong></span>
      </div>

      {/* Segments or Full Text */}
      {hasSegments ? (
        <div className="space-y-3">
          {data.segments.map((seg, i) => {
            const isAgent = seg.speaker?.toLowerCase().includes('agent');
            return (
              <div key={i} className={`flex gap-3 ${isAgent ? 'justify-start' : 'justify-end'}`}>
                <div className={`max-w-[75%] rounded-2xl p-4 ${isAgent ? 'bg-slate-800/80 rounded-tl-sm' : 'bg-cyan-900/30 border border-cyan-800/30 rounded-tr-sm'}`}>
                  <div className="flex items-center gap-2 mb-1.5">
                    {isAgent ? <Headphones className="w-3.5 h-3.5 text-violet-400" /> : <User className="w-3.5 h-3.5 text-cyan-400" />}
                    <span className={`text-xs font-semibold ${isAgent ? 'text-violet-400' : 'text-cyan-400'}`}>{seg.speaker || 'Unknown'}</span>
                  </div>
                  <p className="text-sm text-slate-200 leading-relaxed">{seg.text}</p>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/40">
          <div className="flex items-center gap-2 mb-3">
            <MessageSquare className="w-4 h-4 text-slate-400" />
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Full Transcript</span>
          </div>
          <p className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">{data.full_text}</p>
        </div>
      )}
    </div>
  );
}
