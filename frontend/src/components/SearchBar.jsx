import React, { useState } from 'react';
import { FaSearch, FaMapMarkerAlt, FaRoad } from 'react-icons/fa';

const SearchBar = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    road_name: '',
    city: '',
    state: '',
    road_type: 'urban',
    sampling_distance: 50,
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.road_name.trim()) onSubmit(formData);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const examples = [
    { road: 'MG Road', city: 'Bangalore', state: 'Karnataka' },
    { road: 'Marine Drive', city: 'Mumbai', state: 'Maharashtra' },
    { road: 'Anna Salai', city: 'Chennai', state: 'Tamil Nadu' },
    { road: 'Outer Ring Road', city: 'Hyderabad', state: 'Telangana' },
  ];

  return (
    <div className="search-section">
      <div className="search-header">
        <h2><FaRoad /> Analyze a Road</h2>
        <p>Enter any road name in India to detect potholes and predict speed impact</p>
      </div>

      <form onSubmit={handleSubmit} className="search-form">
        <div className="form-row">
          <div className="form-group form-group-large">
            <label><FaRoad /> Road Name *</label>
            <input
              type="text"
              name="road_name"
              value={formData.road_name}
              onChange={handleChange}
              placeholder="e.g., MG Road, NH44, Outer Ring Road..."
              required
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label><FaMapMarkerAlt /> City</label>
            <input
              type="text"
              name="city"
              value={formData.city}
              onChange={handleChange}
              placeholder="e.g., Bangalore"
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label>State</label>
            <input
              type="text"
              name="state"
              value={formData.state}
              onChange={handleChange}
              placeholder="e.g., Karnataka"
              disabled={loading}
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Road Type</label>
            <select name="road_type" value={formData.road_type} onChange={handleChange} disabled={loading}>
              <option value="highway">Highway (80 km/h base)</option>
              <option value="urban">Urban (50 km/h base)</option>
              <option value="rural">Rural (60 km/h base)</option>
              <option value="residential">Residential (30 km/h base)</option>
            </select>
          </div>
          <div className="form-group">
            <label>Sampling Distance (m)</label>
            <select
              name="sampling_distance"
              value={formData.sampling_distance}
              onChange={handleChange}
              disabled={loading}
            >
              <option value={25}>25m (High Detail)</option>
              <option value={50}>50m (Standard)</option>
              <option value={100}>100m (Fast)</option>
            </select>
          </div>
          <div className="form-group">
            <button type="submit" className="btn-analyze" disabled={loading}>
              {loading ? (
                <><span className="spinner" /> Analyzing...</>
              ) : (
                <><FaSearch /> Start Analysis</>
              )}
            </button>
          </div>
        </div>
      </form>

      <div className="quick-examples">
        <span>Quick examples:</span>
        {examples.map((ex, i) => (
          <button
            key={i}
            className="example-btn"
            disabled={loading}
            onClick={() =>
              setFormData({
                ...formData,
                road_name: ex.road,
                city: ex.city,
                state: ex.state,
              })
            }
          >
            {ex.road}, {ex.city}
          </button>
        ))}
      </div>
    </div>
  );
};

export default SearchBar;