import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [isSosActive, setIsSosActive] = useState(false);
  const [backendStatus, setBackendStatus] = useState('Checking...');
  const [coords, setCoords] = useState({ lat: '40.7128', lng: '-74.0060' });
  const [simulating, setSimulating] = useState(false);

  // Check backend server health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/health');
        if (response.ok) {
          const data = await response.json();
          setBackendStatus('Healthy');
        } else {
          setBackendStatus('Offline');
        }
      } catch (err) {
        setBackendStatus('Offline (Unreachable)');
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  // Simulate coordinate changes
  useEffect(() => {
    if (!simulating) return;

    const interval = setInterval(() => {
      setCoords(prev => ({
        lat: (parseFloat(prev.lat) + (Math.random() - 0.5) * 0.002).toFixed(6),
        lng: (parseFloat(prev.lng) + (Math.random() - 0.5) * 0.002).toFixed(6)
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, [simulating]);

  const handleSosTrigger = () => {
    setIsSosActive(!isSosActive);
  };

  return (
    <div className="app-container">
      {/* Navigation Header */}
      <header className="app-header">
        <div className="logo-container">
          <div className="logo-icon">G</div>
          <span className="logo-text">Enterprise CX Guardian AI</span>
        </div>
        <div className="status-badge">
          <div className="status-dot"></div>
          <span>Platform Live</span>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-tagline">Duty of Care Platform</div>
        <h1 className="hero-title">Real-Time Safety & Smart Route Navigation</h1>
        <p className="hero-desc">
          Empowering enterprise teams, remote field agents, and gig workers with active
          location monitoring, threat-mapped routing, and live guardian SOS tracking.
        </p>
      </section>

      {/* Main Dashboard Cards Grid */}
      <main className="dashboard-grid">
        {/* Core Navigator Card */}
        <div className="glass-card">
          <div className="card-icon">📍</div>
          <h2 className="card-title">Live Geolocation</h2>
          <p className="card-desc">
            Monitor precise coords during operations. Simulating routing hazards automatically updates local threat tables.
          </p>
          <div className="stat-list" style={{ marginBottom: '1.5rem' }}>
            <div className="stat-item">
              <span className="stat-label">Latitude</span>
              <span className="stat-value">{coords.lat}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Longitude</span>
              <span className="stat-value">{coords.lng}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Simulation Mode</span>
              <span className="stat-value" style={{ color: simulating ? '#10b981' : '#ef4444' }}>
                {simulating ? 'ACTIVE' : 'STANDBY'}
              </span>
            </div>
          </div>
          <button 
            className="action-button" 
            onClick={() => setSimulating(!simulating)}
          >
            {simulating ? 'Pause Simulator' : 'Start Coordinate Drift'}
          </button>
        </div>

        {/* SOS Panel Card */}
        <div className="glass-card">
          <div className="card-icon">🚨</div>
          <h2 className="card-title">Emergency Control</h2>
          <p className="card-desc">
            Triggering SOS sends instant location snapshots to all designated contacts and alerts backend controllers.
          </p>
          <div className="stat-list" style={{ marginBottom: '1.5rem' }}>
            <div className="stat-item">
              <span className="stat-label">SOS Alarm Status</span>
              <span className="stat-value" style={{ color: isSosActive ? '#ef4444' : '#9ca3af', fontWeight: 'bold' }}>
                {isSosActive ? 'CRITICAL (BROADCASTING)' : 'IDLE'}
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">SMS Alert Log</span>
              <span className="stat-value">{isSosActive ? 'TWILIO QUEUED' : 'EMPTY'}</span>
            </div>
          </div>
          <button 
            className={`sos-button ${isSosActive ? 'active' : ''}`}
            onClick={handleSosTrigger}
          >
            {isSosActive ? 'Cancel Active SOS' : 'Trigger Emergency SOS'}
          </button>
        </div>

        {/* Connection & Services Card */}
        <div className="glass-card">
          <div className="card-icon">🛡️</div>
          <h2 className="card-title">Backend Integrity</h2>
          <p className="card-desc">
            Check local integrations, MongoDB database connectivity, and messaging systems.
          </p>
          <div className="stat-list">
            <div className="stat-item">
              <span className="stat-label">Express Health API</span>
              <span className="stat-value" style={{ color: backendStatus.startsWith('Healthy') ? '#10b981' : '#f59e0b' }}>
                {backendStatus}
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Websocket Gateway</span>
              <span className="stat-value">Standby</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Twilio SMS Broker</span>
              <span className="stat-value">Standby</span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-links">
          <a href="/docs/architecture" className="footer-link">Architecture Docs</a>
          <a href="/docs/pitch" className="footer-link">Product Pitch</a>
          <a href="https://github.com" className="footer-link">Enterprise GitHub</a>
        </div>
        <p>&copy; 2026 Enterprise CX Guardian AI. Scaffolding complete. Ready for implementation changes.</p>
      </footer>
    </div>
  );
}

export default App;
