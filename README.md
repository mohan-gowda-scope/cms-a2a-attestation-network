# CMS A2A Attestation Network

A production-grade, multi-cloud (AWS/GCP) agentic framework for autonomous healthcare attestation and prior-authorization validation.

## 📖 Detailed Documentation

- **[Project Overview](docs/OVERVIEW.md)**: Mission, components, and multi-cloud strategy.
- **[Architecture & Design](docs/ARCHITECTURE.md)**: Technical data flow, security model, and trust registry.
- **[API Reference](docs/API_REFERENCE.md)**: JSON-RPC methods and data formats.
- **[Setup & Testing](docs/SETUP.md)**: Local installation and cloud deployment guide.

## 🚀 Quick Start (Simulation)

To see the autonomous network in action locally:

```bash
pip install -r gcp_functions/requirements.txt
export PYTHONPATH=$PYTHONPATH:.
python3 scripts/e2e_orchestrator.py
```

## 🔐 Security Features

- **W3C Verifiable Credentials**: Standardized attestation formats.
- **Ed25519 Cryptography**: Real digital signatures for non-repudiation and integrity.
- **Trust Registry**: Decentralized identity (DID) resolution for automated verification.
- **Multi-Cloud Handshake**: Secure AWS-GCP cross-cloud verification.

## 🛠 Tech Stack

- **GCP**: Cloud Functions, Firestore, Vertex AI (Gemini 1.5 Flash).
- **AWS**: Lambda, DynamoDB, S3, Bedrock (Claude 3.5 Sonnet).
- **Security**: Ed25519 (Cryptography), JSON-RPC 2.0.
- **IaC**: Terraform (HCL).

---

_Developed for CMS A2A Innovation_
