import React from 'react';
import { FaFileCsv, FaDownload } from 'react-icons/fa';
import { downloadCSV } from '../services/api';

const ReportDownload = ({ analysisId, roadName }) => {
  if (!analysisId) return null;

  const handleDownload = () => {
    const url = downloadCSV(analysisId);
    window.open(url, '_blank');
  };

  return (
    <div className="report-section">
      <div className="report-card">
        <FaFileCsv size={40} color="#4caf50" />
        <div>
          <h4>Download Full CSV Report</h4>
          <p>
            Get structured segment-level data for <strong>{roadName}</strong> including
            pothole density, severity, predicted speed, and risk classification.
          </p>
        </div>
        <button className="btn-download" onClick={handleDownload}>
          <FaDownload /> Download CSV
        </button>
      </div>
    </div>
  );
};

export default ReportDownload;