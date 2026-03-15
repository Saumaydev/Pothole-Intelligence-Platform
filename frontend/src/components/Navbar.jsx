import Switch from "./Switch";
import React from 'react';
import { FaRoad, FaGithub } from 'react-icons/fa';

const Navbar = () => (
  <nav className="navbar">
    <div className="navbar-brand">
      <FaRoad className="navbar-icon" />
      <div>
        <h1>Pothole Intelligence Platform</h1>
        <span className="navbar-subtitle">AI-Powered Road Infrastructure Monitor</span>
      </div>
    </div>
    <div className="navbar-links">
     <span className="version-badge">v2.0</span>

     <Switch />

     <a href="https://github.com/Saumaydev/Pothole-Intelligence-Platform" target="_blank" rel="noreferrer">
     <FaGithub size={22} />
     </a>
    </div>
  </nav>
);

export default Navbar;
