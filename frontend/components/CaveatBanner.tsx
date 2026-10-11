import React from 'react';
import { AlertCircle, Info } from 'lucide-react';

interface CaveatBannerProps {
  message?: string;
  subtext?: string;
}

export function CaveatBanner({
  message = 'Based on MPPCB test readings from 2023–2025, not current water quality.',
  subtext = 'Decision-support baseline for BMC planning ahead of Durga Visarjan on 20 October 2026. Evaluated against CPCB Class B outdoor bathing criteria.',
}: CaveatBannerProps) {
  return (
    <div className="bg-[#EBF3F5] border-l-4 border-[#0B4F5C] p-4 rounded-r-lg shadow-2xs mb-6 text-[#12262D]">
      <div className="flex items-start gap-3">
        <Info className="w-5 h-5 text-[#0B4F5C] mt-0.5 shrink-0" aria-hidden="true" />
        <div>
          <h2 className="text-sm font-bold text-[#0B4F5C] uppercase tracking-wide">
            Official Data Notice &amp; Scope
          </h2>
          <p className="text-sm font-semibold text-[#12262D] mt-0.5">
            {message}
          </p>
          <p className="text-xs text-[#5B6B73] mt-1">
            {subtext}
          </p>
        </div>
      </div>
    </div>
  );
}
