import Link from 'next/link';
import { AlertTriangle, ShieldAlert, FileText, ArrowRight, CheckCircle2 } from 'lucide-react';
import { fetchRankedGhats, fetchMetadata } from '@/lib/api';
import { CaveatBanner } from '@/components/CaveatBanner';
import { GhatCard } from '@/components/GhatCard';

import { GhatSummary, MetaResponse } from '@/lib/types';

export default async function HomePage() {
  let ghats: GhatSummary[] = [];
  let meta: MetaResponse | null = null;
  let fetchError: string | null = null;

  try {
    [ghats, meta] = await Promise.all([
      fetchRankedGhats(),
      fetchMetadata(),
    ]);
  } catch (err: any) {
    fetchError = err.message || 'Unable to connect to backend server';
  }

  return (
    <div className="space-y-6">
      {/* Top Caveat Banner */}
      <CaveatBanner />

      {/* Hero / Context Title */}
      <div className="bg-white border border-[#DCE4E7] rounded-xl p-6 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-[#0B4F5C]/10 text-[#0B4F5C] text-xs font-bold uppercase tracking-wider mb-2">
              Decision-Support Intelligence
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-[#12262D] tracking-tight">
              Bhopal Immersion Ghats: Risk Ranking
            </h1>
            <p className="text-sm text-[#5B6B73] mt-1 max-w-2xl">
              Water quality vulnerability ranking across Bhopal&apos;s 7 official immersion sites for Durga Visarjan
              (20 October 2026), evaluated against CPCB Class B outdoor bathing criteria from 2023–2025 MPPCB testing data.
            </p>
          </div>

          <div className="shrink-0">
            <Link
              href="/brief"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-[#0B4F5C] text-white hover:bg-[#07353E] transition-all font-semibold text-sm shadow-sm"
            >
              <FileText className="w-4 h-4" />
              <span>Forwardable Brief</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </Link>
          </div>
        </div>

        {/* Quick Summary Metrics */}
        {meta && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-5 border-t border-[#E2E8F0] text-xs">
            <div>
              <span className="text-[#5B6B73] block">Target Event</span>
              <strong className="text-[#12262D] text-sm font-bold">20 Oct 2026</strong>
            </div>
            <div>
              <span className="text-[#5B6B73] block">Statutory Standard</span>
              <strong className="text-[#0B4F5C] text-sm font-bold">CPCB Class B</strong>
            </div>
            <div>
              <span className="text-[#5B6B73] block">Total Monitored Ghats</span>
              <strong className="text-[#12262D] text-sm font-bold">7 Ghats</strong>
            </div>
            <div>
              <span className="text-[#5B6B73] block">Ranking Model Stability</span>
              <strong className="text-[#3C8D6E] text-sm font-bold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> High Robustness
              </strong>
            </div>
          </div>
        )}
      </div>

      {fetchError && (
        <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-xl text-sm">
          <p className="font-bold">Backend Connection Note</p>
          <p className="text-xs mt-1">{fetchError}</p>
          <p className="text-xs mt-1">Make sure the FastAPI backend is running on <code>http://127.0.0.1:8000</code>.</p>
        </div>
      )}

      {/* Ranked List of 7 GhatCards */}
      <section aria-labelledby="ranked-ghats-heading" className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 id="ranked-ghats-heading" className="text-lg font-bold text-[#12262D]">
            Official Ranking (Highest to Lowest Vulnerability)
          </h2>
          <span className="text-xs text-[#5B6B73]">
            Sorted by Risk Score (0–100)
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {ghats.map((ghat) => (
            <GhatCard key={ghat.id} ghat={ghat} />
          ))}
        </div>
      </section>

      {/* What this tool does NOT cover section */}
      {meta && (
        <section
          aria-labelledby="not-covered-heading"
          className="bg-white border border-[#DCE4E7] rounded-xl p-6 shadow-xs text-sm"
        >
          <div className="flex items-center gap-2 mb-3">
            <ShieldAlert className="w-5 h-5 text-[#D98A1F]" />
            <h2 id="not-covered-heading" className="text-base font-bold text-[#12262D]">
              What This Tool Does NOT Cover (Operational Scope)
            </h2>
          </div>
          <p className="text-xs text-[#5B6B73] mb-4">
            To ensure responsible and safe decision-making by Bhopal Municipal Corporation officers, please review the explicit boundaries of this decision-support system:
          </p>

          <ul className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-[#12262D]">
            {meta.what_this_tool_does_not_cover.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2 bg-[#F8FAFC] p-3 rounded-lg border border-[#E2E8F0]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#D98A1F] mt-1.5 shrink-0" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
