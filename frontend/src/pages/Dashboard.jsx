import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-toastify';
import SearchBar from '../components/SearchBar';
import LoadingOverlay from '../components/LoadingOverlay';
import StatsCards from '../components/StatsCards';
import MapView from '../components/MapView';
import SeverityChart from '../components/SeverityChart';
import DensityChart from '../components/DensityChart';
import SpeedImpactChart from '../components/SpeedImpactChart';
import SpeedGauge from '../components/SpeedGauge';
import CumulativeChart from '../components/CumulativeChart';
import ConfidenceHistogram from '../components/ConfidenceHistogram';
import SegmentTable from '../components/SegmentTable';
import ReportDownload from '../components/ReportDownload';
import { startAnalysis, getProgress, getResult } from '../services/api';

const Dashboard = () => {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [analysisId, setAnalysisId] = useState(null);

  const pollProgress = useCallback(async (id) => {
    try {
      const prog = await getProgress(id);
      setProgress(prog);

      if (prog.status === 'completed' || prog.progress >= 100) {
        // Fetch final result
        const result = await getResult(id);
        setAnalysisData(result);
        setLoading(false);
        setProgress(null);
        toast.success(
          `✅ Analysis complete! Found ${result.total_potholes_detected} potholes.`
        );
      } else if (prog.status === 'failed') {
        setLoading(false);
        setProgress(null);
        toast.error(`❌ Analysis failed: ${prog.message}`);
      } else {
        // Continue polling
        setTimeout(() => pollProgress(id), 2000);
      }
    } catch (err) {
      // Result might not be ready yet
      setTimeout(() => pollProgress(id), 3000);
    }
  }, []);

  const handleSubmit = async (formData) => {
    setLoading(true);
    setAnalysisData(null);
    setProgress({ status: 'processing', step: 'geocoding', progress: 0, message: 'Starting...' });

    try {
      const response = await startAnalysis(formData);
      setAnalysisId(response.analysis_id);
      toast.info(`🔍 Analysis started for "${formData.road_name}"`);
      pollProgress(response.analysis_id);
    } catch (err) {
      setLoading(false);
      setProgress(null);
      const msg = err.response?.data?.detail || err.message;
      toast.error(`Failed to start analysis: ${msg}`);
    }
  };

  return (
    <div className="dashboard">
      <SearchBar onSubmit={handleSubmit} loading={loading} />

      {loading && <LoadingOverlay progress={progress} />}

      {analysisData && (
        <div className="results-section">
          <div className="results-header">
            <h2>
              📊 Analysis Results: <span className="road-name-highlight">{analysisData.road_name}</span>
            </h2>
            <p>
              {analysisData.city && `${analysisData.city}, `}
              {analysisData.state && `${analysisData.state}, `}
              India • {analysisData.road_type?.toUpperCase()} road •{' '}
              {analysisData.road_length_km} km analyzed
            </p>
          </div>

          <StatsCards data={analysisData} />

          <MapView data={analysisData} />

          {/* CHARTS SECTION — KEY OBJECTIVE */}
          <div className="charts-section">
            <h3 className="section-title">📈 Analytics & Speed Impact Dashboard</h3>

            {/* Row 1: Speed Impact (main chart) */}
            <SpeedImpactChart speedAnalysis={analysisData.speed_analysis} />

            {/* Row 2: Gauge + Severity */}
            <div className="charts-row">
              <SpeedGauge speedAnalysis={analysisData.speed_analysis} />
              <SeverityChart distribution={analysisData.severity_distribution} />
            </div>

            {/* Row 3: Density + Cumulative */}
            <div className="charts-row">
              <DensityChart
                densityData={analysisData.density_along_road}
                avgDensity={analysisData.avg_pothole_density}
              />
              <CumulativeChart cumulativeData={analysisData.cumulative_potholes} />
            </div>

            {/* Row 4: Confidence Histogram */}
            <div className="charts-row">
              <ConfidenceHistogram confidenceScores={analysisData.confidence_scores} />
            </div>
          </div>

          {/* Detailed Segment Table */}
          <SegmentTable segments={analysisData.segments} />

          {/* Download Report */}
          <ReportDownload analysisId={analysisData.id} roadName={analysisData.road_name} />
        </div>
      )}
    </div>
  );
};

export default Dashboard;