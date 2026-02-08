import React, { useState, useEffect } from 'react';
import { Shield, Activity, CheckCircle, AlertTriangle, Search, Zap, Cpu } from 'lucide-react';
import './App.css';

const agentNames = [
  "Provider Agent", "Clearinghouse", "CMS Agent", "Payer Agent",
  "PBM Agent", "Lab Agent", "Auditor Agent", "Credentialing",
  "Patient Proxy", "Research Agent"
];

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
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      const newLog = {
        id: Math.floor(Math.random() * 10000).toString(),
        provider: agentNames[Math.floor(Math.random() * agentNames.length)],
        patient: `PAT-${Math.floor(Math.random() * 9000 + 1000)}`,
        status: Math.random() > 0.1 ? 'Compliant' : 'Flagged',
        time: 'just now'
      };
      
      setLogs(prev => [newLog, ...prev.slice(0, 7)]);
      setStats(prev => ({
        ...prev,
        totalAttestations: prev.totalAttestations + 1,
        lastUpdate: new Date().toLocaleTimeString()
      }));
    }, 4000);
    
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
          <p className="stat-label">Autonomous Attestation Network Status</p>
        </div>
        <div className="header-meta-group">
          <div className="badge">LIVE_ECOSYSTEM</div>
          <Activity size={20} color="#3b82f6" />
        </div>
      </header>

      <div className="grid">
        <div className="card animate-in" style={{ animationDelay: '0.1s' }}>
          <div className="stat-label">Total Attestations</div>
          <div className="stat-value">{stats.totalAttestations.toLocaleString()}</div>
          <div className="stat-trend positive"><Zap size={12} /> +12% Efficiency</div>
        </div>
        <div className="card animate-in" style={{ animationDelay: '0.2s' }}>
          <div className="stat-label">Compliance Rate</div>
          <div className="stat-value">{stats.successRate}%</div>
          <div className="stat-trend info">W3C VC Verified</div>
        </div>
        <div className="card animate-in" style={{ animationDelay: '0.3s' }}>
          <div className="stat-label">Network Load</div>
          <div className="stat-value">Low</div>
          <div className="stat-trend muted">10 Active Swarms</div>
        </div>
      </div>

      <h3 className="section-title">Ecosystem Swarm Status</h3>
      <div className="orchestration-grid">
        {agentNames.map((name, i) => (
          <div key={i} className="card agent-mini-card glass animate-in" style={{ animationDelay: `${0.1 * i}s` }}>
            <Cpu size={20} color="var(--accent-blue)" style={{ marginBottom: '8px' }} />
            <div className="agent-name">{name}</div>
            <div className="status-row">
              <span className="status-dot active"></span>
              Healthy
            </div>
          </div>
        ))}
      </div>

      <div className="table-container card animate-in" style={{ animationDelay: '0.5s' }}>
        <h2 className="logo-text table-header">
          <Search size={20} color="#3b82f6" />
          Real-time Audit Ledger
        </h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Originating Agent</th>
              <th>Subject</th>
              <th>Trust Status</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td className="id-cell">#{log.id}</td>
                <td>{log.provider}</td>
                <td>{log.patient}</td>
                <td className={log.status === 'Compliant' ? 'status-compliant' : 'status-flagged'}>
                  <div className="status-flex">
                    <CheckCircle size={14} /> {log.status}
                  </div>
                </td>
                <td className="time-cell">{log.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <footer className="app-footer">
        &copy; 2026 CMS A2A Innovation Lab. All Attestations are Cryptographically Signed.
        <div className="footer-meta">
          Infrastructure Optimized: ARM64 / Graviton enabled for maximum efficiency.
        </div>
      </footer>
    </div>
  );
};

export default App;
