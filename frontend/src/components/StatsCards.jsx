import React from 'react';
import { FaExclamationTriangle, FaRoad, FaTachometerAlt, FaClock } from 'react-icons/fa';

const StatsCards = ({ data }) => {
  if (!data) return null;

  const speed = data.speed_analysis || {};

  const riskColors = {
    safe: '#4caf50',
    moderate: '#ff9800',
    dangerous: '#f44336',
    critical: '#b71c1c',
  };

  const cards = [
    {
      icon: <FaExclamationTriangle />,
      title: 'Total Potholes',
      value: data.total_potholes_detected,
      subtitle: `${data.avg_pothole_density} per km avg`,
      color: '#ff5722',
    },
    {
      icon: <FaRoad />,
      title: 'Road Length',
      value: `${data.road_length_km} km`,
      subtitle: `${data.total_points_sampled} points sampled`,
      color: '#2196f3',
    },
    {
      icon: <FaTachometerAlt />,
      title: 'Avg Predicted Speed',
      value: `${speed.avg_predicted_speed || 0} km/h`,
      subtitle: `${speed.speed_reduction_pct || 0}% reduction from ${speed.base_speed || 0} km/h`,
      color: '#ff9800',
    },
    {
      icon: <FaClock />,
      title: 'Time Delay',
      value: `+${speed.time_delay_min || 0} min`,
      subtitle: `Actual: ${speed.actual_travel_time_min || 0} vs Normal: ${speed.normal_travel_time_min || 0} min`,
      color: '#9c27b0',
    },
    {
      icon: <FaExclamationTriangle />,
      title: 'Risk Level',
      value: (data.overall_risk_level || 'safe').toUpperCase(),
      subtitle: `Max density: ${data.max_pothole_density} per km`,
      color: riskColors[data.overall_risk_level] || '#4caf50',
    },
    {
      icon: <FaTachometerAlt />,
      title: 'Min Speed Zone',
      value: `${speed.min_predicted_speed || 0} km/h`,
      subtitle: 'Worst segment predicted speed',
      color: '#f44336',
    },
  ];

  return (
    <div className="stats-grid">
      {cards.map((card, i) => (
        <div key={i} className="stat-card" style={{ borderLeftColor: card.color }}>
          <div className="stat-icon" style={{ color: card.color }}>
            {card.icon}
          </div>
          <div className="stat-info">
            <span className="stat-title">{card.title}</span>
            <span className="stat-value">{card.value}</span>
            <span className="stat-subtitle">{card.subtitle}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default StatsCards;