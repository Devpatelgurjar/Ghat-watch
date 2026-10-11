'use client';

import React, { Suspense, useEffect, useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { ArrowLeft, Printer, AlertCircle, FileCheck2, Info } from 'lucide-react';
import { BriefResponse } from '@/lib/types';
import { fetchBrief } from '@/lib/api';
import { LangToggle } from '@/components/LangToggle';

function BriefContent() {
  const searchParams = useSearchParams();
  const initialLang = (searchParams.get('lang') === 'hi' ? 'hi' : 'en') as 'en' | 'hi';
  const [lang, setLang] = useState<'en' | 'hi'>(initialLang);
  const [briefEn, setBriefEn] = useState<BriefResponse | null>(null);
  const [briefHi, setBriefHi] = useState<BriefResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadBriefs() {
      try {
        setLoading(true);
        const [en, hi] = await Promise.all([
          fetchBrief('en'),
          fetchBrief('hi'),
        ]);
        setBriefEn(en);
        setBriefHi(hi);
      } catch (err: any) {
        setError(err.message || 'Failed to load decision brief');
      } finally {
        setLoading(false);
      }
    }
    loadBriefs();
  }, []);

  const currentBrief = lang === 'hi' ? briefHi : briefEn;

  const handlePrint = () => {
    if (typeof window !== 'undefined') {
      window.print();
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 text-[#5B6B73]">
        <div className="text-center space-y-2">
          <div className="w-8 h-8 border-3 border-[#0B4F5C] border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm font-semibold">Compiling decision brief...</p>
        </div>
      </div>
    );
  }

  if (error || !currentBrief) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-800 p-6 rounded-xl text-center space-y-3">
        <AlertCircle className="w-8 h-8 text-red-600 mx-auto" />
        <h2 className="text-base font-bold">Error Generating Brief</h2>
        <p className="text-xs">{error || 'Data unavailable'}</p>
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-xs font-bold text-[#0B4F5C] underline"
        >
          Return to home page
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Interactive Controls Bar (Hidden during Print) */}
      <div className="no-print bg-white border border-[#DCE4E7] rounded-xl p-4 shadow-xs flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs font-bold text-[#0B4F5C] hover:text-[#1F8A8A] transition-colors px-3 py-1.5 rounded-lg border border-[#DCE4E7]"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Ghat Rankings</span>
          </Link>
          <div className="h-4 w-px bg-[#DCE4E7] hidden sm:block" />
          <span className="text-xs text-[#5B6B73] hidden sm:inline">
            Language selection:
          </span>
          <LangToggle currentLang={lang} onToggle={(newLang) => setLang(newLang)} />
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handlePrint}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#0B4F5C] hover:bg-[#07353E] transition-all text-white font-bold text-xs shadow-sm cursor-pointer"
            title="Print or export as PDF (A4 format)"
          >
            <Printer className="w-4 h-4" />
            <span>Print / Save as PDF</span>
          </button>
        </div>
      </div>

      {/* A4 Printable Document Container */}
      <article
        className={`bg-white border border-[#DCE4E7] rounded-2xl p-8 sm:p-12 shadow-md max-w-4xl mx-auto print-page text-[#12262D] space-y-6 ${
          lang === 'hi' ? "font-['Noto_Sans_Devanagari']" : 'font-sans'
        }`}
      >
        {/* Visible Notice in Hindi Mode */}
        {lang === 'hi' && currentBrief.native_speaker_review_notice && (
          <div className="bg-amber-50 border border-amber-300 text-amber-900 px-3 py-1.5 rounded text-xs font-medium flex items-center justify-between no-print">
            <span>नोट: यह अनुवाद स्वचालित रूप से तैयार किया गया है ({currentBrief.native_speaker_review_notice})</span>
            <span className="text-[10px] text-amber-700">संख्याएं एवं रिपोर्ट संदर्भ पूर्णतः सटीक हैं</span>
          </div>
        )}

        {/* Brief Header */}
        <header className="border-b-2 border-[#0B4F5C] pb-4 space-y-2">
          <div className="flex items-start justify-between gap-4">
            <div>
              <span className="text-xs font-extrabold uppercase tracking-widest text-[#0B4F5C] bg-[#EBF3F5] px-2.5 py-0.5 rounded">
                Bhopal Municipal Corporation · Visarjan 2026
              </span>
              <h1 className="text-xl sm:text-2xl font-black text-[#12262D] tracking-tight mt-1">
                {currentBrief.title}
              </h1>
            </div>
            <div className="text-right shrink-0 text-xs text-[#5B6B73]">
              <p><strong>{lang === 'hi' ? 'जारी तिथि:' : 'Date:'}</strong> {currentBrief.date}</p>
              <p><strong>{lang === 'hi' ? 'लक्षित आयोजन:' : 'Event:'}</strong> {currentBrief.event_target}</p>
            </div>
          </div>
          <p className="text-xs text-[#5B6B73]">
            <strong>{lang === 'hi' ? 'हेतु तैयार:' : 'Prepared for:'}</strong> {currentBrief.target_user_role}
          </p>
        </header>

        {/* Honest Framing & Notice */}
        <section className="bg-[#F5F8F9] p-4 rounded-xl border border-[#DCE4E7] break-inside-avoid">
          <h2 className="text-xs font-bold uppercase tracking-wider text-[#0B4F5C] flex items-center gap-1.5 mb-1">
            <Info className="w-3.5 h-3.5" />
            <span>{lang === 'hi' ? 'मूल्यांकन का आधार एवं दायरा' : 'Assessment Basis & Scope'}</span>
          </h2>
          <p className="text-xs text-[#12262D] font-medium leading-relaxed">
            {currentBrief.honest_framing}
          </p>
        </section>

        {/* Top 3 Priority Immersion Ghats */}
        <section className="space-y-3 break-inside-avoid">
          <h2 className="text-sm font-extrabold text-[#12262D] uppercase tracking-wide border-b border-[#E2E8F0] pb-1">
            {lang === 'hi'
              ? 'प्राथमिक विसर्जन स्थल (ऐतिहासिक जोखिम के अनुसार शीर्ष 3)'
              : 'Priority Immersion Sites (Top 3 by Historical Risk)'}
          </h2>

          <div className="space-y-3">
            {currentBrief.top_ghats.map((ghat) => (
              <div
                key={ghat.rank}
                className="p-4 rounded-xl border border-[#DCE4E7] bg-white shadow-2xs space-y-2 break-inside-avoid"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded bg-[#0B4F5C] text-white flex items-center justify-center font-bold text-xs">
                      #{ghat.rank}
                    </span>
                    <h3 className="text-base font-bold text-[#12262D]">
                      {ghat.name}
                    </h3>
                    <span className="text-xs text-[#5B6B73]">({ghat.water_body})</span>
                  </div>

                  <div className="flex items-center gap-2 text-xs">
                    <span className="font-bold px-2 py-0.5 rounded bg-red-100 text-red-800">
                      {lang === 'hi' ? 'जोखिम:' : 'Risk:'} {ghat.risk_score}/100 ({ghat.risk_tier})
                    </span>
                    <span className="px-2 py-0.5 rounded border border-[#DCE4E7] text-[#5B6B73]">
                      {lang === 'hi' ? 'विश्वसनीयता:' : 'Confidence:'} {ghat.confidence}
                    </span>
                  </div>
                </div>

                <p className="text-xs text-[#12262D] leading-relaxed">
                  <strong>{lang === 'hi' ? 'मुख्य निष्कर्ष:' : 'Finding:'} </strong>
                  {ghat.plain_reason}
                </p>

                <p className="text-[11px] text-[#5B6B73]">
                  <strong>{lang === 'hi' ? 'साक्ष्य संदर्भ:' : 'Evidence Citation:'} </strong>
                  {ghat.evidence_citation}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* Suggested Checks for Visarjan Planning */}
        <section className="space-y-2 break-inside-avoid">
          <h2 className="text-sm font-extrabold text-[#12262D] uppercase tracking-wide border-b border-[#E2E8F0] pb-1">
            {lang === 'hi'
              ? 'नगर निगम अधिकारी हेतु अनुशंसित प्राथमिक जाँच एवं कदम'
              : 'Suggested Planning Priorities for BMC Officers'}
          </h2>
          <ul className="space-y-1.5 text-xs text-[#12262D]">
            {currentBrief.recommended_checks.map((check, idx) => (
              <li key={idx} className="flex items-start gap-2 bg-[#F8FAFC] p-2.5 rounded-lg border border-[#E2E8F0]">
                <FileCheck2 className="w-4 h-4 text-[#0B4F5C] shrink-0 mt-0.5" />
                <span className="leading-relaxed">{check}</span>
              </li>
            ))}
          </ul>
        </section>

        {/* Monitoring Data Gaps & Limitations */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 break-inside-avoid pt-2">
          {/* Data Gaps */}
          <section className="space-y-2">
            <h2 className="text-xs font-bold text-[#B83A32] uppercase tracking-wide">
              {lang === 'hi' ? 'डेटा अंतराल (कमियाँ)' : 'Monitoring Data Gaps'}
            </h2>
            <ul className="space-y-1 text-xs text-[#5B6B73]">
              {currentBrief.data_gaps.map((gap, idx) => (
                <li key={idx} className="flex items-start gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#B83A32] shrink-0 mt-1.5" />
                  <span className="leading-relaxed">{gap}</span>
                </li>
              ))}
            </ul>
          </section>

          {/* Statutory Limits & Scope */}
          <section className="space-y-2">
            <h2 className="text-xs font-bold text-[#0B4F5C] uppercase tracking-wide">
              {lang === 'hi' ? 'दायरा एवं सीमाएँ' : 'Scope & Legal Boundaries'}
            </h2>
            <ul className="space-y-1 text-xs text-[#5B6B73]">
              {currentBrief.limitations.map((lim, idx) => (
                <li key={idx} className="flex items-start gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#0B4F5C] shrink-0 mt-1.5" />
                  <span className="leading-relaxed">{lim}</span>
                </li>
              ))}
            </ul>
          </section>
        </div>

        {/* Official Signoff Footer */}
        <footer className="border-t border-[#DCE4E7] pt-4 flex flex-col sm:flex-row items-center justify-between text-[11px] text-[#5B6B73] gap-2">
          <span>Ghat Watch · Decision Brief · Track 2 Visarjan Planning</span>
          <span>CPCB Class B Outdoor Bathing Standard (DO ≥ 5.0, BOD ≤ 3.0)</span>
        </footer>
      </article>
    </div>
  );
}

export default function DecisionBriefPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center py-20 text-[#5B6B73]">
        <div className="text-center space-y-2">
          <div className="w-8 h-8 border-3 border-[#0B4F5C] border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm font-semibold">Loading decision brief...</p>
        </div>
      </div>
    }>
      <BriefContent />
    </Suspense>
  );
}
