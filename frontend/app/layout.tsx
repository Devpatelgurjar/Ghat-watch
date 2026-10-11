import type { Metadata } from 'next';
import { Inter, Noto_Sans_Devanagari } from 'next/font/google';
import Link from 'next/link';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const notoDevanagari = Noto_Sans_Devanagari({
  subsets: ['devanagari'],
  variable: '--font-devanagari',
  weight: ['400', '500', '600', '700'],
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'Ghat Watch | BMC Visarjan Planning Support',
  description: 'Water quality risk decision-support tool ranking Bhopal immersion ghats for Durga Visarjan 2026 based on MPPCB testing data.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${notoDevanagari.variable}`}>
      <body className="min-h-screen flex flex-col bg-[#F5F8F9] text-[#12262D]">
        {/* Navigation Bar */}
        <header className="bg-[#0B4F5C] text-white border-b border-[#07353E] no-print sticky top-0 z-50 shadow-sm">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link href="/" className="flex items-center gap-2 group">
                <div className="w-8 h-8 rounded bg-[#1F8A8A] flex items-center justify-center font-bold text-white shadow-inner">
                  GW
                </div>
                <div>
                  <div className="text-lg font-bold tracking-tight group-hover:text-teal-200 transition-colors">
                    Ghat Watch
                  </div>
                  <div className="text-xs text-teal-200 font-medium">
                    Bhopal Municipal Corporation · Visarjan 2026
                  </div>
                </div>
              </Link>
            </div>

            <nav className="flex items-center gap-4 text-sm font-medium">
              <Link
                href="/"
                className="px-3 py-1.5 rounded hover:bg-white/10 transition-colors"
              >
                Ghat Rankings
              </Link>
              <Link
                href="/brief"
                className="px-3 py-1.5 rounded bg-[#1F8A8A] hover:bg-[#187272] transition-colors text-white font-semibold flex items-center gap-1.5 shadow-sm"
              >
                <span>Decision Brief</span>
                <span className="text-xs px-1.5 py-0.5 rounded bg-black/20 font-normal">EN / हिन्दी</span>
              </Link>
            </nav>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-6">
          {children}
        </main>

        {/* Civic Tech Footer */}
        <footer className="bg-white border-t border-[#DCE4E7] py-6 text-sm text-[#5B6B73] no-print mt-auto">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
            <div>
              <p className="font-medium text-[#12262D]">
                Ghat Watch · Decision-support for Durga Visarjan (20 Oct 2026)
              </p>
              <p className="text-xs text-[#5B6B73] mt-0.5">
                Evaluates historical MPPCB test reports (2023–2025) vs CPCB Class B bathing standards.
              </p>
            </div>
            <div className="text-xs text-[#5B6B73]">
              Track 2: Claude Impact Lab × Cerebras Café Compute, Bhopal
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
