import { useState, useRef, useEffect } from 'react';
import { Play, Pause, RotateCcw, Volume2 } from 'lucide-react';

interface AudioPlayerProps {
  src?: string;
  file?: File | null;
}

export default function AudioPlayer({ src, file }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrent] = useState(0);
  const [duration, setDuration] = useState(0);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  useEffect(() => {
    if (file) {
      const url = URL.createObjectURL(file);
      setAudioUrl(url);
      return () => URL.revokeObjectURL(url);
    } else if (src) {
      setAudioUrl(src);
    }
  }, [file, src]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (playing) { audioRef.current.pause(); }
    else { audioRef.current.play(); }
    setPlaying(!playing);
  };

  const restart = () => {
    if (!audioRef.current) return;
    audioRef.current.currentTime = 0;
    setCurrent(0);
  };

  const seek = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!audioRef.current) return;
    const time = parseFloat(e.target.value);
    audioRef.current.currentTime = time;
    setCurrent(time);
  };

  const fmt = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${sec.toString().padStart(2, '0')}`;
  };

  if (!audioUrl) return null;

  return (
    <div className="glass-card p-4">
      <audio
        ref={audioRef}
        src={audioUrl}
        onTimeUpdate={() => setCurrent(audioRef.current?.currentTime || 0)}
        onLoadedMetadata={() => setDuration(audioRef.current?.duration || 0)}
        onEnded={() => setPlaying(false)}
      />
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <button onClick={togglePlay} className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg hover:shadow-cyan-500/25 transition-shadow">
            {playing ? <Pause className="w-4 h-4 text-white" /> : <Play className="w-4 h-4 text-white ml-0.5" />}
          </button>
          <button onClick={restart} className="p-2 cs-muted hover:cs-text transition-colors">
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>

        <div className="flex-1 flex items-center gap-3">
          <span className="text-xs font-mono cs-muted w-10">{fmt(currentTime)}</span>
          <input
            type="range" min={0} max={duration || 0} step={0.1} value={currentTime}
            onChange={seek}
            className="flex-1 h-1.5 rounded-full appearance-none cursor-pointer accent-cyan-500"
            style={{ background: `linear-gradient(to right, #06b6d4 ${(currentTime / (duration || 1)) * 100}%, #334155 0%)` }}
          />
          <span className="text-xs font-mono cs-muted w-10">{fmt(duration)}</span>
        </div>

        <Volume2 className="w-4 h-4 cs-muted" />
      </div>
    </div>
  );
}
