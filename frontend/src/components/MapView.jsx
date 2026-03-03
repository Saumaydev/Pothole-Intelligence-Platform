import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Polyline, CircleMarker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Heatmap component using leaflet.heat
const HeatmapLayer = ({ points }) => {
  const map = useMap();

  useEffect(() => {
    if (!points || points.length === 0) return;

    import('leaflet.heat').then((L) => {
      const heatData = points.map((p) => [p.lat, p.lng, p.intensity]);
      const heat = window.L.heatLayer(heatData, {
        radius: 25,
        blur: 20,
        maxZoom: 17,
        max: 1.0,
        gradient: {
          0.2: '#00ff00',
          0.4: '#ffff00',
          0.6: '#ffa500',
          0.8: '#ff4500',
          1.0: '#ff0000',
        },
      }).addTo(map);

      return () => map.removeLayer(heat);
    });
  }, [map, points]);

  return null;
};

const FitBounds = ({ polyline }) => {
  const map = useMap();
  useEffect(() => {
    if (polyline && polyline.length > 1) {
      map.fitBounds(polyline, { padding: [50, 50] });
    }
  }, [map, polyline]);
  return null;
};

const MapView = ({ data }) => {
  if (!data) return null;

  const center = [data.center_lat, data.center_lng];
  const polyline = data.road_polyline || [];
  const detections = data.detections || [];
  const heatmap = data.heatmap_data || [];

  const severityColors = {
    low: '#4caf50',
    medium: '#ff9800',
    high: '#f44336',
    critical: '#b71c1c',
  };

  return (
    <div className="map-section">
      <h3 className="section-title">🗺️ Interactive Pothole Map</h3>
      <div className="map-container">
        <MapContainer center={center} zoom={14} style={{ height: '550px', width: '100%', borderRadius: '12px' }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; OpenStreetMap contributors'
          />

          {polyline.length > 1 && (
            <>
              <Polyline positions={polyline} color="#1a73e8" weight={4} opacity={0.8} />
              <FitBounds polyline={polyline} />
            </>
          )}

          <HeatmapLayer points={heatmap} />

          {detections.map((det, i) => (
            <CircleMarker
              key={i}
              center={[det.latitude, det.longitude]}
              radius={7}
              fillColor={severityColors[det.severity] || '#ff9800'}
              color="#fff"
              weight={2}
              fillOpacity={0.9}
            >
              <Popup>
                <div style={{ fontSize: '13px' }}>
                  <strong>🕳️ Pothole Detected</strong><br />
                  <b>Severity:</b> {det.severity?.toUpperCase()}<br />
                  <b>Confidence:</b> {(det.confidence * 100).toFixed(1)}%<br />
                  <b>GPS:</b> {det.latitude.toFixed(5)}, {det.longitude.toFixed(5)}<br />
                  <b>Distance:</b> {det.distance_along_road?.toFixed(0)}m from start
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>

        <div className="map-legend">
          <span className="legend-title">Severity:</span>
          {Object.entries(severityColors).map(([key, color]) => (
            <span key={key} className="legend-item">
              <span className="legend-dot" style={{ backgroundColor: color }} />
              {key.charAt(0).toUpperCase() + key.slice(1)}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MapView;