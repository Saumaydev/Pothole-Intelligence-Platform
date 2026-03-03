import React from 'react';

const SpeedGauge = ({ speedAnalysis }) => {
  if (!speedAnalysis) return null;

  const { base_speed, avg_predicted_speed, speed_reduction_pct } = speedAnalysis;
  const percentage = (avg_predicted_speed / base_speed) * 100;
  const angle = (percentage / 100) * 180 - 90; // -90 to 90 degrees

  const getColor = () => {
    if (speed_reduction_pct < 10) return '#4caf50';
    if (speed_reduction_pct < 25) return '#ff9800';
    if (speed_reduction_pct < 45) return '#f44336';
    return '#b71c1c';
  };

  return (
    <div className="chart-card gauge-card">
      <h4>⏱️ Speed Impact Gauge</h4>
      <div className="gauge-container">
        <svg viewBox="0 0 200 120" className="gauge-svg">
          {/* Background arc */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="14"
            strokeLinecap="round"
          />
          {/* Colored arc */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none" stroke={getColor()} strokeWidth="14"
            strokeLinecap="round"
            strokeDasharray={`${percentage * 2.51} 251`}
          />
          {/* Needle */}
          <line
            x1="100" y1="100" x2="100" y2="30"
            stroke="#fff" strokeWidth="2"
            transform={`rotate(${angle}, 100, 100)`}
          />
          <circle cx="100" cy="100" r="5" fill="#fff" />
          {/* Labels */}
          <text x="15" y="115" fill="#aaa" fontSize="10">0</text>
          <text x="90" y="50" fill="#fff" fontSize="14" fontWeight="bold" textAnchor="middle">
            {avg_predicted_speed}
          </text>
          <text x="90" y="65" fill="#aaa" fontSize="9" textAnchor="middle">km/h</text>
          <text x="175" y="115" fill="#aaa" fontSize="10">{base_speed}</text>
        </svg>
        <div className="gauge-info">
          <span style={{ color: getColor(), fontSize: '20px', fontWeight: 'bold' }}>
            -{speed_reduction_pct}%
          </span>
          <span style={{ color: '#aaa', fontSize: '12px' }}>speed reduction</span>
        </div>
      </div>
    </div>
  );
};

export default SpeedGauge;