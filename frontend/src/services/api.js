import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 300000, // 5 min for long analyses
  headers: { 'Content-Type': 'application/json' },
});

export const startAnalysis = async (data) => {
  const response = await api.post('/analysis/start', data);
  return response.data;
};

export const getProgress = async (analysisId) => {
  const response = await api.get(`/analysis/progress/${analysisId}`);
  return response.data;
};

export const getResult = async (analysisId) => {
  const response = await api.get(`/analysis/result/${analysisId}`);
  return response.data;
};

export const getHistory = async (limit = 20) => {
  const response = await api.get(`/analysis/history?limit=${limit}`);
  return response.data;
};

export const downloadReport = (analysisId) => {
  return `${API_BASE}/reports/download/${analysisId}`;
};

export const downloadCSV = (analysisId) => {
  return `${API_BASE}/reports/download-csv/${analysisId}`;
};

export default api;