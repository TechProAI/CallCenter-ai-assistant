import { useState, useEffect, useRef, useCallback } from 'react';
import { getAnalysisStatus } from '../services/api';
import type { AnalysisStatus } from '../types';

export function usePolling(callId: string | null, intervalMs = 3000) {
  const [status, setStatus] = useState<AnalysisStatus | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval>>();

  const stopPolling = useCallback(() => {
    setIsPolling(false);
    if (timerRef.current) clearInterval(timerRef.current);
  }, []);

  useEffect(() => {
    if (!callId) return;

    setIsPolling(true);

    const poll = async () => {
      try {
        const data = await getAnalysisStatus(callId);
        setStatus(data);
        if (data.status === 'completed' || data.status === 'failed') {
          stopPolling();
        }
      } catch {
        stopPolling();
      }
    };

    poll();
    timerRef.current = setInterval(poll, intervalMs);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [callId, intervalMs, stopPolling]);

  return { status, isPolling, stopPolling };
}
