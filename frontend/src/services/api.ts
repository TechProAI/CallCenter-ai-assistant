import axios from 'axios';
import type { AnalysisStatus, FullAnalysis, DashboardStats, CallRecord } from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
});

// ── Calls ──

export async function uploadAudio(file: File, language = 'auto'): Promise<AnalysisStatus> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('language', language);
  const { data } = await api.post('/calls/upload-audio', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function analyzeTranscript(
  transcript: string,
  callerName?: string,
  agentName?: string,
  callDate?: string,
  language?: string,
): Promise<AnalysisStatus> {
  const { data } = await api.post('/calls/analyze-transcript', {
    transcript,
    caller_name: callerName || null,
    agent_name: agentName || null,
    call_date: callDate || null,
    language: language || 'auto',
  });
  return data;
}

export async function getAnalysisStatus(callId: string): Promise<AnalysisStatus> {
  const { data } = await api.get(`/calls/status/${callId}`);
  return data;
}

export async function getCallAnalysis(callId: string): Promise<FullAnalysis> {
  const { data } = await api.get(`/calls/${callId}`);
  return data;
}

export async function listCalls(page = 1, pageSize = 20): Promise<{ calls: CallRecord[]; total_count: number }> {
  const { data } = await api.get('/calls/', { params: { page, page_size: pageSize } });
  return data;
}

export async function deleteCall(callId: string): Promise<void> {
  await api.delete(`/calls/${callId}`);
}

export function getExportPdfUrl(callId: string): string {
  return `/api/calls/${callId}/export-pdf`;
}

// ── Dashboard ──

export async function getDashboardStats(): Promise<DashboardStats> {
  const { data } = await api.get('/dashboard/stats');
  return data;
}
