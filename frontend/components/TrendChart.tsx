'use client';

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { TrendPoint } from '@/lib/types';

interface TrendChartProps {
  trendData: TrendPoint[];
}

export function TrendChart({ trendData }: TrendChartProps) {
  // Format data for chart display
  const chartData = trendData.map((d) => ({
    label: `${d.year} ${d.festival[0]} (${d.phase})`,
    fullName: `${d.year} ${d.festival} (${d.phase})`,
    DO: d.do_value !== null ? Number(d.do_value.toFixed(2)) : null,
    BOD: d.bod_value !== null ? Number(d.bod_value.toFixed(2)) : null,
    pH: d.ph_value !== null ? Number(d.ph_value.toFixed(2)) : null,
  }));

  return (
    <div className="bg-white border border-[#DCE4E7] rounded-xl p-5 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div>
          <h3 className="text-base font-bold text-[#12262D]">
            Multi-Year Water Quality Trajectory (2023–2025)
          </h3>
          <p className="text-xs text-[#5B6B73]">
            Pre, During, and After idol immersion phases plotted against CPCB Class B bathing limits.
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <span className="flex items-center gap-1 font-semibold text-[#0B4F5C]">
            <span className="w-2.5 h-2.5 rounded-full bg-[#0B4F5C]" /> DO (Min limit: 5 mg/l)
          </span>
          <span className="flex items-center gap-1 font-semibold text-[#B83A32]">
            <span className="w-2.5 h-2.5 rounded-full bg-[#B83A32]" /> BOD (Max limit: 3 mg/l)
          </span>
        </div>
      </div>

      <div className="w-full h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 10, right: 20, left: -10, bottom: 25 }}
            aria-label="Multi-year water quality trend line chart showing Dissolved Oxygen and BOD values"
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis
              dataKey="label"
              tick={{ fontSize: 11, fill: '#5B6B73' }}
              interval={0}
              angle={-25}
              textAnchor="end"
            />
            <YAxis
              tick={{ fontSize: 11, fill: '#5B6B73' }}
              domain={[0, 'auto']}
              unit=" mg/l"
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-white border border-[#DCE4E7] p-3 rounded-lg shadow-md text-xs">
                      <p className="font-bold text-[#12262D] mb-1.5">{data.fullName}</p>
                      <div className="space-y-1">
                        <p className="text-[#0B4F5C] font-semibold">
                          DO: {data.DO !== null ? `${data.DO} mg/l` : 'Not recorded'}
                          {data.DO !== null && (
                            <span className={data.DO >= 5 ? ' text-[#3C8D6E] ml-1' : ' text-[#B83A32] ml-1 font-bold'}>
                              ({data.DO >= 5 ? 'Pass' : 'Fail < 5.0'})
                            </span>
                          )}
                        </p>
                        <p className="text-[#B83A32] font-semibold">
                          BOD: {data.BOD !== null ? `${data.BOD} mg/l` : 'Not recorded'}
                          {data.BOD !== null && (
                            <span className={data.BOD <= 3 ? ' text-[#3C8D6E] ml-1' : ' text-[#B83A32] ml-1 font-bold'}>
                              ({data.BOD <= 3 ? 'Pass' : 'Fail > 3.0'})
                            </span>
                          )}
                        </p>
                        {data.pH !== null && (
                          <p className="text-[#5B6B73]">
                            pH: {data.pH} ({data.pH >= 6.5 && data.pH <= 8.5 ? 'Pass' : 'Fail'})
                          </p>
                        )}
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            {/* CPCB Class B Reference Lines */}
            <ReferenceLine
              y={5.0}
              stroke="#0B4F5C"
              strokeDasharray="4 4"
              label={{ value: 'DO Limit (5.0)', position: 'insideTopRight', fill: '#0B4F5C', fontSize: 10 }}
            />
            <ReferenceLine
              y={3.0}
              stroke="#B83A32"
              strokeDasharray="4 4"
              label={{ value: 'BOD Limit (3.0)', position: 'insideBottomRight', fill: '#B83A32', fontSize: 10 }}
            />

            <Line
              type="monotone"
              dataKey="DO"
              stroke="#0B4F5C"
              strokeWidth={2.5}
              dot={{ r: 4, fill: '#0B4F5C' }}
              activeDot={{ r: 6 }}
              connectNulls={false}
              name="Dissolved Oxygen"
            />
            <Line
              type="monotone"
              dataKey="BOD"
              stroke="#B83A32"
              strokeWidth={2.5}
              dot={{ r: 4, fill: '#B83A32' }}
              activeDot={{ r: 6 }}
              connectNulls={false}
              name="BOD"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
