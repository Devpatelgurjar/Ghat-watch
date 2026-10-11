import React from 'react';
import { ExternalLink, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { ReadingRecord } from '@/lib/types';
import { getReportPdfUrl } from '@/lib/api';
import { MissingCell } from './MissingCell';

interface EvidenceTableProps {
  records: ReadingRecord[];
}

export function EvidenceTable({ records }: EvidenceTableProps) {
  return (
    <div className="overflow-x-auto border border-[#DCE4E7] rounded-xl bg-white shadow-xs">
      <table className="w-full text-left text-sm border-collapse">
        <thead>
          <tr className="bg-[#EBF3F5] border-b border-[#DCE4E7] text-xs font-bold text-[#0B4F5C] uppercase tracking-wider">
            <th className="py-3 px-3">Year</th>
            <th className="py-3 px-3">Festival</th>
            <th className="py-3 px-3">Phase</th>
            <th className="py-3 px-3">Parameter</th>
            <th className="py-3 px-3">Value</th>
            <th className="py-3 px-3">Status</th>
            <th className="py-3 px-3">Evaluation</th>
            <th className="py-3 px-3 text-right">PDF Source</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[#E2E8F0] text-xs">
          {records.map((r, idx) => {
            const pdfUrl = r.source_page && r.source_page !== 'unknown'
              ? getReportPdfUrl(r.report_file, r.source_page)
              : null;

            return (
              <tr key={idx} className="hover:bg-[#F8FAFC] transition-colors">
                <td className="py-2.5 px-3 font-semibold text-[#12262D]">{r.year}</td>
                <td className="py-2.5 px-3 text-[#5B6B73]">{r.festival}</td>
                <td className="py-2.5 px-3 font-medium capitalize text-[#12262D]">{r.phase}</td>
                <td className="py-2.5 px-3 font-medium text-[#12262D]">{r.parameter}</td>
                <td className="py-2.5 px-3 font-mono">
                  {r.status === 'numeric' && r.value !== null ? (
                    <span className="font-semibold text-[#12262D]">
                      {r.value} {r.unit_assumed}
                    </span>
                  ) : r.status === 'below_detection' ? (
                    <span className="font-bold text-[#1F8A8A]" title="Below Detection Limit">
                      BDL ({r.unit_assumed || 'mg/l'})
                    </span>
                  ) : (
                    <MissingCell isNoTable={r.status === 'no_table'} />
                  )}
                </td>
                <td className="py-2.5 px-3 capitalize text-[#5B6B73]">
                  {r.status.replace('_', ' ')}
                </td>
                <td className="py-2.5 px-3">
                  {r.evaluation === 'pass' ? (
                    <span className="inline-flex items-center gap-1 text-[#3C8D6E] font-bold">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Pass
                    </span>
                  ) : r.evaluation === 'fail' ? (
                    <span className="inline-flex items-center gap-1 text-[#B83A32] font-bold">
                      <XCircle className="w-3.5 h-3.5" /> Fail
                      {r.is_ambiguous && (
                        <span className="text-[10px] bg-red-100 text-red-700 px-1 rounded ml-1">
                          ambiguous
                        </span>
                      )}
                    </span>
                  ) : r.evaluation === 'not_scored' ? (
                    <span className="text-[#5B6B73] font-medium">Unscored</span>
                  ) : (
                    <MissingCell isNoTable={r.status === 'no_table'} />
                  )}
                </td>
                <td className="py-2.5 px-3 text-right">
                  {pdfUrl ? (
                    <a
                      href={pdfUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-[#0B4F5C] hover:text-[#1F8A8A] font-semibold underline underline-offset-2"
                      title={`Open official MPPCB ${r.year} PDF on page ${r.source_page}`}
                    >
                      <span>p.{r.source_page}</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  ) : (
                    <span className="text-[#94A3A8] italic">No page</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
