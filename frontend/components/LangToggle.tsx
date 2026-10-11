'use client';

import React from 'react';

interface LangToggleProps {
  currentLang: 'en' | 'hi';
  onToggle: (lang: 'en' | 'hi') => void;
}

export function LangToggle({ currentLang, onToggle }: LangToggleProps) {
  return (
    <div className="inline-flex items-center rounded-lg bg-[#E2E8F0] p-1 border border-[#DCE4E7] shadow-2xs">
      <button
        id="lang-toggle-en"
        type="button"
        onClick={() => onToggle('en')}
        className={`px-3 py-1 text-xs font-bold rounded-md transition-all cursor-pointer ${
          currentLang === 'en'
            ? 'bg-[#0B4F5C] text-white shadow-xs'
            : 'text-[#12262D] hover:text-[#0B4F5C]'
        }`}
        aria-pressed={currentLang === 'en'}
      >
        English
      </button>
      <button
        id="lang-toggle-hi"
        type="button"
        onClick={() => onToggle('hi')}
        className={`px-3 py-1 text-xs font-bold rounded-md font-['Noto_Sans_Devanagari'] transition-all cursor-pointer ${
          currentLang === 'hi'
            ? 'bg-[#0B4F5C] text-white shadow-xs'
            : 'text-[#12262D] hover:text-[#0B4F5C]'
        }`}
        aria-pressed={currentLang === 'hi'}
      >
        हिन्दी
      </button>
    </div>
  );
}
