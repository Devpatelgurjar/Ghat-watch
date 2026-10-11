import React from 'react';
import { RiskTier } from '@/lib/types';

interface RiskBarProps {
  score: number;
  tier?: RiskTier;
  showLabel?: boolean;
}

export function RiskBar({ score, tier, showLabel = true }: RiskBarProps) {
  // Determine color based on risk score
  let barColor = '#3C8D6E'; // Lower relative risk
  let tierLabel = 'Lower relative risk';

  if (score >= 70) {
    barColor = '#B83A32'; // High
    tierLabel = 'High risk';
  } else if (score >= 50) {
    barColor = '#D98A1F'; // Elevated
    tierLabel = 'Elevated risk';
  }

  const effectiveTier = tier ? (tier === 'Lower relative risk' ? 'Lower relative risk' : `${tier} risk`) : tierLabel;

  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex justify-between items-center text-xs mb-1.5">
          <span className="font-semibold text-[#12262D]">
            Risk Score: <span className="text-base font-bold" style={{ color: barColor }}>{score.toFixed(1)}</span>
            <span className="text-xs text-[#5B6B73]">/100</span>
          </span>
          <span
            className="px-2 py-0.5 rounded text-xs font-semibold"
            style={{
              backgroundColor: `${barColor}15`,
              color: barColor,
              border: `1px solid ${barColor}40`,
            }}
          >
            {effectiveTier}
          </span>
        </div>
      )}
      <div
        className="w-full bg-[#E2E8F0] h-3 rounded-full overflow-hidden"
        role="progressbar"
        aria-valuenow={score}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`Risk score ${score.toFixed(1)} out of 100 (${effectiveTier})`}
      >
        <div
          className="h-full rounded-full transition-all duration-300"
          style={{
            width: `${Math.min(100, Math.max(2, score))}%`,
            backgroundColor: barColor,
          }}
        />
      </div>
    </div>
  );
}
