import Link from 'next/link';
import { notFound } from 'next/navigation';
import {
  ArrowLeft,
  AlertTriangle,
  FileText,
  Calendar,
  CheckCircle2,
  XCircle,
  ExternalLink,
  Info,
} from 'lucide-react';
import { fetchGhatDetail, getReportPdfUrl } from '@/lib/api';
import { ConfidenceBadge } from '@/components/ConfidenceBadge';
import { RiskBar } from '@/components/RiskBar';
import { MissingCell } from '@/components/MissingCell';
import { TrendChart } from '@/components/TrendChart';
import { EvidenceTable } from '@/components/EvidenceTable';

interface GhatPageProps {
  params: Promise<{ id: string }>;
}

export default async function GhatDetailPage({ params }: GhatPageProps) {
  const { id } = await params;

  let ghat;
  try {
    ghat = await fetchGhatDetail(id);
  } catch (error) {
    notFound();
  }

  // Split parameters into scored vs unscored
  const scoredParams = ghat.parameters.filter((p) => p.is_scored);
  const unscoredParams = ghat.parameters.filter((p) => !p.is_scored);

  return (
    <div className="space-y-6">
      {/* Top Back Navigation */}
      <div>
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-xs font-bold text-[#0B4F5C] hover:text-[#1F8A8A] transition-colors bg-white px-3 py-1.5 rounded-lg border border-[#DCE4E7] shadow-2xs"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to All 7 Ghats</span>
        </Link>
      </div>

      {/* Ghat Profile Header Banner */}
      <div className="bg-white border border-[#DCE4E7] rounded-xl p-6 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <span
              className={`w-12 h-12 rounded-xl flex items-center justify-center font-extrabold text-lg shrink-0 shadow-sm ${
                ghat.rank === 1
                  ? 'bg-[#B83A32] text-white'
                  : ghat.rank === 2
                  ? 'bg-[#D98A1F] text-white'
                  : 'bg-[#0B4F5C] text-white'
              }`}
            >
              #{ghat.rank}
            </span>
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <span className="text-xs font-bold uppercase tracking-wider text-[#0B4F5C] bg-[#EBF3F5] px-2 py-0.5 rounded">
                  {ghat.water_body}
                </span>
                <span className="text-xs text-[#5B6B73]">
                  ID: <code className="text-[#12262D]">{ghat.id}</code>
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-[#12262D] tracking-tight">
                {ghat.name}
              </h1>
              <p className="text-xs text-[#5B6B73] mt-1">
                Historical water quality evaluation across 2023–2025 Ganesh &amp; Durga visarjan monitoring cycles.
              </p>
            </div>
          </div>

          <div className="shrink-0 flex flex-col items-end gap-2">
            <ConfidenceBadge
              confidence={ghat.confidence}
              coveragePct={ghat.coverage_pct}
            />
            {ghat.missing_share_pct > 0 && (
              <span className="text-[11px] text-[#5B6B73]">
                {ghat.missing_share_pct}% readings missing / unrecorded
              </span>
            )}
          </div>
        </div>

        {/* Risk Score Progress Bar */}
        <div className="mt-6 pt-5 border-t border-[#E2E8F0]">
          <RiskBar score={ghat.risk_score} tier={ghat.risk_tier} />
        </div>

        {/* Plain Language Rationale List */}
        <div className="mt-5 space-y-2">
          <h2 className="text-xs font-bold text-[#0B4F5C] uppercase tracking-wide">
            Key Observational Findings (Traceable to MPPCB Reports)
          </h2>
          <div className="space-y-1.5">
            {ghat.reasons.map((reason, idx) => (
              <div
                key={idx}
                className="bg-[#F8FAFC] border border-[#E2E8F0] p-3 rounded-lg text-xs text-[#12262D] flex items-start gap-2"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-[#0B4F5C] mt-1.5 shrink-0" />
                <span className="leading-relaxed">{reason}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Component Points Breakdown */}
      <div className="bg-white border border-[#DCE4E7] rounded-xl p-5 shadow-xs">
        <h2 className="text-sm font-bold text-[#12262D] mb-3 flex items-center justify-between">
          <span>Risk Score Component Contributions</span>
          <span className="text-xs text-[#5B6B73] font-normal">Weights normalized to 100</span>
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 text-xs">
          <div className="bg-[#F8FAFC] p-3 rounded-lg border border-[#E2E8F0]">
            <span className="text-[#5B6B73] block">DO Fail Rate</span>
            <strong className="text-sm text-[#0B4F5C] font-extrabold">
              {ghat.component_scores.do_failure_rate?.toFixed(1) || '0.0'}
            </strong>
            <span className="text-[10px] text-[#5B6B73] block mt-0.5">Max: 35.0 pts</span>
          </div>
          <div className="bg-[#F8FAFC] p-3 rounded-lg border border-[#E2E8F0]">
            <span className="text-[#5B6B73] block">BOD Fail Rate</span>
            <strong className="text-sm text-[#B83A32] font-extrabold">
              {ghat.component_scores.bod_failure_rate?.toFixed(1) || '0.0'}
            </strong>
            <span className="text-[10px] text-[#5B6B73] block mt-0.5">Max: 25.0 pts</span>
          </div>
          <div className="bg-[#F8FAFC] p-3 rounded-lg border border-[#E2E8F0]">
            <span className="text-[#5B6B73] block">Worst Severity</span>
            <strong className="text-sm text-[#D98A1F] font-extrabold">
              {ghat.component_scores.worst_severity?.toFixed(1) || '0.0'}
            </strong>
            <span className="text-[10px] text-[#5B6B73] block mt-0.5">Max: 10.0 pts</span>
          </div>
          <div className="bg-[#F8FAFC] p-3 rounded-lg border border-[#E2E8F0]">
            <span className="text-[#5B6B73] block">pH Fail Rate</span>
            <strong className="text-sm text-[#12262D] font-extrabold">
              {ghat.component_scores.ph_failure_rate?.toFixed(1) || '0.0'}
            </strong>
            <span className="text-[10px] text-[#5B6B73] block mt-0.5">Max: 5.0 pts</span>
          </div>
          <div className="bg-[#F8FAFC] p-3 rounded-lg border border-[#E2E8F0]">
            <span className="text-[#5B6B73] block">Immersion Impact</span>
            <strong className="text-sm text-[#1F8A8A] font-extrabold">
              {ghat.component_scores.immersion_impact?.toFixed(1) || '0.0'}
            </strong>
            <span className="text-[10px] text-[#5B6B73] block mt-0.5">Max: 15.0 pts</span>
          </div>
          <div className="bg-[#F8FAFC] p-3 rounded-lg border border-[#E2E8F0]">
            <span className="text-[#5B6B73] block">No Recovery</span>
            <strong className="text-sm text-[#B83A32] font-extrabold">
              {ghat.component_scores.no_recovery?.toFixed(1) || '0.0'}
            </strong>
            <span className="text-[10px] text-[#5B6B73] block mt-0.5">Max: 10.0 pts</span>
          </div>
        </div>
      </div>

      {/* Scored Parameters vs CPCB Class B Standard */}
      <div className="bg-white border border-[#DCE4E7] rounded-xl p-5 shadow-xs">
        <div className="mb-4">
          <h2 className="text-base font-bold text-[#12262D]">
            CPCB Class B Scored Parameters (Outdoor Bathing Standard)
          </h2>
          <p className="text-xs text-[#5B6B73]">
            Direct comparison of legal bathing thresholds against aggregated test results.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-[#EBF3F5] border-b border-[#DCE4E7] text-[#0B4F5C] font-bold uppercase tracking-wider">
                <th className="py-2.5 px-3">Parameter</th>
                <th className="py-2.5 px-3">Class B Legal Limit</th>
                <th className="py-2.5 px-3">Valid Tests</th>
                <th className="py-2.5 px-3">Pass / Fail</th>
                <th className="py-2.5 px-3">Missing</th>
                <th className="py-2.5 px-3">Worst Recorded</th>
                <th className="py-2.5 px-3 text-right">PDF Citation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E8F0]">
              {scoredParams.map((param, idx) => (
                <tr key={idx} className="hover:bg-[#F8FAFC]">
                  <td className="py-3 px-3 font-bold text-[#12262D]">{param.parameter}</td>
                  <td className="py-3 px-3 font-semibold text-[#0B4F5C]">{param.cpcb_limit}</td>
                  <td className="py-3 px-3">{param.valid_readings} of {param.total_readings}</td>
                  <td className="py-3 px-3">
                    <span className="inline-flex items-center gap-1.5 font-semibold">
                      <span className="text-[#3C8D6E]">{param.pass_count} Pass</span>
                      <span className="text-[#5B6B73]">/</span>
                      <span className={param.fail_count > 0 ? 'text-[#B83A32] font-bold' : 'text-[#5B6B73]'}>
                        {param.fail_count} Fail ({param.fail_rate_pct}%)
                      </span>
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    {param.missing_count > 0 ? (
                      <MissingCell label={`${param.missing_count} missing`} />
                    ) : (
                      <span className="text-[#3C8D6E] font-medium">None</span>
                    )}
                  </td>
                  <td className="py-3 px-3 font-mono font-bold text-[#12262D]">
                    {param.worst_reading_display}
                  </td>
                  <td className="py-3 px-3 text-right">
                    {param.worst_source_page ? (
                      <span className="text-[#0B4F5C] font-semibold">
                        p.{param.worst_source_page} ({param.worst_year})
                      </span>
                    ) : (
                      <span className="text-[#94A3A8]">N/A</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Multi-Year Trend Chart */}
      <TrendChart trendData={ghat.trend} />

      {/* Unscored Parameters Reference (Metals, COD, Solids) */}
      <div className="bg-white border border-[#DCE4E7] rounded-xl p-5 shadow-xs">
        <div className="mb-3">
          <h2 className="text-sm font-bold text-[#12262D]">
            Unscored Parameters Reference (Displayed for Full Disclosure)
          </h2>
          <p className="text-xs text-[#5B6B73]">
            Heavy metals (Cr, Pb, Zn, Cu), COD, conductivity, and solids are reported in MPPCB tables but have no Class B limits set and are not scored.
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 text-xs">
          {unscoredParams.map((p, idx) => (
            <div key={idx} className="bg-[#F8FAFC] p-3 rounded-lg border border-[#E2E8F0]">
              <span className="font-semibold text-[#12262D] block truncate">{p.parameter}</span>
              <span className="text-[#5B6B73] text-[11px] block mt-0.5">
                Mean: {p.mean_value !== null ? `${p.mean_value} ${p.unit}` : 'BDL/None'}
              </span>
              <span className="text-[10px] text-[#5B6B73] block mt-0.5">
                Max: {p.max_value !== null ? `${p.max_value} ${p.unit}` : 'BDL'}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Full Audit Trail Evidence Table */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-[#12262D]">
              Complete Historical Readings &amp; Evidence Audit Trail
            </h2>
            <p className="text-xs text-[#5B6B73]">
              Every reading links directly to its source PDF page in the official MPPCB reports.
            </p>
          </div>
          <span className="text-xs font-semibold text-[#0B4F5C] bg-[#EBF3F5] px-2.5 py-1 rounded">
            {ghat.evidence.length} Total Records
          </span>
        </div>

        <EvidenceTable records={ghat.evidence} />
      </div>

      {/* Caveats and Transparency Notes */}
      <div className="bg-[#FFFBEB] border border-[#FDE68A] rounded-xl p-5 text-xs text-[#92400E] space-y-2">
        <div className="flex items-center gap-2 font-bold text-sm text-[#B45309]">
          <AlertTriangle className="w-4 h-4" />
          <span>Site Transparency &amp; Data Caveats</span>
        </div>
        <ul className="list-disc list-inside space-y-1">
          {ghat.caveats.map((cav, idx) => (
            <li key={idx} className="leading-relaxed">
              {cav}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
