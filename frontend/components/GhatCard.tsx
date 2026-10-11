import React from 'react';
import Link from 'next/link';
import { ChevronRight, AlertTriangle } from 'lucide-react';
import { GhatSummary } from '@/lib/types';
import { RiskBar } from './RiskBar';
import { ConfidenceBadge } from './ConfidenceBadge';

interface GhatCardProps {
  ghat: GhatSummary;
}

export function GhatCard({ ghat }: GhatCardProps) {
  // Rank badge styling
  let rankBg = 'bg-[#12262D] text-white';
  if (ghat.rank === 1) rankBg = 'bg-[#B83A32] text-white';
  else if (ghat.rank === 2) rankBg = 'bg-[#D98A1F] text-white';
  else if (ghat.rank === 3) rankBg = 'bg-[#0B4F5C] text-white';

  const hasMissingData = ghat.missing_share_pct > 10;

  return (
    <div className="bg-white border border-[#DCE4E7] rounded-xl p-5 shadow-xs hover:border-[#1F8A8A] transition-all hover:shadow-md flex flex-col justify-between">
      <div>
        {/* Top Header: Rank + Site Name + Water Body */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-start gap-3">
            <span
              className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm shrink-0 shadow-xs ${rankBg}`}
              title={`Rank ${ghat.rank} out of 7`}
            >
              #{ghat.rank}
            </span>
            <div>
              <Link
                href={`/ghats/${ghat.id}`}
                className="text-lg font-bold text-[#12262D] hover:text-[#0B4F5C] transition-colors leading-snug line-clamp-1"
              >
                {ghat.name}
              </Link>
              <span className="text-xs font-medium text-[#5B6B73] block mt-0.5">
                Water body: <strong className="text-[#12262D]">{ghat.water_body}</strong>
              </span>
            </div>
          </div>

          <div className="shrink-0">
            <ConfidenceBadge
              confidence={ghat.confidence}
              coveragePct={ghat.coverage_pct}
            />
          </div>
        </div>

        {/* Risk Score Bar */}
        <div className="my-3">
          <RiskBar score={ghat.risk_score} tier={ghat.risk_tier} />
        </div>

        {/* One-Line Plain Reason */}
        <div className="bg-[#F5F8F9] p-3 rounded-lg border border-[#E2E8F0] my-3">
          <p className="text-xs text-[#12262D] leading-relaxed">
            <strong className="text-[#0B4F5C]">Finding: </strong>
            {ghat.top_reason}
          </p>
        </div>

        {/* Missing Data Warning Indicator */}
        {hasMissingData && (
          <div className="flex items-center gap-1.5 text-xs text-[#5B6B73] mb-3">
            <span className="w-2.5 h-2.5 rounded-xs hatch-pattern border border-[#CBD5E1]" aria-hidden="true" />
            <span>
              {ghat.missing_share_pct}% readings missing or unrecorded in official tables
            </span>
          </div>
        )}
      </div>

      {/* Action Link Footer */}
      <div className="pt-3 border-t border-[#F1F5F9] flex items-center justify-between mt-1">
        <span className="text-xs text-[#5B6B73]">
          {ghat.caveats.length > 0 ? `${ghat.caveats.length} transparency notes` : 'Standard monitoring'}
        </span>
        <Link
          href={`/ghats/${ghat.id}`}
          className="inline-flex items-center gap-1 text-xs font-bold text-[#0B4F5C] hover:text-[#1F8A8A] transition-colors"
        >
          <span>View test readings vs Class B</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}
