import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { Layers } from 'lucide-react';
import '../styles/tokens.css';
import '../styles/marketing.css';

export const MarketingLayout: React.FC = () => {
  return (
    <div className="landing-theme-wrapper">
      {/* Top Navbar */}
      <nav className="marketing-header">
        <Link to="/" className="marketing-brand">
          <div className="icon-container">
            <Layers size={28} />
          </div>
          <div>
            WHITFIELD
            <span className="marketing-brand-sub">WAREHOUSE EXECUTION</span>
          </div>
        </Link>
        
        <div className="marketing-nav-links">
          <Link to="/">/ About Us</Link>
          <Link to="/">/ Your Challenges</Link>
          <Link to="/">/ Your Solutions</Link>
          <Link to="/">/ Knowledge Center</Link>
          <Link to="/">/ Intelligent Execution</Link>
        </div>

        <div>
          <Link to="/login" className="btn-contact">
            Login
          </Link>
        </div>
      </nav>

      <Outlet />
    </div>
  );
};
