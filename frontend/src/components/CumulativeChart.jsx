import React from 'react';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from 'recharts';

const CumulativeChart = ({ cumulativeData }) => {
  if (!cumulativeData || cumulativeData.length === 0) return null;

  const data = cumulativeData.map((d) => ({
    segment: `Seg ${d.segment_index + 1}`,
    distance: d.distance,
    count: d.cumulative_count,
  }));

  return (
    <div className="chart-card">
      <h4>📈 Cumulative Pothole Count Along Road</h4>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis dataKey="segment" stroke="#aaa" fontSize={11} />
          <YAxis stroke="#aaa" fontSize={11} />
          <Tooltip
            contentStyle={{ background: '#1e1e2e', border: 'none', borderRadius: '8px', color: '#fff' }}
            formatter={(value) => [`${value} potholes`, 'Cumulative']}
          />
          <defs>
            <linearGradient id="cumGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ff5722" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#ff5722" stopOpacity={0.05} />
            </linearGradient>
          </defs>
          <Area
            type="monotone" dataKey="count" stroke="#ff5722"
            strokeWidth={2} fill="url(#cumGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CumulativeChart;