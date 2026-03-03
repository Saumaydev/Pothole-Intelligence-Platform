import React from 'react';

const SegmentTable = ({ segments }) => {
  if (!segments || segments.length === 0) return null;

  const riskColors = {
    safe: '#4caf50',
    moderate: '#ff9800',
    dangerous: '#f44336',
    critical: '#b71c1c',
  };

  return (
    <div className="chart-card chart-card-wide">
      <h4>📋 Segment-wise Detailed Analysis</h4>
      <div className="table-scroll">
        <table className="segment-table">
          <thead>
            <tr>
              <th>Segment</th>
              <th>Length (m)</th>
              <th>Potholes</th>
              <th>Density (/km)</th>
              <th>Avg Confidence</th>
              <th>Severity</th>
              <th>Risk Level</th>
              <th>Speed (km/h)</th>
              <th>Speed Reduction</th>
            </tr>
          </thead>
          <tbody>
            {segments.map((seg, i) => (
              <tr key={i}>
                <td>#{seg.segment_index + 1}</td>
                <td>{seg.length_meters?.toFixed(0)}</td>
                <td><strong>{seg.pothole_count}</strong></td>
                <td>{seg.pothole_density?.toFixed(1)}</td>
                <td>{(seg.avg_confidence * 100).toFixed(1)}%</td>
                <td>{seg.avg_severity?.toFixed(2)}</td>
                <td>
                  <span
                    className="risk-badge"
                    style={{ backgroundColor: riskColors[seg.risk_level] || '#666' }}
                  >
                    {seg.risk_level?.toUpperCase()}
                  </span>
                </td>
                <td><strong>{seg.predicted_speed?.toFixed(1)}</strong></td>
                <td style={{ color: seg.speed_reduction > 20 ? '#f44336' : '#ff9800' }}>
                  -{seg.speed_reduction?.toFixed(1)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SegmentTable;