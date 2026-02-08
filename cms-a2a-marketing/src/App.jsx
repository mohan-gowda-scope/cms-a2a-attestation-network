import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, Zap, Users, CheckCircle, ArrowRight, Activity, Database, Globe, Lock, Cpu } from 'lucide-react';

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
  return (
    <div className="app">
      {/* Navigation */}
      <nav className="container" style={{ padding: '24px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>A2A <span className="gradient-text">Network</span></h2>
        <div style={{ display: 'flex', gap: '32px', alignItems: 'center' }}>
          <a href="#features" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Features</a>
          <a href="#pricing" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Pricing</a>
          <button className="btn-primary" style={{ padding: '8px 20px' }}>Launch Hub</button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero container">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="badge" style={{ marginBottom: '24px' }}>Now Compliant with W3C VC & FHIR R4</div>
          <h1 style={{ fontSize: '4rem', marginBottom: '24px', lineHeight: 1.1 }}>
            Attestation at the <br />
            <span className="gradient-text">Speed of Trust</span>
          </h1>
          <p style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', maxWidth: '700px', margin: '0 auto 40px' }}>
            The world's first decentralized 10-agent healthcare mesh. Automate prior authorizations, audits, and matching with cryptographic certainty.
          </p>
          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
            <button className="btn-primary">Book a Demo <ArrowRight size={18} style={{ verticalAlign: 'middle', marginLeft: '8px' }} /></button>
            <button className="glass" style={{ padding: '12px 24px', borderRadius: '8px', color: 'white', fontWeight: 600 }}>Whitepaper</button>
          </div>
        </motion.div>

        <motion.div 
          style={{ marginTop: '60px', borderRadius: '24px', overflow: 'hidden', border: '1px solid var(--border-glass)' }}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
        >
          <img src="/hero_healthcare_ai.png" alt="Futuristic Healthcare AI" style={{ width: '100%', maxWidth: '1000px', display: 'block' }} />
        </motion.div>
      </section>

      {/* Features / Agents Section */}
      <section id="features" className="container">
        <div style={{ textAlign: 'center', marginBottom: '60px' }}>
          <h2 style={{ fontSize: '2.5rem', marginBottom: '16px' }}>The 10-Agent Ecosystem</h2>
          <p style={{ color: 'var(--text-secondary)' }}>A specialized swarm of AI agents working in perfect harmony.</p>
        </div>
        
        <div className="card-grid">
          {agents.map((agent, i) => (
            <motion.div 
              key={i} 
              className="glass agent-card"
              whileHover={{ borderColor: 'var(--accent-cyan)' }}
            >
              <div style={{ color: 'var(--accent-cyan)', marginBottom: '16px' }}>{agent.icon}</div>
              <h3 style={{ marginBottom: '12px' }}>{agent.name}</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{agent.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="container" style={{ background: 'radial-gradient(circle at 0% 100%, rgba(0, 242, 255, 0.05) 0%, transparent 40%)' }}>
        <div style={{ textAlign: 'center', marginBottom: '60px' }}>
          <h2 style={{ fontSize: '2.5rem', marginBottom: '16px' }}>Scalable Trust Pricing</h2>
          <p style={{ color: 'var(--text-secondary)' }}>From clinics to national healthcare networks.</p>
        </div>

        <div className="card-grid">
          {plans.map((plan, i) => (
            <div key={i} className={`glass agent-card ${plan.popular ? 'popular' : ''}`} style={{ 
              position: 'relative', 
              border: plan.popular ? '2px solid var(--accent-cyan)' : '1px solid var(--border-glass)' 
            }}>
              {plan.popular && <div className="badge" style={{ position: 'absolute', top: '-12px', left: '50%', transform: 'translateX(-50%)' }}>Most Popular</div>}
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

      {/* Footer */}
      <footer className="container" style={{ padding: '60px 0', borderTop: '1px solid var(--border-glass)', marginTop: '80px', textAlign: 'center' }}>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          © 2026 CMS A2A Network. Built on trust, driven by AI. <br />
          All data encrypted with Ed25519. RFC 7515 compliant.
        </p>
      </footer>
    </div>
  );
}
