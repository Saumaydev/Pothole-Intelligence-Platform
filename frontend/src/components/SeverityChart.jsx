import React from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = {
  low: '#4caf50',
  medium: '#ff9800',
  high: '#f44336',
  critical: '#b71c1c',
};

const SeverityChart = ({ distribution }) => {
  if (!distribution) return null;

  const data = Object.entries(distribution)
    .filter(([_, count]) => count > 0)
    .map(([severity, count]) => ({
      name: severity.charAt(0).toUpperCase() + severity.slice(1),
      value: count,
      color: COLORS[severity],
    }));

  const total = data.reduce((s, d) => s + d.value, 0);

  const renderLabel = ({ name, value, percent }) =>
    `${name}: ${value} (${(percent * 100).toFixed(0)}%)`;

  return (
    <div className="chart-card">
      <h4>🎯 Pothole Severity Distribution</h4>
      <ResponsiveContainer width="100%" height={320}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={true}
            label={renderLabel}
            outerRadius={100}
            innerRadius={50}
            dataKey="value"
            stroke="rgba(255,255,255,0.3)"
            strokeWidth={2}
          >
            {data.map((entry, idx) => (
              <Cell key={idx} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ background: '#1e1e2e', border: 'none', borderRadius: '8px', color: '#fff' }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
      <p className="chart-footer">Total: {total} potholes detected</p>
    </div>
  );
};

export default SeverityChart;