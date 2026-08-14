import React from 'react';
import { Link } from 'react-router-dom';
import { CheckCircle2 } from 'lucide-react';
import '../../styles/marketing.css';

export const HomePage: React.FC = () => {
  return (
    <div className="landing-theme-wrapper">
      
      {/* Hero Section */}
      <main className="marketing-hero">
        
        {/* Left Column (Content) */}
        <div className="hero-content">
          <div className="hero-badge">
            <div className="icon-dot"><CheckCircle2 size={14} /></div>
            Secure • Scalable • Real-Time
            <span style={{ color: '#9ca3af', margin: '0 0.5rem' }}>—</span>
            <span style={{ fontWeight: 400 }}>A single WMS to standardize operations.</span>
          </div>
          
          <h1 className="hero-title">WAREHOUSE</h1>
          <h2 className="hero-title-accent">Management Systems</h2>
          
          <p className="hero-description">
            Our entry-to-enterprise WMS orchestrates people, processes, robotics, and automation in one scalable system. No phantom stock. Atomic locking enabled.
          </p>

          <div className="hero-actions">
            <Link to="/login" className="btn-contact">TALK TO AN EXPERT</Link>
            <Link to="/login" className="btn-secondary-outline">KEY RESOURCES</Link>
          </div>

          <div className="metrics-section">
            <h3 className="metrics-title">Turn Expertise Into Measurable Impact</h3>
            <div className="metrics-grid">
              
              <div className="metric-card">
                <div className="metric-header">
                  <h4 className="metric-value">1,600+</h4>
                  <span className="metric-label">WMS CUSTOMERS</span>
                </div>
                <p className="metric-desc">Trusted across the Americas, Europe and Asia.</p>
              </div>

              <div className="metric-card">
                <div className="metric-header">
                  <h4 className="metric-value">40+</h4>
                  <span className="metric-label">WWMS EXPERTISE</span>
                </div>
                <p className="metric-desc">Continuous innovation through upgrades and support.</p>
              </div>

            </div>
          </div>
        </div>

        {/* Right Column (Logistics Flow Image) */}
        <div className="hero-scene" style={{ transform: 'translateY(-6rem)' }}>
          <img 
            src="/logistics_flow.jpg" 
            alt="Logistics Flow Diagram" 
            style={{ width: '100%', height: 'auto', display: 'block', borderRadius: '8px', boxShadow: '0 20px 40px rgba(0,0,0,0.08)' }} 
          />
        </div>

      </main>

    </div>
  );
};
