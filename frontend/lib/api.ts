/**
 * API client for fetching data from Ghat Watch FastAPI backend.
 * Supports both container-internal networking and browser-local access.
 */
import { BriefResponse, GhatDetail, GhatSummary, MetaResponse } from './types';

function getApiBaseUrl(): string {
  // If running in browser:
  if (typeof window !== 'undefined') {
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }
  // If running on server inside Docker container:
  if (process.env.INTERNAL_API_URL) {
    return process.env.INTERNAL_API_URL;
  }
  return process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
}

export async function fetchRankedGhats(): Promise<GhatSummary[]> {
  const url = `${getApiBaseUrl()}/api/ghats`;
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) {
    throw new Error(`Failed to fetch ranked ghats: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchGhatDetail(id: string): Promise<GhatDetail> {
  const url = `${getApiBaseUrl()}/api/ghats/${id}`;
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) {
    throw new Error(`Failed to fetch ghat detail for ${id}: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchBrief(lang: 'en' | 'hi' = 'en'): Promise<BriefResponse> {
  const url = `${getApiBaseUrl()}/api/brief?lang=${lang}`;
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) {
    throw new Error(`Failed to fetch brief (${lang}): ${res.statusText}`);
  }
  return res.json();
}

export async function fetchMetadata(): Promise<MetaResponse> {
  const url = `${getApiBaseUrl()}/api/meta`;
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) {
    throw new Error(`Failed to fetch metadata: ${res.statusText}`);
  }
  return res.json();
}

export function getReportPdfUrl(reportFile: string, pageNumber: string): string {
  // Client browser link
  const clientBase = typeof window !== 'undefined'
    ? (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
    : 'http://localhost:8000';
  return `${clientBase}/reports/${reportFile}#page=${pageNumber}`;
}
