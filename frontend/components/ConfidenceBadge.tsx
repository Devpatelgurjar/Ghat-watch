import React from 'react';
import { ConfidenceTier } from '@/lib/types';

interface ConfidenceBadgeProps {
  confidence: ConfidenceTier;
  coveragePct?: number;
}

export function ConfidenceBadge({ confidence, coveragePct }: ConfidenceBadgeProps) {
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium text-[#12262D] bg-white border border-[#DCE4E7] shadow-2xs"
      title={`Data completeness confidence: ${confidence}${coveragePct !== undefined ? ` (${coveragePct}% valid scored readings)` : ''}`}
    >
      <span className="w-2 h-2 rounded-full bg-[#5B6B73]" aria-hidden="true" />
      <span>Confidence: <strong>{confidence}</strong></span>
      {coveragePct !== undefined && (
        <span className="text-[#5B6B73]">({coveragePct}%)</span>
      )}
    </span>
  );
}
