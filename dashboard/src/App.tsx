import React, { useState } from 'react';
import { Shield, Activity, CheckCircle, AlertTriangle, Search, Zap } from 'lucide-react';

const App: React.FC = () => {
  const [stats, setStats] = useState({
    totalAttestations: 1242,
    successRate: 98.4,
    activeAgents: 10,
    lastUpdate: new Date().toLocaleTimeString()
  });

  const [logs, setLogs] = useState([
    { id: '1', provider: 'Mayo Clinic', patient: 'PAT-8822', status: 'Compliant', time: '2m ago' },
    { id: '2', provider: 'Aetna Payer', patient: 'PAT-4412', status: 'Compliant', time: '5m ago' },
    { id: '3', provider: 'CMS Direct', patient: 'PAT-9911', status: 'Flagged', time: '12m ago' },
    { id: '4', provider: 'Stanford Health', patient: 'PAT-2233', status: 'Compliant', time: '15m ago' },
  ]);

  // Phase 6: Real-time Data Streaming Simulation
  React.useEffect(() => {
    const interval = setInterval(() => {
      const newLog = {
        id: Math.floor(Math.random() * 10000).toString(),
        provider: ['Mayo Clinic', 'Aetna Payer', 'Blue Cross', 'Stanford Health', 'PBM Pharma', 'Quest Labs', 'HHS-OIG Auditor', 'NPI Verifier', 'Patient Proxy', 'Pharma Research'][Math.floor(Math.random() * 10)],
        patient: `PAT-${Math.floor(Math.random() * 9000 + 1000)}`,
        status: Math.random() > 0.1 ? 'Compliant' : 'Flagged',
        time: 'just now'
      };
      
      setLogs(prev => [newLog, ...prev.slice(0, 9)]);
      setStats(prev => ({
        ...prev,
        totalAttestations: prev.totalAttestations + 1,
        lastUpdate: new Date().toLocaleTimeString()
      }));
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      <header className="animate-in">
        <div className="logo-container">
          <h1 className="logo-text">
            <Shield color="#3b82f6" size={28} />
            CMS <span className="text-accent">A2A</span> Monitoring Hub
          </h1>
          <p style={{ color: '#9ca3af', fontSize: '0.875rem' }}>Autonomous Attestation Network Status</p>
        </div>
        <div className="header-meta">
          <div className="badge" style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)', color: '#3b82f6' }}>Live Simulation</div>
          <Activity size={20} color="#3b82f6" />
        </div>
      </header>

      <div className="grid">
        <div className="card animate-in" style={{ animationDelay: '0.1s' }}>
          <div className="stat-label">Total Attestations</div>
          <div className="stat-value">{stats.totalAttestations.toLocaleString()}</div>
          <div className="stat-trend positive">
            <Zap size={12} /> +12% from last week
          </div>
        </div>

        <div className="card animate-in" style={{ animationDelay: '0.2s' }}>
          <div className="stat-label">Compliance Rate</div>
          <div className="stat-value">{stats.successRate}%</div>
          <div className="stat-trend info">
            Verified via Ed25519
          </div>
        </div>

        <div className="card animate-in" style={{ animationDelay: '0.3s' }}>
          <div className="stat-label">Active Agents</div>
          <div className="stat-value">{stats.activeAgents}</div>
          <div className="stat-trend muted">
            Multi-Cloud (AWS/GCP)
          </div>
        </div>
      </div>

      <div className="table-container card animate-in" style={{ animationDelay: '0.4s' }}>
        <h2 className="table-header">
          <Search size={20} color="#3b82f6" />
          Recent Attestation Logs
        </h2>
        <table>
          <thead>
            <tr>
              <th>Request ID</th>
              <th>Provider / Payer</th>
              <th>Patient ID</th>
              <th>Status</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td className="id-cell">{log.id.padStart(4, '0')}</td>
                <td className="provider-cell">{log.provider}</td>
                <td>{log.patient}</td>
                <td className={log.status === 'Compliant' ? 'status-compliant' : 'status-flagged'}>
                  <div className="status-cell">
                    {log.status === 'Compliant' ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
                    {log.status}
                  </div>
                </td>
                <td style={{ color: '#9ca3af' }}>{log.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <footer className="app-footer">
        &copy; 2026 CMS A2A Innovation Lab. All Attestations are Cryptographically Signed.
        <div style={{ marginTop: '0.5rem', opacity: 0.5 }}>
          Infrastructure Optimized: ARM64 / Graviton enabled for maximum efficiency.
        </div>
      </footer>
    </div>
  );
};

export default App;
