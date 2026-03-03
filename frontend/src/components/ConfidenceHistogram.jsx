import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, Cell,
} from 'recharts';

const ConfidenceHistogram = ({ confidenceScores }) => {
  if (!confidenceScores || confidenceScores.length === 0) return null;

  // Create histogram bins
  const bins = [
    { range: '25-35%', min: 0.25, max: 0.35, count: 0, color: '#90caf9' },
    { range: '35-50%', min: 0.35, max: 0.50, count: 0, color: '#42a5f5' },
    { range: '50-65%', min: 0.50, max: 0.65, count: 0, color: '#1e88e5' },
    { range: '65-80%', min: 0.65, max: 0.80, count: 0, color: '#1565c0' },
    { range: '80-95%', min: 0.80, max: 0.95, count: 0, color: '#0d47a1' },
    { range: '95-100%', min: 0.95, max: 1.01, count: 0, color: '#002171' },
  ];

  confidenceScores.forEach((score) => {
    const bin = bins.find((b) => score >= b.min && score < b.max);
    if (bin) bin.count++;
  });

  const data = bins.filter((b) => b.count > 0);

  return (
    <div className="chart-card">
      <h4>🎯 Detection Confidence Distribution</h4>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis dataKey="range" stroke="#aaa" fontSize={11} />
          <YAxis stroke="#aaa" fontSize={11} />
          <Tooltip
            contentStyle={{ background: '#1e1e2e', border: 'none', borderRadius: '8px', color: '#fff' }}
          />
          <Bar dataKey="count" name="Detections" radius={[4, 4, 0, 0]}>
            {data.map((entry, idx) => (
              <Cell key={idx} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ConfidenceHistogram;