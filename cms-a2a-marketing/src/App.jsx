import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Zap, Users, CheckCircle, ArrowRight, Activity, Cpu, Terminal, Play, Server, Lock } from 'lucide-react';

const agents = [
  { name: "Provider Agent", icon: <Users />, desc: "Initiates clinical attestations directly from the EHR." },
  { name: "Payer Agent", icon: <CheckCircle />, desc: "Automates prior authorization using verified CMS proofs." },
  { name: "CMS Agent", icon: <Shield />, desc: "The root of trust. Signs and issues Verifiable Credentials." },
  { name: "Auditor Agent", icon: <Activity />, desc: "Real-time regulatory oversight and anomaly detection." },
  { name: "Patient Agent", icon: <Lock />, desc: "Puts patients in control of their digital health identity." },
  { name: "Research Agent", icon: <Cpu />, desc: "AI-driven clinical trial matching with 95% confidence." },
];

const plans = [
  { name: "Starter", price: "$499", features: ["Up to 500 attestations", "3 Core Agents", "Standard Support"] },
  { name: "Professional", price: "$1,999", features: ["10,000 attestations", "Full 10-Agent Mesh", "Priority API Access", "Custom Policies"], popular: true },
  { name: "Enterprise", price: "Custom", features: ["Unlimited volume", "Multi-region dedicated", "On-site Compliance Audit", "White-label Portal"] },
];

export default function App() {
  const [provider, setProvider] = useState('AWS');

  const sandboxSteps = [
    { type: 'info', msg: `🚀 Initializing A2A Sandbox [Provider: ${provider}]...` },
    { type: 'info', msg: `💎 Step 1: Verification of Clinical Identity (NPI: 1234567890)...` },
    { type: 'success', msg: `✅ Identity Verified: ACTIVE (did:web:cred-v1-${provider.toLowerCase()})` },
    { type: 'info', msg: "🏥 Step 2: Provider Initiates Attestation Swarm (FHIR R4 Bundle)..." },
    { type: 'info', msg: "🧬 Step 3: Collaborative Agency Review (Lab + Payer + PBM)..." },
    { type: 'success', msg: `✅ Concurrence Token Issued via ${provider} Stack.` },
    { type: 'info', msg: "🏛️ Step 4: CMS Agent Final Audit & Verifiable Credential Issuance..." },
    { type: 'success', msg: "✅ CMS ISSUED VC: urn:uuid:7b42-9901-a2a-4421" },
    { type: 'info', msg: `🔐 Cryptographic Proof: Ed25519Signature2020 verified.` },
    { type: 'success', msg: "🏁 Simulation Complete: 10/10 Agents Synchronized." }
  ];

  const runDemo = async () => {
    setRunning(true);
    setLogs([]);
    for (const step of sandboxSteps) {
      setLogs(prev => [...prev, step]);
      await new Promise(r => setTimeout(r, 600));
    }
    setRunning(false);
  };

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [logs]);

  return (
    <div className="app">
      {/* Navigation */}
      <nav className="container" style={{ padding: '24px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>A2A <span className="gradient-text">Network</span></h2>
        <div style={{ display: 'flex', gap: '32px', alignItems: 'center' }}>
          <a href="#features" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Features</a>
          <a href="#sandbox" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Sandbox</a>
          <a href="#pricing" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Pricing</a>
          <button className="btn-primary" style={{ padding: '8px 20px' }}>Join Network</button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero container">
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
          <div className="badge" style={{ marginBottom: '24px' }}>Now Compliant with W3C VC & FHIR R4</div>
          <h1 style={{ fontSize: '4rem', marginBottom: '24px', lineHeight: 1.1 }}>
            Attestation at the <br />
            <span className="gradient-text">Speed of Trust</span>
          </h1>
          <p style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', maxWidth: '700px', margin: '0 auto 40px' }}>
            The world's first decentralized 10-agent healthcare mesh. Automate prior authorizations, audits, and matching with cryptographic certainty.
          </p>
          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
            <a href="#sandbox" className="btn-primary" style={{ textDecoration: 'none' }}>Launch Sandbox</a>
            <button className="glass" style={{ padding: '12px 24px', borderRadius: '8px', color: 'white', fontWeight: 600 }}>Whitepaper</button>
          </div>
        </motion.div>

        <motion.div 
          style={{ marginTop: '60px', borderRadius: '24px', overflow: 'hidden', border: '1px solid var(--border-glass)' }}
          initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.4 }}
        >
          <img src="/hero_healthcare_ai.png" alt="Futuristic Healthcare AI" style={{ width: '100%', maxWidth: '1000px', display: 'block' }} />
        </motion.div>
      </section>

      {/* Sandbox Section */}
      <section id="sandbox" className="container" style={{ marginTop: '120px' }}>
        <div style={{ background: 'var(--bg-card)', borderRadius: '32px', border: '1px solid var(--border-glass)', padding: '60px', position: 'relative', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', top: 0, right: 0, padding: '40px', opacity: 0.1 }}><Server size={200} /></div>
          
          <div style={{ maxWidth: '600px', marginBottom: '40px' }}>
            <div className="badge" style={{ background: 'rgba(0, 242, 255, 0.1)', color: 'var(--accent-cyan)', marginBottom: '16px' }}>INTERACTIVE SANDBOX</div>
            <h2 style={{ fontSize: '2.5rem', marginBottom: '16px' }}>Experience the Mesh</h2>
            <p style={{ color: 'var(--text-secondary)' }}>Launch an ephemeral instance of the 10-agent network. Watch in real-time as agents collaborate to issue Verifiable Credentials.</p>
          </div>

          <div className="glass" style={{ minHeight: '300px', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.1)', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <div style={{ background: 'rgba(255,255,255,0.05)', padding: '12px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                <Terminal size={16} /> a2a-trust-shell --provider={provider.toLowerCase()}
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                {!running && (
                  <select 
                    value={provider} 
                    onChange={(e) => setProvider(e.target.value)}
                    style={{ background: 'transparent', color: 'white', border: '1px solid rgba(255,255,255,0.2)', borderRadius: '4px', fontSize: '0.8rem', padding: '2px 8px' }}
                  >
                    <option value="AWS">AWS Stack</option>
                    <option value="GCP">GCP Stack</option>
                  </select>
                )}
                {!running && !logs.length && (
                  <button onClick={runDemo} className="btn-primary" style={{ padding: '6px 16px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Play size={14} /> Start Simulation
                  </button>
                )}
              </div>
            </div>
            
            <div ref={scrollRef} style={{ flex: 1, padding: '20px', fontFamily: 'monospace', fontSize: '0.9rem', maxHeight: '300px', overflowY: 'auto' }}>
              {!logs.length && <div style={{ color: '#4b5563' }}>// Click start to initialize the autonomous mesh simulation...</div>}
              {logs.map((log, i) => (
                <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} style={{ marginBottom: '8px', color: log.type === 'success' ? 'var(--accent-cyan)' : 'var(--text-primary)' }}>
                  {log.msg}
                </motion.div>
              ))}
              {running && <motion.div animate={{ opacity: [0, 1] }} transition={{ repeat: Infinity, duration: 0.5 }} style={{ width: '8px', height: '16px', background: 'var(--accent-cyan)', display: 'inline-block' }} />}
            </div>
          </div>
        </div>
      </section>

      {/* ... (Features & Pricing sections remain the same) */}
      <section id="features" className="container" style={{ marginTop: '120px' }}>
        <div style={{ textAlign: 'center', marginBottom: '60px' }}>
          <h2 style={{ fontSize: '2.5rem', marginBottom: '16px' }}>The 10-Agent Ecosystem</h2>
          <p style={{ color: 'var(--text-secondary)' }}>A specialized swarm of AI agents working in perfect harmony.</p>
        </div>
        <div className="card-grid">
          {agents.map((agent, i) => (
            <div key={i} className="glass agent-card">
              <div style={{ color: 'var(--accent-cyan)', marginBottom: '16px' }}>{agent.icon}</div>
              <h3 style={{ marginBottom: '12px' }}>{agent.name}</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{agent.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="pricing" className="container" style={{ paddingBottom: '100px' }}>
        <div style={{ textAlign: 'center', marginBottom: '60px' }}>
          <h2 style={{ fontSize: '2.5rem', marginBottom: '16px' }}>Scalable Trust Pricing</h2>
          <p style={{ color: 'var(--text-secondary)' }}>From clinics to national healthcare networks.</p>
        </div>
        <div className="card-grid">
          {plans.map((plan, i) => (
            <div key={i} className={`glass agent-card ${plan.popular ? 'popular' : ''}`}>
              <h3 style={{ marginBottom: '8px', color: 'var(--text-secondary)' }}>{plan.name}</h3>
              <div style={{ fontSize: '3rem', fontWeight: 800, marginBottom: '24px' }}>{plan.price}<span style={{ fontSize: '1rem', fontWeight: 400 }}>/mo</span></div>
              <ul style={{ listStyle: 'none', marginBottom: '32px' }}>
                {plan.features.map((f, j) => (
                  <li key={j} style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem' }}>
                    <CheckCircle size={16} color="var(--accent-cyan)" /> {f}
                  </li>
                ))}
              </ul>
              <button className={plan.popular ? 'btn-primary' : 'glass'} style={{ width: '100%', padding: '12px' }}>Get Started</button>
            </div>
          ))}
        </div>
      </section>

      <footer className="container" style={{ padding: '60px 0', borderTop: '1px solid var(--border-glass)', textAlign: 'center' }}>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          © 2026 CMS A2A Network. Built on trust, driven by AI. <br />
          All data encrypted with Ed25519. RFC 7515 compliant.
        </p>
      </footer>
    </div>
  );
}
