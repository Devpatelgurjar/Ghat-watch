import React from 'react';

interface MissingCellProps {
  label?: string;
  isNoTable?: boolean;
}

export function MissingCell({ label = 'Missing', isNoTable = false }: MissingCellProps) {
  const text = isNoTable ? 'No Table' : label;
  return (
    <div
      className="hatch-pattern text-[#5B6B73] px-2.5 py-1.5 rounded border border-[#DCE4E7] text-xs font-semibold inline-flex items-center gap-1.5 shadow-2xs"
      title={isNoTable ? 'Omitted in official report table' : 'Not sampled or missing reading'}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-[#94A3A8]" aria-hidden="true" />
      <span>{text}</span>
    </div>
  );
}
