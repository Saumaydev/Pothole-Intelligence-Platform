import React from 'react';
import {
  ComposedChart, Line, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, Legend, Area,
} from 'recharts';

const SpeedImpactChart = ({ speedAnalysis }) => {
  if (!speedAnalysis || !speedAnalysis.segments_speed) return null;

  const data = speedAnalysis.segments_speed.map((seg) => ({
    segment: `Seg ${seg.segment_index + 1}`,
    distance: `${seg.start_distance}m`,
    baseSpeed: seg.base_speed,
    predictedSpeed: seg.predicted_speed,
    speedReduction: seg.speed_reduction_pct,
    density: seg.pothole_density,
  }));

  return (
    <div className="chart-card chart-card-wide">
      <h4>🚗 Speed Impact Analysis Along Road</h4>
      <p className="chart-description">
        Shows how potholes reduce vehicle speed compared to normal driving conditions.
        Base speed: <strong>{speedAnalysis.base_speed} km/h</strong> →
        Average: <strong>{speedAnalysis.avg_predicted_speed} km/h</strong>
        ({speedAnalysis.speed_reduction_pct}% reduction)
      </p>
      <ResponsiveContainer width="100%" height={380}>
        <ComposedChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis dataKey="segment" stroke="#aaa" fontSize={11} angle={-30} textAnchor="end" />
          <YAxis yAxisId="speed" stroke="#aaa" fontSize={11} domain={[0, 'auto']}
            label={{ value: 'Speed (km/h)', angle: -90, position: 'insideLeft', style: { fill: '#aaa' } }} />
          <YAxis yAxisId="reduction" orientation="right" stroke="#aaa" fontSize={11} domain={[0, 100]}
            label={{ value: 'Reduction %', angle: 90, position: 'insideRight', style: { fill: '#aaa' } }} />

          <Tooltip contentStyle={{ background: '#1e1e2e', border: 'none', borderRadius: '8px', color: '#fff' }} />
          <Legend />

          <Area yAxisId="speed" type="monotone" dataKey="baseSpeed" fill="rgba(33,150,243,0.1)"
            stroke="#2196f3" strokeDasharray="5 5" name="Base Speed (km/h)" />
          <Line yAxisId="speed" type="monotone" dataKey="predictedSpeed" stroke="#ff9800"
            strokeWidth={3} dot={{ fill: '#ff9800', r: 5 }} name="Predicted Speed (km/h)" />
          <Bar yAxisId="reduction" dataKey="speedReduction" fill="rgba(244,67,54,0.5)"
            radius={[4, 4, 0, 0]} name="Speed Reduction %" />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SpeedImpactChart;