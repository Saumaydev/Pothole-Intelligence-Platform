import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, Cell, ReferenceLine
} from 'recharts';

const DensityChart = ({ densityData, avgDensity }) => {
  if (!densityData || densityData.length === 0) return null;

  const data = densityData.map((d) => ({
    segment: `Seg ${d.segment_index + 1}`,
    density: d.density,
    distance: `${d.distance}m`,
  }));

  const getColor = (density) => {
    if (density < 3) return '#4caf50';
    if (density < 6) return '#ff9800';
    if (density < 10) return '#f44336';
    return '#b71c1c';
  };

  return (
    <div className="chart-card">
      <h4>📊 Pothole Density per Segment (potholes/km)</h4>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis dataKey="segment" stroke="#aaa" fontSize={11} angle={-30} textAnchor="end" />
          <YAxis stroke="#aaa" fontSize={11} label={{ value: 'Potholes/km', angle: -90, position: 'insideLeft', style: { fill: '#aaa' } }} />
          <Tooltip
            contentStyle={{ background: '#1e1e2e', border: 'none', borderRadius: '8px', color: '#fff' }}
            formatter={(value) => [`${value} potholes/km`, 'Density']}
          />
          <ReferenceLine y={avgDensity} stroke="#ff9800" strokeDasharray="5 5" label={{ value: `Avg: ${avgDensity}`, fill: '#ff9800', fontSize: 11 }} />
          <Bar dataKey="density" radius={[4, 4, 0, 0]}>
            {data.map((entry, idx) => (
              <Cell key={idx} fill={getColor(entry.density)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default DensityChart;