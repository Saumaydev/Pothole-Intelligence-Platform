import Loader from './Loader';
import React from 'react';
import { motion } from 'framer-motion';

const steps = [
  { key: 'geocoding', label: 'Geocoding road name...' },
  { key: 'road_extraction', label: 'Extracting road geometry from OSM...' },
  { key: 'sampling', label: 'Sampling coordinate points...' },
  { key: 'image_acquisition', label: 'Acquiring street-level images...' },
  { key: 'detection', label: 'Running YOLOv8 pothole detection...' },
  { key: 'analysis', label: 'Aggregating results...' },
  { key: 'speed_prediction', label: 'Predicting speed impact...' },
  { key: 'saving', label: 'Saving to database...' },
];

const LoadingOverlay = ({ progress }) => {
  if (!progress || progress.status === 'completed') return null;

  const pct = progress.progress || 0;
  const currentStep = progress.step || 'geocoding';

  return (
    <motion.div
      className="loading-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className="loading-card">
        <Loader />
        <h3>Analyzing Road...</h3>
        <p className="loading-message">{progress.message}</p>

        <div className="progress-bar-container">
          <motion.div
            className="progress-bar-fill"
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ duration: 0.5 }}
          />
          <span className="progress-text">{pct}%</span>
        </div>

        <div className="step-list">
          {steps.map((step) => {
            const stepIdx = steps.findIndex((s) => s.key === step.key);
            const currentIdx = steps.findIndex((s) => s.key === currentStep);
            let status = 'pending';
            if (stepIdx < currentIdx) status = 'done';
            else if (stepIdx === currentIdx) status = 'active';

            return (
              <div key={step.key} className={`step-item step-${status}`}>
                <span className="step-indicator">
                  {status === 'done' ? '✓' : status === 'active' ? '⟳' : '○'}
                </span>
                <span>{step.label}</span>
              </div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
};

export default LoadingOverlay;
